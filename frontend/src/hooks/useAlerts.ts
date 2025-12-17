/** React Query hooks for alerts. */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsAPI } from '../services/api';
import type { AlertListResponse, Alert } from '../types';

export function useAlerts(params?: {
  status?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
}) {
  return useQuery<AlertListResponse>({
    queryKey: ['alerts', params],
    queryFn: () => alertsAPI.list(params),
  });
}

export function useActiveAlerts(page = 1, limit = 50) {
  return useQuery<AlertListResponse>({
    queryKey: ['alerts', 'active', page, limit],
    queryFn: () => alertsAPI.getActive(page, limit),
  });
}

export function useAlert(alertId: number) {
  return useQuery<Alert>({
    queryKey: ['alert', alertId],
    queryFn: () => alertsAPI.get(alertId),
    enabled: !!alertId,
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: number) => alertsAPI.acknowledge(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

