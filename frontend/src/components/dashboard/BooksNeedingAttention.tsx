/** Books needing attention component. */

import { useDataQuality } from '../../hooks/useStats';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../utils/formatters';

export function BooksNeedingAttention() {
  const { data: qualityData, isLoading, error } = useDataQuality();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Books Needing Attention</h2>
        <p className="text-red-600">Error loading data: {error.message}</p>
      </div>
    );
  }

  if (!qualityData || qualityData.books_needing_attention.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Books Needing Attention</h2>
        <div className="text-center py-8">
          <p className="text-gray-600">All books have complete data! 🎉</p>
        </div>
      </div>
    );
  }

  // Group books by issue type
  const booksByIssue: Record<string, typeof qualityData.books_needing_attention> = {
    missing_author: [],
    missing_url: [],
    missing_price: [],
  };

  qualityData.books_needing_attention.forEach((book) => {
    if (!book.author || book.author.trim() === '') {
      booksByIssue.missing_author.push(book);
    }
    if (!book.packt_url || book.packt_url.trim() === '') {
      booksByIssue.missing_url.push(book);
    }
    if (!book.packt_price) {
      booksByIssue.missing_price.push(book);
    }
  });

  const issueLabels: Record<string, string> = {
    missing_author: 'Missing Author',
    missing_url: 'Missing URL',
    missing_price: 'Missing Price',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h2 className="text-xl font-bold text-gray-900 mb-6">
        Books Needing Attention ({qualityData.books_needing_attention.length})
      </h2>
      <div className="space-y-6">
        {Object.entries(booksByIssue).map(([issueType, books]) => {
          if (books.length === 0) return null;

          return (
            <div key={issueType}>
              <h3 className="text-base font-semibold text-gray-700 mb-3">
                {issueLabels[issueType]} ({books.length})
              </h3>
              <div className="space-y-2">
                {books.slice(0, 5).map((book) => (
                  <div
                    key={book.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex-1 min-w-0">
                      <Link
                        to={`/books/${book.isbn}`}
                        className="font-medium text-blue-600 hover:text-blue-800 truncate block"
                        title={book.title || 'Untitled'}
                      >
                        {book.title || 'Untitled'}
                      </Link>
                      <p className="text-sm text-gray-600 mt-1">
                        ISBN: {book.isbn}
                        {book.packt_price && ` • Price: ${formatPrice(book.packt_price)}`}
                      </p>
                    </div>
                    <Link
                      to={`/books/${book.isbn}`}
                      className="ml-4 text-base text-blue-600 hover:text-blue-800 font-medium whitespace-nowrap"
                    >
                      View →
                    </Link>
                  </div>
                ))}
                {books.length > 5 && (
                  <p className="text-sm text-gray-600 mt-2">
                    +{books.length - 5} more books with this issue
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

