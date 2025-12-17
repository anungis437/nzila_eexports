import React from 'react';
import { TrendingDown, TrendingUp, Clock } from 'lucide-react';

interface PriceHistoryItem {
  id: number;
  old_price: string;
  new_price: string;
  price_difference: string;
  percentage_change: string;
  changed_at: string;
  is_price_drop: boolean;
}

interface PriceHistoryBadgeProps {
  priceHistory?: PriceHistoryItem[];
  currentPrice: string;
}

export const PriceHistoryBadge: React.FC<PriceHistoryBadgeProps> = ({ priceHistory }) => {
  if (!priceHistory || priceHistory.length === 0) {
    return null;
  }

  const latestChange = priceHistory[0];
  const isPriceDrop = latestChange.is_price_drop;
  const percentageChange = Math.abs(parseFloat(latestChange.percentage_change));

  // Only show badge for price drops
  if (!isPriceDrop) {
    return null;
  }

  // Calculate days since price change
  const changedDate = new Date(latestChange.changed_at);
  const today = new Date();
  const daysSince = Math.floor((today.getTime() - changedDate.getTime()) / (1000 * 60 * 60 * 24));

  // Only show if price dropped within last 7 days
  if (daysSince > 7) {
    return null;
  }

  return (
    <div className="absolute top-3 right-3 z-10">
      <div className="bg-gradient-to-r from-green-500 to-green-600 text-white px-3 py-1.5 rounded-lg shadow-lg flex items-center gap-1.5 animate-pulse">
        <TrendingDown className="h-4 w-4" />
        <span className="text-sm font-bold">
          {percentageChange.toFixed(0)}% OFF
        </span>
      </div>
      {daysSince === 0 && (
        <div className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded mt-1 text-center font-medium">
          Just dropped!
        </div>
      )}
    </div>
  );
};

interface PriceHistoryChartProps {
  vehicleId: number;
  onClose: () => void;
}

export const PriceHistoryChart: React.FC<PriceHistoryChartProps> = ({ vehicleId, onClose }) => {
  const [history, setHistory] = React.useState<PriceHistoryItem[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(
          `/api/price-history/vehicle_history/?vehicle_id=${vehicleId}`,
          { credentials: 'include' }
        );
        const data = await response.json();
        setHistory(data.history || []);
      } catch (error) {
        console.error('Failed to fetch price history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [vehicleId]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">Price History</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold">Price History</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ×
          </button>
        </div>
        <p className="text-gray-600">No price changes recorded for this vehicle.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Price History</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors text-2xl leading-none"
          aria-label="Close"
        >
          ×
        </button>
      </div>

      <div className="space-y-4">
        {history.map((item, _index) => {
          const isPriceDrop = item.is_price_drop;
          const date = new Date(item.changed_at);
          const formattedDate = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          });
          const percentage = parseFloat(item.percentage_change);

          return (
            <div
              key={item.id}
              className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex-shrink-0">
                {isPriceDrop ? (
                  <div className="bg-green-100 p-2 rounded-full">
                    <TrendingDown className="h-5 w-5 text-green-600" />
                  </div>
                ) : (
                  <div className="bg-red-100 p-2 rounded-full">
                    <TrendingUp className="h-5 w-5 text-red-600" />
                  </div>
                )}
              </div>

              <div className="flex-grow">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-gray-400 line-through text-sm">
                    ${parseFloat(item.old_price).toLocaleString()}
                  </span>
                  <span className="text-xl font-bold text-gray-900">
                    ${parseFloat(item.new_price).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="h-3 w-3" />
                  <span>{formattedDate}</span>
                </div>
              </div>

              <div className="flex-shrink-0 text-right">
                <div
                  className={`text-lg font-bold ${
                    isPriceDrop ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {isPriceDrop ? '-' : '+'}
                  {Math.abs(percentage).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">
                  ${Math.abs(parseFloat(item.price_difference)).toLocaleString()}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {history.length > 5 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">
            Showing {history.length} price change{history.length !== 1 ? 's' : ''}
          </p>
        </div>
      )}
    </div>
  );
};
