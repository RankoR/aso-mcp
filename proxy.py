import logging
import os
import random
from typing import Optional, Dict, List, Set

logger = logging.getLogger(__name__)

# Environment variable name for proxy configuration
PROXY_ENV_VAR = "ASO_MCP_PROXIES"


class ProxyManager:
    """
    Manages a pool of proxies with rotation and retry support.

    Proxies are loaded from the ASO_MCP_PROXIES environment variable.
    Format: comma-separated list of proxy URLs
    Example: "http://host1:port1,http://host2:port2,http://user:pass@host3:port3"
    """

    def __init__(self):
        self._proxies: List[str] = []
        self._failed_proxies: Set[str] = set()
        self._load_proxies()

    def _load_proxies(self) -> None:
        """Load proxies from environment variable."""
        proxy_env = os.environ.get(PROXY_ENV_VAR, "").strip()

        if not proxy_env:
            logger.debug(f"No proxies configured ({PROXY_ENV_VAR} not set)")
            return

        self._proxies = [p.strip() for p in proxy_env.split(",") if p.strip()]
        logger.info(f"Loaded {len(self._proxies)} proxies from {PROXY_ENV_VAR}")

    @property
    def has_proxies(self) -> bool:
        """Check if any proxies are available."""
        return len(self._proxies) > 0

    @property
    def available_proxies(self) -> List[str]:
        """Get list of proxies that haven't failed recently."""
        return [p for p in self._proxies if p not in self._failed_proxies]

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get a random proxy from the pool.
        Returns None if no proxies are configured or all have failed.
        """
        if not self.has_proxies:
            return None

        available = self.available_proxies

        # If all proxies have failed, reset and try again
        if not available:
            logger.warning("All proxies failed, resetting failed list")
            self._failed_proxies.clear()
            available = self._proxies

        proxy_url = random.choice(available)
        return {"https": proxy_url}

    def mark_failed(self, proxy: Optional[Dict[str, str]]) -> None:
        """Mark a proxy as failed."""
        if proxy and "https" in proxy:
            proxy_url = proxy["https"]
            self._failed_proxies.add(proxy_url)
            logger.debug(f"Marked proxy as failed: {self._mask_proxy(proxy_url)}")

    def reset_failed(self) -> None:
        """Reset the list of failed proxies."""
        self._failed_proxies.clear()
        logger.debug("Reset failed proxies list")

    @staticmethod
    def _mask_proxy(proxy_url: str) -> str:
        """Mask credentials in proxy URL for logging."""
        if "@" in proxy_url:
            # Has credentials - mask them
            parts = proxy_url.split("@")
            return f"***@{parts[-1]}"
        return proxy_url


# Global proxy manager instance
proxy_manager = ProxyManager()
