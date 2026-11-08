"""
app/routers/datasets.py
-----------------------
Dataset upload, listing, and preview endpoints.
Uses an in-memory store for uploaded datasets (not persisted across restarts).
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.data_cleaner import DataCleanerService

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

# ---------------------------------------------------------------------------
#  In-memory dataset store
# ---------------------------------------------------------------------------
# Key: dataset_id (str)
# Value: dict with metadata + the actual DataFrame
_datasets: Dict[str, Dict[str, Any]] = {}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(..., description="CSV file to upload (max 10 MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a CSV file for analysis.

    - Maximum file size: 10 MB
    - Only CSV files are accepted
    - The file is validated and cleaned before storage
    """
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported. Please upload a .csv file.",
        )

    # Read file content with size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Validate CSV structure
    file_content = content.decode("utf-8", errors="replace")
    validation = DataCleanerService.validate_csv(file_content, file.filename)

    if not validation.get("valid", False):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=validation.get("errors", ["Invalid CSV format"]),
        )

    # Parse into DataFrame
    try:
        df = pd.read_csv(io.StringIO(file_content))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse CSV: {str(exc)}",
        )

    # Clean the data
    df = DataCleanerService.clean_csv(df)

    # Store in memory
    dataset_id = str(uuid.uuid4())
    _datasets[dataset_id] = {
        "id": dataset_id,
        "filename": file.filename,
        "uploaded_by": current_user.email,
        "uploaded_at": datetime.now(tz=timezone.utc).isoformat(),
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "size_bytes": len(content),
        "dataframe": df,
    }

    return {
        "id": dataset_id,
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "size_bytes": len(content),
        "uploaded_at": _datasets[dataset_id]["uploaded_at"],
        "message": "Dataset uploaded and cleaned successfully",
    }


@router.get("")
def list_datasets(
    current_user: User = Depends(get_current_user),
):
    """List all uploaded datasets (metadata only, no data)."""
    datasets = []
    for dataset_id, meta in _datasets.items():
        datasets.append({
            "id": meta["id"],
            "filename": meta["filename"],
            "uploaded_by": meta["uploaded_by"],
            "uploaded_at": meta["uploaded_at"],
            "rows": meta["rows"],
            "columns": meta["columns"],
            "column_names": meta["column_names"],
            "size_bytes": meta["size_bytes"],
        })
    return {"datasets": datasets, "total": len(datasets)}


@router.get("/{dataset_id}/preview")
def preview_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
):
    """Return the first 50 rows of a previously uploaded dataset."""
    if dataset_id not in _datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found",
        )

    meta = _datasets[dataset_id]
    df: pd.DataFrame = meta["dataframe"]
    preview_df = df.head(50)

    return {
        "id": dataset_id,
        "filename": meta["filename"],
        "total_rows": meta["rows"],
        "preview_rows": len(preview_df),
        "columns": list(df.columns),
        "data": preview_df.to_dict(orient="records"),
    }
