/** React Query hooks for books. */

import { useQuery } from '@tanstack/react-query';
import { booksAPI } from '../services/api';
import type { BookListResponse, PriceHistory } from '../types';

export function useBooks(params?: {
  search?: string;
  sort?: string;
  order?: string;
  page?: number;
  limit?: number;
  alert_only?: boolean;
}) {
  return useQuery<BookListResponse>({
    queryKey: ['books', params],
    queryFn: () => booksAPI.list(params),
  });
}

export function useBook(isbn: string) {
  return useQuery({
    queryKey: ['book', isbn],
    queryFn: () => booksAPI.getByISBN(isbn),
    enabled: !!isbn,
  });
}

export function usePriceHistory(bookId: number, limit = 100) {
  return useQuery<PriceHistory[]>({
    queryKey: ['price-history', bookId, limit],
    queryFn: () => booksAPI.getPriceHistory(bookId, limit),
    enabled: !!bookId,
  });
}

