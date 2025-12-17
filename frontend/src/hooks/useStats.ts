/** React Query hooks for statistics. */

import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '../services/api';
import type {
  DashboardStats,
  PriceTrendsResponse,
  ComparisonStats,
  PriceDistributionResponse,
  DataQualityResponse,
  RecentActivityResponse,
} from '../types';

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ['stats', 'dashboard'],
    queryFn: () => statsAPI.getDashboard(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function usePriceTrends(days = 30, bookId?: number) {
  return useQuery<PriceTrendsResponse>({
    queryKey: ['stats', 'price-trends', days, bookId],
    queryFn: () => statsAPI.getPriceTrends(days, bookId),
  });
}

export function useComparisonStats() {
  return useQuery<ComparisonStats>({
    queryKey: ['stats', 'comparison'],
    queryFn: () => statsAPI.getComparison(),
  });
}

export function usePriceDistribution() {
  return useQuery<PriceDistributionResponse>({
    queryKey: ['stats', 'price-distribution'],
    queryFn: () => statsAPI.getPriceDistribution(),
  });
}

export function useDataQuality() {
  return useQuery<DataQualityResponse>({
    queryKey: ['stats', 'data-quality'],
    queryFn: () => statsAPI.getDataQuality(),
  });
}

export function useRecentActivity(days = 30) {
  return useQuery<RecentActivityResponse>({
    queryKey: ['stats', 'recent-activity', days],
    queryFn: () => statsAPI.getRecentActivity(days),
  });
}

