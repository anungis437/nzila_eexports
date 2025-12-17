import React from 'react';
import { Clock, X, Search } from 'lucide-react';

interface SearchHistoryItem {
  id: string;
  query: string;
  filters: {
    make?: string;
    year?: string;
    condition?: string;
    fuelType?: string;
    drivetrain?: string;
    engineType?: string;
  };
  timestamp: number;
}

interface SearchHistoryProps {
  onApplySearch: (item: SearchHistoryItem) => void;
  language: 'en' | 'fr';
}

export const SearchHistory: React.FC<SearchHistoryProps> = ({ onApplySearch, language }) => {
  const [history, setHistory] = React.useState<SearchHistoryItem[]>([]);
  const [isOpen, setIsOpen] = React.useState(false);

  // Load search history from localStorage
  React.useEffect(() => {
    const saved = localStorage.getItem('searchHistory');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setHistory(parsed);
      } catch (e) {
        console.error('Failed to load search history', e);
      }
    }
  }, []);

  // Clear all history
  const clearHistory = () => {
    localStorage.removeItem('searchHistory');
    setHistory([]);
    setIsOpen(false);
  };

  // Remove single history item
  const removeItem = (id: string) => {
    const updated = history.filter((item) => item.id !== id);
    setHistory(updated);
    localStorage.setItem('searchHistory', JSON.stringify(updated));
  };

  // Format timestamp
  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return language === 'fr' ? 'À l\'instant' : 'Just now';
    if (diffMins < 60) return language === 'fr' ? `Il y a ${diffMins} min` : `${diffMins} min ago`;
    if (diffHours < 24) return language === 'fr' ? `Il y a ${diffHours}h` : `${diffHours}h ago`;
    if (diffDays < 7) return language === 'fr' ? `Il y a ${diffDays}j` : `${diffDays}d ago`;
    return date.toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  // Format search description
  const formatDescription = (item: SearchHistoryItem) => {
    const parts: string[] = [];
    
    if (item.query) {
      parts.push(`"${item.query}"`);
    }
    
    if (item.filters.make) {
      parts.push(item.filters.make);
    }
    
    if (item.filters.year) {
      parts.push(item.filters.year);
    }
    
    if (item.filters.condition) {
      const conditionLabels: any = {
        new: language === 'fr' ? 'Neuf' : 'New',
        used_excellent: language === 'fr' ? 'Excellent' : 'Excellent',
        used_good: language === 'fr' ? 'Bon' : 'Good',
        used_fair: language === 'fr' ? 'Acceptable' : 'Fair',
      };
      parts.push(conditionLabels[item.filters.condition] || item.filters.condition);
    }

    if (item.filters.fuelType) {
      const fuelLabels: any = {
        gasoline: language === 'fr' ? 'Essence' : 'Gasoline',
        diesel: 'Diesel',
        electric: language === 'fr' ? 'Électrique' : 'Electric',
        hybrid: language === 'fr' ? 'Hybride' : 'Hybrid',
      };
      parts.push(fuelLabels[item.filters.fuelType] || item.filters.fuelType);
    }

    if (item.filters.drivetrain) {
      parts.push(item.filters.drivetrain.toUpperCase());
    }

    if (item.filters.engineType) {
      parts.push(item.filters.engineType);
    }

    return parts.length > 0 
      ? parts.join(' • ') 
      : (language === 'fr' ? 'Tous les véhicules' : 'All vehicles');
  };

  if (history.length === 0) {
    return null;
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
        aria-label={language === 'fr' ? 'Historique de recherche' : 'Search history'}
      >
        <Clock className="w-4 h-4" />
        <span>
          {language === 'fr' ? 'Historique' : 'History'} ({history.length})
        </span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">
                {language === 'fr' ? 'Recherches récentes' : 'Recent Searches'}
              </h3>
              <button
                onClick={clearHistory}
                className="text-xs text-red-600 hover:text-red-700 font-medium"
              >
                {language === 'fr' ? 'Effacer tout' : 'Clear all'}
              </button>
            </div>

            {/* History Items */}
            <div className="divide-y divide-gray-100">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="p-3 hover:bg-gray-50 transition-colors group"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      <Search className="w-4 h-4 text-gray-400" />
                    </div>
                    
                    <div
                      onClick={() => {
                        onApplySearch(item);
                        setIsOpen(false);
                      }}
                      className="flex-grow cursor-pointer"
                    >
                      <p className="text-sm text-gray-900 font-medium mb-1">
                        {formatDescription(item)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatTimestamp(item.timestamp)}
                      </p>
                    </div>

                    <button
                      onClick={() => removeItem(item.id)}
                      className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      aria-label={language === 'fr' ? 'Supprimer' : 'Remove'}
                    >
                      <X className="w-4 h-4 text-gray-400 hover:text-red-600" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Helper function to save search to history
export const saveSearchToHistory = (
  query: string,
  filters: {
    make?: string;
    year?: string;
    condition?: string;
    fuelType?: string;
    drivetrain?: string;
    engineType?: string;
  }
) => {
  // Don't save if no search criteria
  if (!query && !filters.make && !filters.year && !filters.condition && !filters.fuelType && !filters.drivetrain && !filters.engineType) {
    return;
  }

  const saved = localStorage.getItem('searchHistory');
  let history: SearchHistoryItem[] = [];
  
  if (saved) {
    try {
      history = JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse search history', e);
    }
  }

  // Create new history item
  const newItem: SearchHistoryItem = {
    id: Date.now().toString(),
    query,
    filters,
    timestamp: Date.now(),
  };

  // Check if identical search already exists (avoid duplicates)
  const isDuplicate = history.some(
    (item) =>
      item.query === query &&
      JSON.stringify(item.filters) === JSON.stringify(filters)
  );

  if (!isDuplicate) {
    // Add to beginning of array
    history.unshift(newItem);
    
    // Keep only last 10 searches
    history = history.slice(0, 10);
    
    // Save to localStorage
    localStorage.setItem('searchHistory', JSON.stringify(history));
  }
};
