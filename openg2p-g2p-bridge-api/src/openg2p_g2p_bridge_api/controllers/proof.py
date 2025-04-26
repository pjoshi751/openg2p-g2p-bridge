import logging
from typing import Optional, List
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, status, Depends
from openg2p_fastapi_common.controller import BaseController
from ..config import Settings
from ..services import ProofService

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class ProofController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proof_service = ProofService.get_component()
        self.router.tags += ["G2P Bridge Proof Submission"]
        
        # Register API route according to OpenAPI spec path
        self.router.add_api_route(
            "/api/v1/submit_proof", # Path from OpenAPI spec
            self.submit_proof,
            status_code=status.HTTP_200_OK,
            summary="Submit proof for disbursement",
            description="Submit proof images for a disbursement with agent and beneficiary details, geo location, photo descriptions, and optional JSON LD proofs.",
            methods=["POST"],
            # Define potential error responses based on OpenAPI spec
            responses={
                400: {"description": "Bad request, invalid input parameters"},
                404: {"description": "Disbursement ID not found"},
                409: {"description": "Disbursement information mismatch"},
                413: {"description": "Maximum limit for photos reached"},
                422: {"description": "Mandatory field not submitted"},
                500: {"description": "Internal server error"}
            }
        )

    async def submit_proof(
        self,
        disbursement_id: str = Form(..., description="ID of the disbursement"),
        agent_id: str = Form(..., description="ID of the agent submitting the proof"),
        beneficiary_id: str = Form(..., description="ID of the beneficiary"),
        latitude: float = Form(..., description="Latitude in decimal degrees"),
        longitude: float = Form(..., description="Longitude in decimal degrees"),
        photos: List[UploadFile] = File(..., description="Proof image files (min 1, max 5)"),
        geojson: Optional[str] = Form(None, description="Optional GeoJSON object as string"),
        proofs: Optional[str] = Form(None, description="Optional proofs in JSON LD format as string"),
        descriptions: Optional[List[str]] = Form(None, description="Optional descriptions for each photo"),
    ):
        """
        Handles the proof submission request.
        Validates basic constraints and calls the ProofService.
        Returns a success message or raises appropriate HTTP exceptions.
        """
        _logger.info(f"Controller received proof submission for disbursement_id={disbursement_id}")

        # Basic validation based on OpenAPI spec
        if len(photos) > 5:
            _logger.error("Too many photos submitted.")
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Maximum of 5 photos allowed.")
        if len(photos) < 1:
            _logger.error("No photos submitted.")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one photo must be submitted.")
        if descriptions and len(descriptions) != len(photos):
             _logger.error("Mismatch between number of photos and descriptions.")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of descriptions must match number of photos if provided.")

        # Call the dummy service method
        try:
            success = await self.proof_service.process_proof_submission(
                disbursement_id=disbursement_id,
                agent_id=agent_id,
                beneficiary_id=beneficiary_id,
                latitude=latitude,
                longitude=longitude,
                photos=photos,
                geojson=geojson,
                proofs=proofs,
                descriptions=descriptions,
            )
            if success:
                _logger.info(f"Proof submission processed successfully for disbursement_id={disbursement_id}")
                return {"status": "success", "message": "Proof submitted successfully"}
            else:
                # This part shouldn't be reached with the current dummy service
                _logger.error("Proof service indicated failure (unexpected for dummy service)")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Proof submission failed internally.")

        except Exception as e:
            _logger.exception(f"An unexpected error occurred during proof submission: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")

# Instantiate the controller
proof_controller = ProofController()
