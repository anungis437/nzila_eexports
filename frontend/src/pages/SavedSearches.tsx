import React, { useState, useEffect } from 'react';
import { Search, Plus, Bell, BellOff, Trash2, Eye } from 'lucide-react';
import axios from 'axios';

interface SavedSearch {
  id: number;
  name: string;
  criteria_display: string;
  match_count: number;
  is_active: boolean;
  email_notifications: boolean;
  notification_frequency: string;
  created_at: string;
}

const SavedSearches: React.FC = () => {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchSavedSearches();
  }, []);

  const fetchSavedSearches = async () => {
    try {
      const response = await axios.get('/api/saved-searches/', {
        withCredentials: true,
      });
      setSearches(response.data);
    } catch (error) {
      console.error('Error fetching saved searches:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (searchId: number) => {
    try {
      const response = await axios.post(
        `/api/saved-searches/${searchId}/toggle-active/`,
        {},
        { withCredentials: true }
      );
      setSearches(searches.map(s => s.id === searchId ? response.data : s));
    } catch (error) {
      console.error('Error toggling search:', error);
    }
  };

  const deleteSearch = async (searchId: number) => {
    if (!confirm('Are you sure you want to delete this saved search?')) return;

    try {
      await axios.delete(`/api/saved-searches/${searchId}/`, {
        withCredentials: true,
      });
      setSearches(searches.filter(s => s.id !== searchId));
    } catch (error) {
      console.error('Error deleting search:', error);
    }
  };

  const filteredSearches = searches.filter(search =>
    search.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    search.criteria_display.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Saved Searches
          </h1>
          <p className="text-slate-600">
            Manage your saved searches and get notified when new matching vehicles arrive
          </p>
        </div>

        {/* Search Bar and Create Button */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search saved searches..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              aria-label="Search saved searches"
            />
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition whitespace-nowrap"
          >
            <Plus className="w-5 h-5" />
            Create New Search
          </button>
        </div>

        {/* Saved Searches Grid */}
        {filteredSearches.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              {searchQuery ? 'No matching searches' : 'No saved searches yet'}
            </h3>
            <p className="text-slate-600 mb-6">
              {searchQuery
                ? 'Try adjusting your search query'
                : 'Create your first saved search to get notifications about new vehicles'}
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
              >
                <Plus className="w-5 h-5" />
                Create Saved Search
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSearches.map((search) => (
              <div
                key={search.id}
                className="bg-white border border-slate-200 rounded-lg p-6 hover:shadow-lg transition"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900 flex-1">
                    {search.name}
                  </h3>
                  <div className="flex items-center gap-2">
                    {search.email_notifications ? (
                      <Bell className="w-5 h-5 text-primary-600" aria-label="Notifications enabled" />
                    ) : (
                      <BellOff className="w-5 h-5 text-slate-400" aria-label="Notifications disabled" />
                    )}
                  </div>
                </div>

                {/* Criteria */}
                <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                  {search.criteria_display}
                </p>

                {/* Match Count */}
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-100">
                  <span className="text-sm font-medium text-slate-700">
                    {search.match_count} {search.match_count === 1 ? 'match' : 'matches'}
                  </span>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      search.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {search.is_active ? 'Active' : 'Paused'}
                  </span>
                </div>

                {/* Notification Frequency */}
                {search.email_notifications && (
                  <p className="text-xs text-slate-500 mb-4">
                    📧 {search.notification_frequency.charAt(0).toUpperCase() + search.notification_frequency.slice(1)} notifications
                  </p>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => window.location.href = `/buyer-portal?search=${search.id}`}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition text-sm font-medium"
                  >
                    <Eye className="w-4 h-4" />
                    View Matches
                  </button>
                  <button
                    onClick={() => toggleActive(search.id)}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition"
                    title={search.is_active ? 'Pause notifications' : 'Resume notifications'}
                    aria-label={search.is_active ? 'Pause notifications' : 'Resume notifications'}
                  >
                    {search.is_active ? <BellOff className="w-5 h-5" /> : <Bell className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={() => deleteSearch(search.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                    title="Delete search"
                    aria-label="Delete search"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            How Saved Searches Work
          </h3>
          <ul className="space-y-2 text-blue-800">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">•</span>
              <span>Save your search criteria and we'll automatically notify you when new matching vehicles arrive</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">•</span>
              <span>Choose between immediate, daily, or weekly notification digests</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">•</span>
              <span>Pause or delete searches anytime without losing your preferences</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">•</span>
              <span>Click "View Matches" to see all vehicles matching your criteria</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SavedSearches;
