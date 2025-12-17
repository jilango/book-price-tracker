/** Dashboard home page. */

import { SummaryCards } from '../components/dashboard/SummaryCards';
import { PriceDistributionChart } from '../components/charts/PriceDistributionChart';
import { PriceTiersChart } from '../components/charts/PriceTiersChart';
import { BooksNeedingAttention } from '../components/dashboard/BooksNeedingAttention';

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Catalog overview and data quality insights</p>
      </div>

      <SummaryCards />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 items-start">
        <PriceDistributionChart />
        <PriceTiersChart />
      </div>

      <BooksNeedingAttention />
    </div>
  );
}

