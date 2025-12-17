/** Price trends chart component. */

import { usePriceTrends } from '../../hooks/useStats';
import { LoadingSpinner } from '../common/LoadingSpinner';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PriceTrendsChartProps {
  days?: number;
  bookId?: number;
}

export function PriceTrendsChart({ days = 30, bookId }: PriceTrendsChartProps) {
  const { data: trendsData, isLoading } = usePriceTrends(days, bookId);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!trendsData || trendsData.trends.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Price Trends (Last {days} Days)</h2>
        <div className="text-center py-8">
          <p className="text-gray-600 mb-2">No price data available for the selected period.</p>
          <p className="text-sm text-gray-600">
            Price history will appear here as books are tracked over time.
          </p>
        </div>
      </div>
    );
  }

  // If only one data point, show it differently or add a note
  const hasMultiplePoints = trendsData.trends.length > 1;

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 pt-6 pb-2">
        <h2 className="text-xl font-bold text-gray-900">Price Trends (Last {days} Days)</h2>
        {!hasMultiplePoints && (
          <p className="text-sm text-gray-600 mt-2">
            Limited data available. More data points will appear as prices are tracked over time.
          </p>
        )}
      </div>
      <div className="w-full px-6 pb-6" style={{ minHeight: '400px', height: '400px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trendsData.trends} margin={{ top: 10, right: 30, left: 20, bottom: hasMultiplePoints ? 80 : 40 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={hasMultiplePoints ? -45 : 0}
            textAnchor={hasMultiplePoints ? "end" : "middle"}
            height={hasMultiplePoints ? 80 : 40}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number) => (value ? `$${value.toFixed(2)}` : 'N/A')}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="packt_price"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Packt Price (Avg)"
            dot={true}
            activeDot={{ r: 6 }}
          />
          {trendsData.trends.some(t => t.third_party_price !== null) && (
            <Line
              type="monotone"
              dataKey="third_party_price"
              stroke="#ef4444"
              strokeWidth={2}
              name="Third-Party Price"
              dot={true}
              activeDot={{ r: 6 }}
            />
          )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

