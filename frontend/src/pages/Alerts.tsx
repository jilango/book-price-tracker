/** Alerts page. */

import { useState } from 'react';
import { useAlerts, useAcknowledgeAlert } from '../hooks/useAlerts';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { formatPrice, formatDateTime } from '../utils/formatters';
import { Link } from 'react-router-dom';

export function Alerts() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<string>('');
  const acknowledgeMutation = useAcknowledgeAlert();

  const { data, isLoading, error } = useAlerts({
    status: status || undefined,
    page,
    limit: 20,
  });

  const handleAcknowledge = async (alertId: number) => {
    try {
      await acknowledgeMutation.mutateAsync(alertId);
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-600">Error loading alerts: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Price Alerts</h1>
          <p className="text-gray-600 mt-2">View and manage price drop alerts</p>
        </div>
        <div>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <option value="">All Statuses</option>
            <option value="sent">Sent</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {data && (
        <>
          <div className="grid grid-cols-1 gap-4">
            {data.alerts.map((alert) => (
              <div
                key={alert.id}
                className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {alert.book?.title || 'Unknown Book'}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          alert.status === 'sent'
                            ? 'bg-red-100 text-red-800'
                            : alert.status === 'acknowledged'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {alert.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">
                      ISBN: {alert.book?.isbn || 'N/A'} | Author:{' '}
                      {alert.book?.author || 'N/A'}
                    </p>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-xs text-gray-600">Packt Price</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {formatPrice(alert.packt_price)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">
                          {alert.third_party_source} Price
                        </p>
                        <p className="text-lg font-semibold text-gray-900">
                          {formatPrice(alert.third_party_price)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Savings</p>
                        <p className="text-lg font-semibold text-red-600">
                          {formatPrice(alert.packt_price - alert.third_party_price)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>Threshold: {alert.threshold_type}</span>
                      <span>•</span>
                      <span>Notified: {formatDateTime(alert.notified_at)}</span>
                    </div>
                  </div>
                  <div className="flex flex-col space-y-2 ml-4">
                    {alert.book && (
                      <Link
                        to={`/books/${alert.book.isbn}`}
                        className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800"
                      >
                        View Book
                      </Link>
                    )}
                    {alert.status === 'sent' && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={acknowledgeMutation.isPending}
                        className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
                      >
                        Acknowledge
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of{' '}
              {data.total} alerts
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                disabled={page >= data.total_pages}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

