/** Trends page. */

import { useState } from 'react';
import { usePriceTrends, useComparisonStats } from '../hooks/useStats';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { PriceTrendsChart } from '../components/dashboard/PriceTrendsChart';
import { formatPrice } from '../utils/formatters';

export function Trends() {
  const [days, setDays] = useState(30);
  const { data: trendsData, isLoading: trendsLoading } = usePriceTrends(days);
  const { data: comparisonStats, isLoading: statsLoading } = useComparisonStats();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Price Trends</h1>
          <p className="text-gray-600 mt-2">Analyze price trends and comparisons</p>
        </div>
        <div>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={180}>Last 180 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>
      </div>

      {/* Comparison Stats */}
      {statsLoading ? (
        <LoadingSpinner />
      ) : comparisonStats ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <p className="text-sm font-medium text-gray-600">Total Comparisons</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              {comparisonStats.total_comparisons}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <p className="text-sm font-medium text-gray-600">Packt Cheaper</p>
            <p className="text-2xl font-bold text-green-600 mt-2">
              {comparisonStats.packt_cheaper}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <p className="text-sm font-medium text-gray-600">Third-Party Cheaper</p>
            <p className="text-2xl font-bold text-red-600 mt-2">
              {comparisonStats.third_party_cheaper}
            </p>
            {comparisonStats.average_difference && (
              <p className="text-sm text-gray-600 mt-1">
                Avg difference: {formatPrice(comparisonStats.average_difference)}
              </p>
            )}
          </div>
        </div>
      ) : null}

      {/* Price Trends Chart */}
      {trendsLoading ? (
        <LoadingSpinner />
      ) : (
        <PriceTrendsChart days={days} />
      )}
    </div>
  );
}

