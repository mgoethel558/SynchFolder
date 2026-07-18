"""Höflicher HTTP-Client für die Scraper (NF-02).

Kapselt httpx mit:
* konfigurierbarem Rate-Limiting (Mindestpause je Host),
* ``robots.txt``-Prüfung (optional abschaltbar),
* Retries mit exponentiellem Backoff (tenacity),
* Timeout und sinnvollem User-Agent.

Keine parallelen Massenanfragen — der Client serialisiert Requests je Host.
"""

from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlparse

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import HttpConfig
from .logging_setup import get_logger

log = get_logger(__name__)


class PoliteClient:
    """Serieller, höflicher HTTP-GET-Client."""

    def __init__(self, http: HttpConfig) -> None:
        self.http = http
        self._last_request_at: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._client = httpx.Client(
            headers={"User-Agent": http.user_agent},
            timeout=http.timeout_seconds,
            follow_redirects=True,
        )

    # -- Kontextmanager -----------------------------------------------------
    def __enter__(self) -> "PoliteClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # -- robots.txt ---------------------------------------------------------
    def _allowed(self, url: str) -> bool:
        if not self.http.respect_robots_txt:
            return True
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        rp = self._robots.get(host)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{host}/robots.txt")
            try:
                rp.read()
            except Exception as exc:  # noqa: BLE001
                log.warning("robots.txt für %s nicht lesbar (%s) — erlaube vorsichtig", host, exc)
                rp = None
            self._robots[host] = rp
        if rp is None:
            return True
        return rp.can_fetch(self.http.user_agent, url)

    # -- Rate-Limiting ------------------------------------------------------
    def _throttle(self, url: str) -> None:
        host = urlparse(url).netloc
        last = self._last_request_at.get(host)
        if last is not None:
            elapsed = time.monotonic() - last
            wait = self.http.min_delay_seconds - elapsed
            if wait > 0:
                time.sleep(wait)
        self._last_request_at[host] = time.monotonic()

    # -- öffentlicher GET ---------------------------------------------------
    def get(self, url: str) -> str | None:
        """Holt eine URL höflich. Gibt den Body-Text zurück oder ``None``,
        wenn robots.txt es verbietet."""
        if not self._allowed(url):
            log.warning("robots.txt verbietet %s — übersprungen", url)
            return None
        self._throttle(url)
        return self._get_with_retry(url)

    def _get_with_retry(self, url: str) -> str:
        @retry(
            retry=retry_if_exception_type(
                (httpx.TransportError, httpx.HTTPStatusError)
            ),
            stop=stop_after_attempt(self.http.max_retries),
            wait=wait_exponential(multiplier=self.http.backoff_base_seconds),
            reraise=True,
        )
        def _do() -> str:
            log.debug("GET %s", url)
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp.text

        return _do()
