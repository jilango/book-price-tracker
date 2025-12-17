/** Books list page. */

import { useState } from 'react';
import { useBooks } from '../hooks/useBooks';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { SearchBar } from '../components/common/SearchBar';
import { formatPrice, formatDate } from '../utils/formatters';
import { Link } from 'react-router-dom';
import type { Book } from '../types';

export function Books() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('id');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');

  const { data, isLoading, error } = useBooks({
    search: search || undefined,
    sort,
    order,
    page,
    limit: 20,
  });

  const handleSort = (field: string) => {
    if (sort === field) {
      setOrder(order === 'asc' ? 'desc' : 'asc');
    } else {
      setSort(field);
      setOrder('asc');
    }
  };

  const getAttentionIssues = (book: Book) => {
    const issues: string[] = [];
    if (!book.author || book.author.trim() === '') {
      issues.push('Missing Author');
    }
    if (!book.packt_url || book.packt_url.trim() === '') {
      issues.push('Missing URL');
    }
    if (!book.packt_price) {
      issues.push('Missing Price');
    }
    return issues;
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-600">Error loading books: {error.message}</div>;
  }

  return (
    <div className="space-y-6 max-w-full overflow-x-hidden">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Books</h1>
          <p className="text-gray-600 mt-2">Manage and view all tracked books</p>
        </div>
        <div className="w-full sm:w-64">
          <SearchBar
            onSearch={setSearch}
            placeholder="Search by title, author, or ISBN..."
          />
        </div>
      </div>

      {data && (
        <>
          <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden w-full">
            <div className="overflow-x-auto -mx-0">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleSort('title')}
                    >
                      Title {sort === 'title' && (order === 'asc' ? '↑' : '↓')}
                    </th>
                    <th
                      className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleSort('author')}
                    >
                      Author {sort === 'author' && (order === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ISBN
                    </th>
                    <th
                      className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleSort('packt_price')}
                    >
                      Packt Price {sort === 'packt_price' && (order === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Updated
                    </th>
                    <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Attention Needed
                    </th>
                    <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.books.map((book) => {
                    const issues = getAttentionIssues(book);
                    const hasIssues = issues.length > 0;
                    return (
                      <tr 
                        key={book.id} 
                        className="hover:bg-gray-50"
                      >
                        <td className="px-4 sm:px-6 py-4">
                          <div className="text-sm font-medium text-gray-900 max-w-xs truncate" title={book.title || 'N/A'}>
                            {book.title || 'N/A'}
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4">
                          <div className="text-sm text-gray-600 max-w-xs truncate" title={book.author || 'N/A'}>
                            {book.author || 'N/A'}
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{book.isbn}</div>
                        </td>
                        <td className="px-4 sm:px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {formatPrice(book.packt_price)}
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">
                            {formatDate(book.last_updated)}
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4">
                          {hasIssues ? (
                            <div className="flex flex-wrap gap-1">
                              {issues.map((issue, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-orange-100 text-orange-800"
                                >
                                  {issue}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <Link
                            to={`/books/${book.isbn}`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            View Details
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of{' '}
              {data.total} books
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

