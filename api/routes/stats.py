"""Statistics endpoints."""

from typing import Optional
from fastapi import APIRouter, Query, Depends
from api.models import (
    DashboardStatsResponse,
    PriceTrendsResponse,
    ComparisonStatsResponse,
    PriceTrendDataPoint,
    PriceDistributionResponse,
    DataQualityResponse,
    RecentActivityResponse
)
from api.services.stats_service import StatsService
from api.dependencies import get_database

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db=Depends(get_database)):
    """Get dashboard summary statistics."""
    return StatsService.get_dashboard_stats()


@router.get("/price-trends", response_model=PriceTrendsResponse)
async def get_price_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    db=Depends(get_database)
):
    """Get price trends data for charts."""
    trends = StatsService.get_price_trends(days=days, book_id=book_id)
    return PriceTrendsResponse(trends=trends)


@router.get("/comparison", response_model=ComparisonStatsResponse)
async def get_comparison_stats(db=Depends(get_database)):
    """Get price comparison statistics."""
    return StatsService.get_comparison_stats()


@router.get("/price-distribution", response_model=PriceDistributionResponse)
async def get_price_distribution(db=Depends(get_database)):
    """Get price distribution by buckets."""
    return StatsService.get_price_distribution()


@router.get("/data-quality", response_model=DataQualityResponse)
async def get_data_quality(db=Depends(get_database)):
    """Get data quality metrics."""
    return StatsService.get_data_quality()


@router.get("/recent-activity", response_model=RecentActivityResponse)
async def get_recent_activity(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db=Depends(get_database)
):
    """Get recent activity timeline."""
    return StatsService.get_recent_activity(days=days)

