/** Price history chart component for book detail page. */

import { usePriceHistory } from '../../hooks/useBooks';
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
import { formatPrice } from '../../utils/formatters';

interface PriceHistoryChartProps {
  bookId: number;
}

export function PriceHistoryChart({ bookId }: PriceHistoryChartProps) {
  const { data: history, isLoading } = usePriceHistory(bookId, 100);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!history || history.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Price History</h2>
        <p className="text-gray-600">No price history available for this book.</p>
      </div>
    );
  }

  // Group by source and date
  const chartData: Record<string, { date: string; packt?: number; [key: string]: any }> = {};

  history.forEach((entry) => {
    const date = new Date(entry.timestamp).toLocaleDateString();
    if (!chartData[date]) {
      chartData[date] = { date };
    }
    chartData[date][entry.source] = entry.price;
  });

  const data = Object.values(chartData).reverse();

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 pt-6 pb-2">
        <h2 className="text-xl font-bold text-gray-900">Price History</h2>
      </div>
      <div className="w-full px-6 pb-6" style={{ minHeight: '300px', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number) => (value ? formatPrice(value) : 'N/A')}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="packt"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Packt Price"
            dot={false}
          />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

