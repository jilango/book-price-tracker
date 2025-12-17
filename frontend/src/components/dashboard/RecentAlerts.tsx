/** Recent alerts component for dashboard. */

import { useActiveAlerts } from '../../hooks/useAlerts';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { formatPrice, formatDateTime } from '../../utils/formatters';
import { Link } from 'react-router-dom';

export function RecentAlerts() {
  const { data: alertsData, isLoading } = useActiveAlerts(1, 5);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!alertsData || alertsData.alerts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Alerts</h2>
        <div className="text-center py-8">
          <p className="text-gray-600 mb-2">No active alerts at this time.</p>
          <p className="text-sm text-gray-500">
            Alerts will appear here when third-party prices are cheaper than Packt prices.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">Recent Alerts</h2>
        <Link
          to="/alerts"
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          View All →
        </Link>
      </div>
      <div className="space-y-4">
        {alertsData.alerts.map((alert) => (
          <div
            key={alert.id}
            className="border-l-4 border-red-500 pl-4 py-2 bg-red-50 rounded"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-gray-900">
                  {alert.book?.title || 'Unknown Book'}
                </h3>
                <p className="text-sm text-gray-600">
                  ISBN: {alert.book?.isbn || 'N/A'}
                </p>
                <div className="mt-2 flex items-center space-x-4 text-sm">
                  <span className="text-gray-700">
                    Packt: {formatPrice(alert.packt_price)}
                  </span>
                  <span className="text-gray-700">
                    {alert.third_party_source}: {formatPrice(alert.third_party_price)}
                  </span>
                  <span className="text-red-600 font-semibold">
                    Save: {formatPrice(alert.packt_price - alert.third_party_price)}
                  </span>
                </div>
              </div>
              <span className="text-xs text-gray-600">
                {formatDateTime(alert.notified_at)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

