/** Price distribution chart component. */

import { usePriceDistribution } from '../../hooks/useStats';
import { LoadingSpinner } from '../common/LoadingSpinner';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export function PriceDistributionChart() {
  const { data, isLoading, error } = usePriceDistribution();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Price Distribution</h2>
        <p className="text-red-600">Error loading data: {error.message}</p>
      </div>
    );
  }

  if (!data || data.buckets.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Price Distribution</h2>
        <p className="text-gray-600">No price data available.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 pt-6 pb-2">
        <h2 className="text-xl font-bold text-gray-900">Price Distribution</h2>
      </div>
      <div className="w-full px-6 pb-6" style={{ minHeight: '350px', height: '350px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.buckets} margin={{ top: 10, right: 20, left: 10, bottom: 45 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="range"
              tick={{ fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={55}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: number, name: string, props: any) => [
                `${value} books (${props.payload.percentage}%)`,
                'Count',
              ]}
            />
            <Legend />
            <Bar dataKey="count" fill="#3b82f6" name="Number of Books" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

