from typing import Sequence
from urllib.parse import urlparse
import requests

from looker_metadata_extractor.nav.context_injector import ContextInjector
from looker_metadata_extractor.utils.logger import logger


class FlareSolverrInjector(ContextInjector):
    """
    Solves a Cloudflare challenge using an existing FlareSolverr instance and injects the cookies into the browser context
    """

    def __init__(self, **kwargs):
        flaresolverr_url = kwargs.get("flaresolverr_url")
        cloudflare_challenge_url = kwargs.get("cloudflare_challenge_url")
        
        if not isinstance(flaresolverr_url, str):
            raise ValueError("Missing or invalid required argument `flaresolverr_url`")
        if not isinstance(cloudflare_challenge_url, str):
            raise ValueError("Missing or invalid required argument `cloudflare_challenge_url`")
        
        self.flaresolverr_url = flaresolverr_url
        self.cloudflare_challenge_url = cloudflare_challenge_url
        self._user_agent = None
        self._max_wait_time_ms = 60000

    @property
    def user_agent_priority(self) -> int:
        return 100
    @property
    def user_agent(self) -> str | None:
        if self._user_agent:
            return self._user_agent
        logger.info("Fetching User-Agent from FlareSolverr...")
        payload = {"cmd": "request.get", "url": "http://www.google.com", "maxTimeout": self._max_wait_time_ms}
        res = requests.post(self.flaresolverr_url, json=payload).json()
        solution = res.get("solution", {})
        self._user_agent = solution.get("userAgent")
        logger.info(f"Obtained User-Agent from FlareSolverr: {self._user_agent}")
        return self._user_agent

    def inject(self, context):
        logger.info("Starting FlareSolverr injection to solve Cloudflare challenge...")
        payload = {
            "cmd": "request.get",
            "url": self.cloudflare_challenge_url,
            "maxTimeout": self._max_wait_time_ms
        }
        timeout_seconds = int(self._max_wait_time_ms / 1000)
        
        logger.info(f"Waiting for Cloudflare challenge solution for {self.cloudflare_challenge_url}...")
        response = requests.post(self.flaresolverr_url, json=payload, timeout=timeout_seconds)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"FlareSolverr returned non-ok status: {data}")
        if "solution" not in data:
            raise RuntimeError(f"FlareSolverr response missing 'solution': {data}")
        solution = data["solution"]
        
        logger.info("FlareSolverr solution obtained - extracting cookies...")
        solved_cookies = FlareSolverrInjector._extract_cf_cookies_for_host(solution.get("cookies", []), self.cloudflare_challenge_url)
        if not solved_cookies:
            raise RuntimeError("No Cloudflare clearance cookies returned by FlareSolverr")
        logger.info(f"FlareSolverr cookies converted to Playwright format: {solved_cookies}")
        context.add_cookies(solved_cookies)
        logger.info("Successfully injected cookies from FlareSolverr into browser context")

    @staticmethod
    def _extract_cf_cookies_for_host(flaresolverr_cookies: list[dict], url: str) -> Sequence:
        host = (urlparse(url).hostname or "").lower()
        out = []

        for c in flaresolverr_cookies:
            if "name" not in c or "value" not in c or "domain" not in c:
                continue
            name = (c.get("name") or "")
            if name not in ("cf_clearance", "__cf_bm", "_cfuvid"):
                continue

            domain = (c.get("domain") or "").lstrip(".").lower()
            if not domain:
                continue

            if not (host == domain or host.endswith("." + domain)):
                continue

            logger.info(f"Extracting Cloudflare cookie '{name}' for domain '{domain}' matching host '{host}'")
            logger.info(f"Full cookie data: {c}")

            pw = {
                "name": name,
                "value": c.get("value"),
                "url": f"{urlparse(url).scheme}://{host}",
            }

            expires = c.get("expiry") or c.get("expires")
            logger.info(f"Cookie {name} has expires value: {expires}")
            if isinstance(expires, (int, float)) and expires > 0:
                pw["expires"] = int(expires)

            if isinstance(c.get("secure"), bool):
                pw["secure"] = c["secure"]
            if isinstance(c.get("httpOnly"), bool):
                pw["httpOnly"] = c["httpOnly"]
            if c.get("sameSite") in ("Lax", "Strict", "None"):
                pw["sameSite"] = c["sameSite"]

            out.append(pw)

        return out
