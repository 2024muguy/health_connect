/**
 * HealthConnect AI - useHealthCheck Hook
 * Backend health check polling
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '@/lib/constants';

interface HealthCheckResult {
  isLoading: boolean;
  isError: boolean;
  isHealthy: boolean;
  data: Record<string, unknown> | null;
  refetch: () => Promise<void>;
}

export function useHealthCheck(intervalMs: number = 30000): HealthCheckResult {
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [isHealthy, setIsHealthy] = useState(false);
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
        timeout: 5000,
      });
      setIsHealthy(response.data?.status === 'healthy');
      setData(response.data);
      setIsError(false);
    } catch {
      setIsHealthy(false);
      setIsError(true);
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();

    if (intervalMs > 0) {
      const interval = setInterval(checkHealth, intervalMs);
      return () => clearInterval(interval);
    }
  }, [checkHealth, intervalMs]);

  return {
    isLoading,
    isError,
    isHealthy,
    data,
    refetch: checkHealth,
  };
}