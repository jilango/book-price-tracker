"""Sync status endpoints."""

from fastapi import APIRouter, Depends
from api.models import SyncStatusResponse, SyncHistoryListResponse, SyncHistoryResponse
from api.dependencies import get_database
from src.storage.models import CSVSyncLog

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(db=Depends(get_database)):
    """Get CSV sync status."""
    from src.config import config
    from pathlib import Path
    
    csv_path = Path(config.csv_file_path)
    filename = csv_path.name if csv_path.exists() else None
    
    latest_sync = db.get_latest_sync_log(filename) if filename else None
    
    if latest_sync:
        return SyncStatusResponse(
            last_sync_time=latest_sync.last_processed_time,
            last_sync_hash=latest_sync.last_processed_hash,
            rows_processed=latest_sync.rows_processed,
            rows_inserted=latest_sync.rows_inserted,
            rows_updated=latest_sync.rows_updated,
            filename=latest_sync.filename
        )
    
    return SyncStatusResponse()


@router.get("/history", response_model=SyncHistoryListResponse)
async def get_sync_history(
    limit: int = 50,
    db=Depends(get_database)
):
    """Get sync history."""
    with db.get_session() as session:
        history = session.query(CSVSyncLog).order_by(
            CSVSyncLog.last_processed_time.desc()
        ).limit(limit).all()
        
        total = session.query(CSVSyncLog).count()
        
        return SyncHistoryListResponse(
            history=[SyncHistoryResponse.model_validate(h) for h in history],
            total=total
        )

