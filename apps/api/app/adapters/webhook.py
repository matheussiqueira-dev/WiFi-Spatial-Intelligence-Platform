"""Signed HTTP POST to the single configured local receiver. No proxies, no redirects.

The receiver verifies ``X-Spatial-Signature: sha256=<hex>`` computed as
HMAC-SHA256(secret, f"{X-Spatial-Timestamp}.{raw body}") and should reject stale
timestamps. Neither the secret nor the body is ever logged.
"""

import hashlib
import hmac
import socket
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

TIMEOUT_SECONDS = 3


class RefuseRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "redirect refused", headers, fp)


OPENER = build_opener(ProxyHandler({}), RefuseRedirect())


@dataclass(frozen=True)
class DeliveryResult:
    delivered: bool
    http_status: int | None
    error: str | None


def signature(secret: str, timestamp: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256)
    return "sha256=" + digest.hexdigest()


def post(url: str, secret: str, body: bytes) -> DeliveryResult:
    timestamp = str(int(time.time()))
    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "wifi-spatial-alerts/1",
            "X-Spatial-Timestamp": timestamp,
            "X-Spatial-Signature": signature(secret, timestamp, body),
        },
    )
    try:
        with OPENER.open(request, timeout=TIMEOUT_SECONDS) as response:
            return DeliveryResult(200 <= response.status < 300, response.status, None)
    except HTTPError as error:
        code = "redirect_refused" if 300 <= error.code < 400 else "http_error"
        return DeliveryResult(False, error.code, code)
    except (TimeoutError, socket.timeout):
        return DeliveryResult(False, None, "timeout")
    except (URLError, OSError):
        # The exception text may echo the URL; only a fixed code leaves this function.
        return DeliveryResult(False, None, "connection_failed")
