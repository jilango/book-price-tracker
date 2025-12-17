/** TypeScript type definitions for the application. */

export interface Book {
  id: number;
  isbn: string;
  title: string | null;
  author: string | null;
  packt_price: number | null;
  packt_url: string | null;
  last_updated: string | null;
  created_at: string | null;
}

export interface BookListResponse {
  books: Book[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface PriceHistory {
  id: number;
  book_id: number;
  source: string;
  price: number | null;
  timestamp: string;
}

export interface Alert {
  id: number;
  book_id: number;
  book?: Book;
  threshold_type: string;
  threshold_value: number;
  packt_price: number;
  third_party_price: number;
  third_party_source: string;
  notified_at: string;
  status: string;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface DashboardStats {
  // Legacy fields
  total_books: number;
  active_alerts: number;
  average_price_difference: number | null;
  total_savings_opportunity: number | null;
  books_with_alerts: number;
  // New catalog overview fields
  total_catalog_value: number | null;
  min_price: number | null;
  max_price: number | null;
  average_price: number | null;
  // Data quality fields
  books_missing_authors: number;
  books_missing_urls: number;
  books_without_price_history: number;
  data_completeness_percentage: number | null;
}

export interface PriceTrendDataPoint {
  date: string;
  packt_price: number | null;
  third_party_price: number | null;
  difference: number | null;
}

export interface PriceTrendsResponse {
  trends: PriceTrendDataPoint[];
  date_from: string | null;
  date_to: string | null;
}

export interface ComparisonStats {
  total_comparisons: number;
  packt_cheaper: number;
  third_party_cheaper: number;
  average_difference: number | null;
}

export interface SyncStatus {
  last_sync_time: string | null;
  last_sync_hash: string | null;
  rows_processed: number;
  rows_inserted: number;
  rows_updated: number;
  filename: string | null;
}

export interface SyncHistory {
  id: number;
  filename: string;
  last_processed_time: string;
  rows_processed: number;
  rows_inserted: number;
  rows_updated: number;
}

export interface SyncHistoryListResponse {
  history: SyncHistory[];
  total: number;
}

export interface PriceBucket {
  range: string;
  count: number;
  percentage: number;
}

export interface PriceDistributionResponse {
  buckets: PriceBucket[];
  total_books: number;
}

export interface DataQualityResponse {
  total_books: number;
  books_missing_authors: number;
  books_missing_urls: number;
  books_missing_prices: number;
  books_without_price_history: number;
  books_stale: number;
  data_completeness_percentage: number;
  books_needing_attention: Book[];
}

export interface ActivityDataPoint {
  date: string;
  books_added: number;
  books_updated: number;
  total_changes: number;
}

export interface RecentActivityResponse {
  activity: ActivityDataPoint[];
  date_from: string | null;
  date_to: string | null;
}

