/** Utility functions for formatting data. */

export function formatPrice(price: number | null | undefined): string {
  if (price === null || price === undefined) {
    return 'N/A';
  }
  return `$${price.toFixed(2)}`;
}

export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return `${value.toFixed(2)}%`;
}

export function formatDate(date: string | null | undefined): string {
  if (!date) {
    return 'N/A';
  }
  try {
    return new Date(date).toLocaleDateString();
  } catch {
    return 'Invalid Date';
  }
}

export function formatDateTime(date: string | null | undefined): string {
  if (!date) {
    return 'N/A';
  }
  try {
    return new Date(date).toLocaleString();
  } catch {
    return 'Invalid Date';
  }
}

export function formatISBN(isbn: string): string {
  // Format ISBN for display (add hyphens if needed)
  return isbn;
}

