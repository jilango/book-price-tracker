/** Header component. */

import { Link } from 'react-router-dom';
import { SearchBar } from './SearchBar';

interface HeaderProps {
  onSearch?: (query: string) => void;
}

export function Header({ onSearch }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-blue-600">
              Packt Price Watcher
            </Link>
          </div>
          {onSearch && (
            <div className="flex-1 max-w-md mx-8">
              <SearchBar onSearch={onSearch} placeholder="Search books..." />
            </div>
          )}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Sales Team</span>
          </div>
        </div>
      </div>
    </header>
  );
}

