/** Recent activity chart component. */

import { useRecentActivity } from '../../hooks/useStats';
import { LoadingSpinner } from '../common/LoadingSpinner';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export function RecentActivityChart() {
  const { data, isLoading, error } = useRecentActivity(30);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity (Last 30 Days)</h2>
        <p className="text-red-600">Error loading data: {error.message}</p>
      </div>
    );
  }

  if (!data || data.activity.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity (Last 30 Days)</h2>
        <div className="text-center py-8">
          <p className="text-gray-600 mb-2">No recent activity data available.</p>
          <p className="text-sm text-gray-600">
            Activity will appear here as books are added or updated.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 pt-6 pb-2">
        <h2 className="text-xl font-bold text-gray-900">Recent Activity (Last 30 Days)</h2>
      </div>
      <div className="w-full px-6 pb-6" style={{ minHeight: '300px', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data.activity} margin={{ top: 5, right: 30, left: 20, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number, name: string) => [
              `${value} ${name === 'books_added' ? 'added' : name === 'books_updated' ? 'updated' : 'changes'}`,
              name === 'books_added' ? 'Added' : name === 'books_updated' ? 'Updated' : 'Total',
            ]}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="books_added"
            stackId="1"
            stroke="#3b82f6"
            fill="#3b82f6"
            name="Books Added"
            opacity={0.8}
          />
          <Area
            type="monotone"
            dataKey="books_updated"
            stackId="1"
            stroke="#10b981"
            fill="#10b981"
            name="Books Updated"
            opacity={0.8}
          />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

