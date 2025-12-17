"""Alert endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Depends
from api.models import AlertResponse, AlertListResponse
from api.services.alert_service import AlertService
from api.dependencies import get_database

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db=Depends(get_database)
):
    """List all alerts with filtering and pagination."""
    alerts, total = AlertService.get_alerts(
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit
    )
    
    total_pages = (total + limit - 1) // limit
    
    # Include book information
    alert_responses = []
    for alert in alerts:
        alert_dict = AlertResponse.model_validate(alert).model_dump()
        if alert.book:
            from api.models import BookResponse
            alert_dict['book'] = BookResponse.model_validate(alert.book).model_dump()
        alert_responses.append(AlertResponse(**alert_dict))
    
    return AlertListResponse(
        alerts=alert_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/active", response_model=AlertListResponse)
async def get_active_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db=Depends(get_database)
):
    """Get active alerts only."""
    alerts, total = AlertService.get_active_alerts(page=page, limit=limit)
    
    total_pages = (total + limit - 1) // limit
    
    alert_responses = []
    for alert in alerts:
        alert_dict = AlertResponse.model_validate(alert).model_dump()
        if alert.book:
            from api.models import BookResponse
            alert_dict['book'] = BookResponse.model_validate(alert.book).model_dump()
        alert_responses.append(AlertResponse(**alert_dict))
    
    return AlertListResponse(
        alerts=alert_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db=Depends(get_database)):
    """Get alert by ID."""
    alert = AlertService.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert_dict = AlertResponse.model_validate(alert).model_dump()
    if alert.book:
        from api.models import BookResponse
        alert_dict['book'] = BookResponse.model_validate(alert.book).model_dump()
    
    return AlertResponse(**alert_dict)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: int, db=Depends(get_database)):
    """Acknowledge an alert."""
    alert = AlertService.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert_dict = AlertResponse.model_validate(alert).model_dump()
    if alert.book:
        from api.models import BookResponse
        alert_dict['book'] = BookResponse.model_validate(alert.book).model_dump()
    
    return AlertResponse(**alert_dict)

