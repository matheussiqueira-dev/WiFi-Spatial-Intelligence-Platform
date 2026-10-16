"""Read the current Windows link only. No scan, profiles, SSID, BSSID or traffic export."""

import ipaddress
import json
import re
import subprocess
import sys
import unicodedata
from base64 import b64encode


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
    readings = []
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
