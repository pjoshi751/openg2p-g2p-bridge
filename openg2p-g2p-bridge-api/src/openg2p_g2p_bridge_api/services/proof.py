import logging
from typing import Optional, List
from fastapi import UploadFile
from openg2p_fastapi_common.service import BaseService
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)

class ProofService(BaseService):
    async def process_proof_submission(
        self,
        disbursement_id: str,
        agent_id: str,
        beneficiary_id: str,
        latitude: float,
        longitude: float,
        photos: List[UploadFile],
        geojson: Optional[str] = None,
        proofs: Optional[str] = None,
        descriptions: Optional[List[str]] = None,
    ) -> bool:
        """
        Dummy service method to handle proof submission.
        Currently logs receipt and returns True.
        
        In a real implementation, this would involve:
        1. Validating data against DB (e.g., disbursement exists)
        2. Saving photo files to storage
        3. Saving proof metadata to the database
        4. Handling potential errors
        """
        _logger.info(
            f"ProofService received submission for disbursement_id={disbursement_id}, "
            f"agent_id={agent_id}, beneficiary_id={beneficiary_id} with {len(photos)} photos."
        )
        # Dummy implementation always succeeds for now
        return True

# Instantiate the service for potential use with get_component()
proof_service = ProofService()
