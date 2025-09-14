# neuro_core/neuropacks/health/protocheck/core/adapters/azzem_ccam.py

from __future__ import annotations

import logging
from typing import Optional, Dict

from neuro_core.neuropacks.health.protocheck.core.logger import get_logger

LOGGER = get_logger(__name__)


class AzzemCcamAdapter:
    """
    Graceful stub for Azzem's CCAM DB.
    Real implementation will wire an actual connection/driver.
    This stub allows CLI/tests to run without external deps.
    """

    def __init__(self, connection_string: Optional[str] = None) -> None:
        self.connection_string = connection_string
        self._connected = False
        if connection_string:
            # TODO: attempt real connection
            LOGGER.warning(
                "AzzemCcamAdapter received connection string but real connection "
                "is not implemented; operating in stub mode."
            )

    def ping(self) -> bool:
        """
        Return False in stub mode; log that verification will be skipped.
        """
        if not self._connected:
            LOGGER.info("AzzemCcamAdapter: not connected (stub). Skipping verification.")
            return False
        return True

    def fetch_by_code(self, code: str) -> Optional[Dict[str, str]]:
        """
        Return None in stub mode.
        Expected real return: {'code': 'HBLD001', 'label': '...', 'materials': '...', 'basket': '...'}
        """
        LOGGER.debug("AzzemCcamAdapter.fetch_by_code(%s): stub -> None", code)
        return None
