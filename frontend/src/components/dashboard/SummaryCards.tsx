/** Summary cards component for dashboard. */

import { useDashboardStats } from '../../hooks/useStats';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { formatPrice } from '../../utils/formatters';
import {
  BookIcon,
  DiamondIcon,
  DollarIcon,
  ChartBarIcon,
  PenIcon,
  LinkIcon,
  ChartLineIcon,
  CheckCircleIcon,
} from '../common/Icons';

export function SummaryCards() {
  const { data: stats, isLoading, error } = useDashboardStats();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading dashboard stats: {error.message}</p>
      </div>
    );
  }

  if (!stats) {
    return <div>No data available</div>;
  }

  // Row 1: Catalog Overview
  const catalogCards = [
    {
      title: 'Total Books',
      value: stats.total_books.toString(),
      Icon: BookIcon,
      color: 'bg-blue-500',
    },
    {
      title: 'Catalog Value',
      value: stats.total_catalog_value
        ? formatPrice(stats.total_catalog_value)
        : '$0.00',
      Icon: DiamondIcon,
      color: 'bg-purple-500',
    },
    {
      title: 'Average Price',
      value: stats.average_price
        ? formatPrice(stats.average_price)
        : 'N/A',
      Icon: DollarIcon,
      color: 'bg-green-500',
    },
    {
      title: 'Price Range',
      value: stats.min_price && stats.max_price
        ? `${formatPrice(stats.min_price)} - ${formatPrice(stats.max_price)}`
        : 'N/A',
      Icon: ChartBarIcon,
      color: 'bg-indigo-500',
    },
  ];

  // Row 2: Data Quality
  const qualityCards = [
    {
      title: 'Missing Authors',
      value: stats.books_missing_authors.toString(),
      Icon: PenIcon,
      color: 'bg-orange-500',
      subtitle: stats.books_missing_authors > 0 ? 'Needs attention' : 'All complete',
    },
    {
      title: 'Missing URLs',
      value: stats.books_missing_urls.toString(),
      Icon: LinkIcon,
      color: 'bg-pink-500',
      subtitle: stats.books_missing_urls > 0 ? 'Needs attention' : 'All complete',
    },
    {
      title: 'No Price History',
      value: stats.books_without_price_history.toString(),
      Icon: ChartLineIcon,
      color: 'bg-yellow-500',
      subtitle: stats.books_without_price_history > 0 ? 'Not tracked' : 'All tracked',
    },
    {
      title: 'Data Completeness',
      value: stats.data_completeness_percentage !== null && stats.data_completeness_percentage !== undefined
        ? `${Number(stats.data_completeness_percentage).toFixed(1)}%`
        : '0%',
      Icon: CheckCircleIcon,
      color: 'bg-teal-500',
      subtitle: 'Complete records',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Row 1: Catalog Overview */}
      <div>
        <h3 className="text-base font-semibold text-gray-700 mb-4">Catalog Overview</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {catalogCards.map((card) => {
            const IconComponent = card.Icon;
            return (
              <div
                key={card.title}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{card.title}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{card.value}</p>
                  </div>
                  <div className={`${card.color} rounded-full p-4 flex items-center justify-center`}>
                    <IconComponent className="text-white" size={24} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Row 2: Data Quality */}
      <div>
        <h3 className="text-base font-semibold text-gray-700 mb-4">Data Quality</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {qualityCards.map((card) => {
            const IconComponent = card.Icon;
            return (
              <div
                key={card.title}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{card.title}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{card.value}</p>
                    {card.subtitle && (
                      <p className="text-sm text-gray-600 mt-1">{card.subtitle}</p>
                    )}
                  </div>
                  <div className={`${card.color} rounded-full p-4 flex items-center justify-center`}>
                    <IconComponent className="text-white" size={24} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

