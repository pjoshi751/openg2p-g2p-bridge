import logging
import os
import shutil
import json
import uuid # For unique temporary directory
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import (
    APIRouter, Form, File, UploadFile, HTTPException, status, Depends
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError # Import SQLAlchemyError

from openg2p_fastapi_common.controller import BaseController
from ..config import Settings
# Import the instantiated service instance, not the class directly for Depends
from ..services.proof import ProofService, proof_service

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)

# Define upload directory base
UPLOAD_DIR_BASE = Path("/tmp/proof_uploads")

class ProofController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Correctly get the service instance using get_component()
        # Remove the incorrect Depends assignment
        # self.service = Depends(proof_service) 
        self.service = ProofService.get_component()

        self.router.tags += ["G2P Bridge Proof"] # Use a descriptive tag

        # Ensure base upload directory exists
        UPLOAD_DIR_BASE.mkdir(parents=True, exist_ok=True)

        # Keep the route definition as is
        self.router.add_api_route(
            # ... (route definition remains the same) ...
            path="/api/v1/submit_proof",
            endpoint=self.submit_proof,
            status_code=status.HTTP_200_OK,
            summary="Submit proof for disbursement",
            description="Submit proof images for a disbursement with agent and beneficiary details, geo location, photo descriptions, and optional JSON LD proofs.",
            methods=["POST"],
            responses={
                400: {"description": "Bad request, invalid input parameters"},
                404: {"description": "Disbursement ID not found"}, # Potentially from service
                409: {"description": "Disbursement information mismatch"}, # Potentially from service
                413: {"description": "Maximum limit for photos reached"},
                422: {"description": "Mandatory field not submitted or invalid JSON"},
                500: {"description": "Internal server error"}
            }
        )

    def _cleanup_files(self, upload_dir: Path):
        """Removes the temporary upload directory and its contents."""
        if upload_dir.exists():
            try:
                shutil.rmtree(upload_dir)
                _logger.info(f"Cleaned up temporary directory: {upload_dir}")
            except Exception as e:
                _logger.error(f"Error cleaning up directory {upload_dir}: {e}", exc_info=True)

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
        Handles the proof submission request. Saves photos, parses JSON,
        calls the ProofService to save data, and handles cleanup.
        """
        _logger.info(f"Controller received proof submission for disbursement_id={disbursement_id}")

        # 1. Basic Validation
        if len(photos) > 5:
            _logger.error("Too many photos submitted.")
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Maximum of 5 photos allowed.")
        if len(photos) < 1:
             _logger.error("No photos submitted.")
             raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one photo must be submitted.")
        if descriptions and len(descriptions) != len(photos):
            _logger.error("Mismatch between number of photos and descriptions.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of descriptions must match number of photos if provided.")

        # 2. Setup Temporary Storage
        request_id = str(uuid.uuid4())
        upload_dir = UPLOAD_DIR_BASE / request_id
        upload_dir.mkdir(parents=True, exist_ok=False) # Create unique dir for this request
        _logger.info(f"Created temporary upload directory: {upload_dir}")

        photo_details: List[Dict[str, Any]] = []
        saved_file_paths: List[str] = [] # Keep track for potential cleanup

        try:
            # 3. Process and Save Photos Synchronously
            for i, photo in enumerate(photos):
                if not photo.filename:
                     # Should not happen with File(...) but check anyway
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Photo {i+1} has no filename.")

                # Sanitize filename (basic example)
                safe_filename = f"{i+1}_{Path(photo.filename).name}"
                file_path = upload_dir / safe_filename
                try:
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(photo.file, buffer)
                    saved_file_paths.append(str(file_path)) # Store absolute path as string
                    # Get description or default to empty string
                    description = descriptions[i] if descriptions and i < len(descriptions) else ""
                    photo_details.append({"file_path": str(file_path), "description": description})
                    _logger.debug(f"Saved photo to: {file_path}")
                except Exception as e:
                    _logger.error(f"Failed to save photo {photo.filename}: {e}", exc_info=True)
                    # Raise 500 as it's a server-side file issue
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save photo: {photo.filename}")
                finally:
                    # Ensure file object is closed
                    await photo.close()

            # 4. Parse JSON fields
            geojson_dict: Optional[Dict[str, Any]] = None
            proofs_ld_dict: Optional[Dict[str, Any]] = None

            if geojson:
                try:
                    geojson_dict = json.loads(geojson)
                except json.JSONDecodeError:
                    _logger.error("Invalid GeoJSON format received.")
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid GeoJSON format.")

            if proofs:
                try:
                    proofs_ld_dict = json.loads(proofs)
                except json.JSONDecodeError:
                    _logger.error("Invalid Proofs LD JSON format received.")
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid Proofs LD JSON format.")

            # 5. Call the Service Layer
            # Use the injected service instance `self.service`
            created_proof_id = await self.service.process_submission(
                disbursement_id=disbursement_id,
                agent_id=agent_id,
                beneficiary_id=beneficiary_id,
                latitude=latitude,
                longitude=longitude,
                photo_details=photo_details, # Pass the processed list
                geojson=geojson_dict,       # Pass the parsed dict
                proofs_ld=proofs_ld_dict   # Pass the parsed dict
            )

            _logger.info(f"Proof submission processed by service, created proof ID: {created_proof_id}")
            # Success: Return the ID
            return {
                "status": "success",
                "message": "Proof submitted successfully",
                "proof_id": created_proof_id,
            }

        except (HTTPException, SQLAlchemyError) as e:
            # If a known HTTP error (from validation, service, etc.) or DB error occurred, re-raise it
            # The service layer should handle db.rollback() for SQLAlchemyError
            _logger.error(f"Caught HTTPException or SQLAlchemyError: {e}", exc_info=True)
            raise e # Re-raise the exception
        except Exception as e:
            # Catch any other unexpected errors during file processing, JSON parsing, etc.
            _logger.exception(f"An unexpected error occurred during proof submission: {e}")
            # Ensure rollback if an unexpected error occurs before the service call
            # (though service handles its own rollback)
            # await db.rollback() # Careful: Only rollback if session is active and error happened before service commit
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")
        finally:
            # IMPORTANT: Cleanup should happen if *any* exception occurred
            # We check if 'created_proof_id' was successfully assigned. If not, an error happened.
             if 'created_proof_id' not in locals():
                self._cleanup_files(upload_dir)
            # If successful ('created_proof_id' exists), the files should *not* be cleaned up yet.
            # Cleanup of successfully processed files should be handled elsewhere (e.g., background task after archival).

# Instantiate the controller
proof_controller = ProofController()
