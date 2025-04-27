import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from openg2p_fastapi_common.service import BaseService
from openg2p_fastapi_common.context import dbengine
from sqlalchemy.ext.asyncio import async_sessionmaker
from openg2p_g2p_bridge_models.models import Proof 
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class ProofService(BaseService):
    async def process_submission(
        self,
        disbursement_id: str,
        agent_id: str,
        beneficiary_id: str,
        latitude: float,
        longitude: float,
        photo_details: List[Dict[str, Any]],
        geojson: Optional[Dict[str, Any]] = None,
        proofs_ld: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Processes the proof submission and saves it to the database.

        Args:
            disbursement_id: The ID of the disbursement.
            agent_id: The ID of the agent submitting the proof.
            beneficiary_id: The ID of the beneficiary.
            latitude: The latitude of the submission location.
            longitude: The longitude of the submission location.
            photo_details: A list of dictionaries, each containing 'file_path' and 'description'.
            geojson: Optional GeoJSON data associated with the proof.
            proofs_ld: Optional JSON-LD proofs data.

        Returns:
            The ID of the created proof record.

        Raises:
            HTTPException: If a database error occurs or an unexpected error happens.
        """
        _logger.info(
            f"Processing proof submission in service for disbursement_id={disbursement_id}"
        )
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            try:
                new_proof = Proof(
                    disbursement_id=disbursement_id,
                    agent_id=agent_id,
                    beneficiary_id=beneficiary_id,
                    latitude=latitude,
                    longitude=longitude,
                    photo_details=photo_details,
                    geojson=geojson,
                    proofs_ld=proofs_ld,
                    active=True
                )

                session.add(new_proof)
                await session.commit()
                await session.refresh(new_proof)

                _logger.info(f"Successfully saved proof with ID: {new_proof.id}")
                if new_proof.id is None:
                    _logger.error("Proof ID is None after commit and refresh.")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve proof ID after saving.",
                    )
                return int(new_proof.id)

            except SQLAlchemyError as e:
                await session.rollback()
                _logger.error(f"Database error during proof submission: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error saving proof: {e}",
                )
            except Exception as e:
                await session.rollback()
                _logger.error(f"Unexpected error during proof submission: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"An unexpected error occurred: {e}",
                )


# Instantiate the service
proof_service = ProofService()
