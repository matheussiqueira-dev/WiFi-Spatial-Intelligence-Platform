"""Read the current Windows link and, opt-in, per-channel aggregates of visible networks.

No profiles, SSID, BSSID or traffic export."""

import ipaddress
import json
import re
import subprocess
import sys
import unicodedata
from base64 import b64encode
from typing import Any


def normalized(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value.lower())
        if not unicodedata.combining(char)
    ).strip()


def unavailable(code: str) -> dict:
    return {"link_state": "UNAVAILABLE", "collector_error": code}


def parse_interfaces(text: str) -> dict:
    blocks = re.split(r"(?im)^\s*(?:name|nome)\s*:", text)
    readings: list[dict[str, Any]] = []
    for block in blocks:
        values = {
            normalized(key): value.strip()
            for key, value in re.findall(r"(?m)^\s*([^:\n]+):\s*([^\r\n]*)", block)
        }
        state = values.get("estado", values.get("state", "")).lower()
        if state not in {"connected", "conectado", "disconnected", "desconectado"}:
            continue
        if state in {"disconnected", "desconectado"}:
            readings.append({"link_state": "DISCONNECTED"})
            continue

        def number(keys: tuple[str, ...], upper: float) -> float | None:
            value = next((values[key] for key in keys if key in values), "")
            if not re.fullmatch(r"\d+(?:[.,]\d+)?%?", value):
                return None
            result = float(value.rstrip("%").replace(",", "."))
            return result if 0 <= result <= upper else None

        radio = values.get("tipo de radio", values.get("radio type"))
        readings.append(
            {
                "link_state": "CONNECTED",
                "signal_percent": number(("sinal", "signal"), 100),
                "channel": number(("canal", "channel"), 233),
                "radio_type": radio
                if radio
                in {"802.11a", "802.11b", "802.11g", "802.11n", "802.11ac", "802.11ax", "802.11be"}
                else None,
                "rx_mbps": number(("taxa de recepcao (mbps)", "receive rate (mbps)"), 100000),
                "tx_mbps": number(("taxa de transmissao (mbps)", "transmit rate (mbps)"), 100000),
            }
        )
    active = [reading for reading in readings if reading["link_state"] == "CONNECTED"]
    if len(active) > 1:
        return unavailable("multiple_adapters")
    result = active[0] if active else readings[0] if readings else unavailable("unsupported_output")
    for key in ("signal_percent", "channel"):
        value = result.get(key)
        if value is not None:
            result[key] = (
                int(value) if value.is_integer() and (key != "channel" or value > 0) else None
            )
    return result


def read_link() -> dict:
    if sys.platform != "win32":
        return unavailable("read_failed")
    try:
        completed = subprocess.run(
            ["netsh.exe", "wlan", "show", "interfaces"],
            capture_output=True,
            timeout=8,
        )
        if completed.returncode:
            return unavailable("read_failed")
        try:
            text = completed.stdout[:65536].decode("utf-8-sig")
        except UnicodeDecodeError:
            text = completed.stdout[:65536].decode("oem", errors="replace")
        return parse_interfaces(text)
    except (OSError, subprocess.TimeoutExpired):
        return unavailable("read_failed")


def private_gateway(value: str) -> bool:
    try:
        address = ipaddress.IPv4Address(value)
        return any(
            address in ipaddress.IPv4Network(network)
            for network in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16")
        )
    except ValueError:
        return False


def powershell_json(script: str, timeout: int = 8):
    encoded = b64encode(script.encode("utf-16-le")).decode("ascii")
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        capture_output=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise ValueError("local command unavailable")
    return json.loads(result.stdout.lstrip("\ufeff"))


def probe_gateway() -> dict:
    """Three ICMP requests to the one private default gateway of the Wi-Fi interface."""
    failed = {"probe_status": "UNAVAILABLE", "probe_sent": 0, "probe_rtt_ms": []}
    if sys.platform != "win32":
        return failed
    try:
        gateway = powershell_json(
            "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); "
            "$g=@(Get-NetIPConfiguration | Where-Object { "
            "$_.NetAdapter.InterfaceType -eq 71 -and $_.IPv4DefaultGateway } "
            "| ForEach-Object { $_.IPv4DefaultGateway.NextHop }); "
            "ConvertTo-Json -InputObject $g -Compress"
        )
        if not isinstance(gateway, list) or len(gateway) != 1 or not private_gateway(gateway[0]):
            return failed
        # Only a canonical private IPv4 literal enters this command, never user input.
        target = str(ipaddress.IPv4Address(gateway[0]))
        replies = powershell_json(
            "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); "
            "$p=[Net.NetworkInformation.Ping]::new(); "
            "try { $r=@(1..3 | ForEach-Object { $v=$p.Send('"
            + target
            + "',1000); if($v.Status -eq 'Success'){ [double]$v.RoundtripTime } }); "
            "ConvertTo-Json -InputObject $r -Compress } finally { $p.Dispose() }"
        )
        if not isinstance(replies, list) or not all(
            isinstance(value, int | float) and 0 <= value <= 10000 for value in replies
        ):
            return failed
        return {"probe_status": "COMPLETED", "probe_sent": 3, "probe_rtt_ms": replies}
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return failed


def parse_networks(text: str) -> list[dict] | None:
    """Per-BSSID band/channel/signal/load from `netsh wlan show networks mode=bssid`.

    SSID, BSSID, authentication and rates are never returned: only radio aggregates.
    Returns None when the output is not recognised.
    """
    if not re.search(r"(?im)^\s*ssid\s+\d+\s*:", text):
        return [] if re.search(r"(?im)\b0\b.*(?:redes|networks)", text) else None
    readings = []
    for block in re.split(r"(?im)^\s*bssid\s+\d+\s*:[^\r\n]*", text)[1:]:
        block = re.split(r"(?im)^\s*ssid\s+\d+\s*:", block)[0]
        values = {
            normalized(key): value.strip()
            for key, value in re.findall(r"(?m)^\s*([^:\n]+):\s*([^\r\n]*)", block)
        }
        signal = re.fullmatch(r"(\d{1,3})\s*%", values.get("sinal", values.get("signal", "")))
        channel = re.fullmatch(r"\d{1,3}", values.get("canal", values.get("channel", "")))
        if not signal or not channel or not 0 <= int(signal[1]) <= 100:
            continue
        number = int(channel[0])
        band_text = values.get("banda", values.get("band", "")).replace(",", ".")
        band = (
            "2.4GHz"
            if band_text.startswith("2.4")
            else "5GHz"
            if band_text.startswith("5")
            else "6GHz"
            if band_text.startswith("6")
            else "2.4GHz"
            if number <= 14
            else "5GHz"
        )
        load = re.search(
            r"\((\d{1,3})\s*%\)",
            values.get("utilizacao do canal", values.get("channel utilization", "")),
        )
        if not 1 <= number <= 233:
            continue
        readings.append(
            {
                "band": band,
                "channel": number,
                "signal_percent": int(signal[1]),
                "utilization_percent": int(load[1]) if load and int(load[1]) <= 100 else None,
            }
        )
    return readings


def read_channel_survey() -> dict:
    """Passive: reads the list Windows already scanned; does not trigger a scan or connect."""
    from app.application.channel_plan import aggregate

    if sys.platform != "win32":
        return {"collector_error": "read_failed"}
    try:
        completed = subprocess.run(
            ["netsh.exe", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            timeout=8,
        )
        if completed.returncode:
            return {"collector_error": "read_failed"}
        try:
            text = completed.stdout[:262144].decode("utf-8-sig")
        except UnicodeDecodeError:
            text = completed.stdout[:262144].decode("oem", errors="replace")
    except (OSError, subprocess.TimeoutExpired):
        return {"collector_error": "read_failed"}
    readings = parse_networks(text)
    if readings is None:
        return {"collector_error": "unsupported_output"}
    return {"channels": aggregate(readings)}
