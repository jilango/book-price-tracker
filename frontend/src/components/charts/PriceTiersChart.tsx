/** Price tiers chart component. */

import { usePriceDistribution } from '../../hooks/useStats';
import { LoadingSpinner } from '../common/LoadingSpinner';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export function PriceTiersChart() {
  const { data, isLoading, error } = usePriceDistribution();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Price Tiers</h2>
        <p className="text-red-600">Error loading data: {error.message}</p>
      </div>
    );
  }

  if (!data || data.buckets.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Price Tiers</h2>
        <p className="text-gray-600">No price data available.</p>
      </div>
    );
  }

  // Group into tiers
  const tiers = [
    { name: 'Budget ($0-10)', count: 0, color: COLORS[0] },
    { name: 'Mid-range ($10-20)', count: 0, color: COLORS[1] },
    { name: 'Premium ($20-30)', count: 0, color: COLORS[2] },
    { name: 'Premium+ ($30+)', count: 0, color: COLORS[3] },
  ];

  data.buckets.forEach((bucket) => {
    const range = bucket.range;
    if (range === '$0-5' || range === '$5-10') {
      tiers[0].count += bucket.count;
    } else if (range === '$10-15' || range === '$15-20') {
      tiers[1].count += bucket.count;
    } else if (range === '$20-25' || range === '$25-30') {
      tiers[2].count += bucket.count;
    } else if (range === '$30+') {
      tiers[3].count += bucket.count;
    }
  });

  const chartData = tiers.filter((tier) => tier.count > 0);

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 pt-6 pb-2">
        <h2 className="text-xl font-bold text-gray-900">Price Tiers</h2>
      </div>
      <div className="w-full px-6 pb-6" style={{ minHeight: '350px', height: '350px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={110}
              fill="#8884d8"
              dataKey="count"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => [`${value} books`, 'Count']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

