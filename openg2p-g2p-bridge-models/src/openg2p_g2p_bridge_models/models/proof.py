from datetime import datetime
from typing import Any, Dict, List, Optional

from openg2p_fastapi_common.models import BaseORMModelWithTimes
from sqlalchemy import DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB  # Assuming PostgreSQL for JSONB
# from sqlalchemy import JSON # Use this for generic JSON support
from sqlalchemy.orm import Mapped, mapped_column


class Proof(BaseORMModelWithTimes):
    """Model to store proof submission details."""

    __tablename__ = "proofs"

    # Corresponds to the disbursement this proof is for
    disbursement_id: Mapped[str] = mapped_column(String, index=True)

    # IDs of the involved parties
    agent_id: Mapped[str] = mapped_column(String, index=True)
    beneficiary_id: Mapped[str] = mapped_column(String, index=True)

    # Geo-location data
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # List of photo details (e.g., [{'path': '/path/to/img1.jpg', 'description': 'desc1'}, ...])
    # Storing paths/identifiers, not the binary data itself.
    photo_details: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)

    # Optional GeoJSON data
    geojson: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Optional JSON-LD proofs data (renamed from 'proofs' to avoid conflict)
    proofs_ld: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, name="proofs_ld", nullable=True)

    # Timestamp of the submission
    submission_timestamp: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, index=True
    )

    def __repr__(self) -> str:
        return f"<Proof(id={self.id}, disbursement_id='{self.disbursement_id}', agent_id='{self.agent_id}')>"
