/** Book detail page. */

import { useParams, Link } from 'react-router-dom';
import { useBook, usePriceHistory } from '../hooks/useBooks';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { PriceHistoryChart } from '../components/charts/PriceHistoryChart';
import { formatPrice, formatDate } from '../utils/formatters';

export function BookDetail() {
  const { isbn } = useParams<{ isbn: string }>();
  const { data: book, isLoading: bookLoading } = useBook(isbn || '');
  const { data: priceHistory, isLoading: historyLoading } = usePriceHistory(
    book?.id || 0
  );

  if (bookLoading) {
    return <LoadingSpinner />;
  }

  if (!book) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Book not found</p>
        <Link to="/books" className="text-blue-600 hover:text-blue-800 mt-4 inline-block">
          ← Back to Books
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link
          to="/books"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-4 inline-block"
        >
          ← Back to Books
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{book.title || 'Unknown Title'}</h1>
        <p className="text-gray-600 mt-2">Book details and price history</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Book Information */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Book Information</h2>
          <dl className="space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-600">Title</dt>
              <dd className="mt-1 text-sm text-gray-900">{book.title || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Author</dt>
              <dd className="mt-1 text-sm text-gray-900">{book.author || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">ISBN</dt>
              <dd className="mt-1 text-sm text-gray-900">{book.isbn}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Packt Price</dt>
              <dd className="mt-1 text-lg font-semibold text-gray-900">
                {formatPrice(book.packt_price)}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Packt URL</dt>
              <dd className="mt-1 text-sm">
                {book.packt_url ? (
                  <a
                    href={book.packt_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {book.packt_url}
                  </a>
                ) : (
                  'N/A'
                )}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-600">Last Updated</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(book.last_updated)}</dd>
            </div>
          </dl>
        </div>

        {/* Price History Chart */}
        <div>
          {historyLoading ? (
            <LoadingSpinner />
          ) : (
            <PriceHistoryChart bookId={book.id} />
          )}
        </div>
      </div>
    </div>
  );
}

