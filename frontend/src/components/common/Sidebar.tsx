/** Sidebar navigation component. */

import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChartPieIcon, BookIcon, BellIcon, ChartLineIcon } from './Icons';

const navigation = [
  { name: 'Dashboard', href: '/', Icon: ChartPieIcon },
  { name: 'Books', href: '/books', Icon: BookIcon },
  { name: 'Alerts', href: '/alerts', Icon: BellIcon },
  { name: 'Trends', href: '/trends', Icon: ChartLineIcon },
];

export function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-md shadow-md border border-gray-200"
        aria-label="Toggle menu"
      >
        <svg
          className="w-6 h-6 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          {isOpen ? (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          ) : (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          )}
        </svg>
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-gray-50 border-r border-gray-200 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <nav className="p-4 pt-16 lg:pt-4">
          <div className="mb-8 pb-6 border-b border-gray-300">
            <Link to="/" onClick={() => setIsOpen(false)} className="block">
              <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                Book Price Tracker
              </h1>
              <p className="text-xs text-gray-500 mt-1">Price Monitoring Dashboard</p>
            </Link>
          </div>
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const IconComponent = item.Icon;
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    onClick={() => setIsOpen(false)}
                    className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <IconComponent
                      className={`mr-3 ${isActive ? 'text-white' : 'text-gray-600'}`}
                      size={20}
                    />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}

