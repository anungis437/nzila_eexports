import React, { useState } from 'react';
import { Save } from 'lucide-react';
import axios from 'axios';

interface SaveSearchButtonProps {
  currentFilters: {
    make?: string;
    model?: string;
    yearMin?: number;
    yearMax?: number;
    priceMin?: number;
    priceMax?: number;
    condition?: string;
    mileageMax?: number;
  };
  onSuccess?: () => void;
}

const SaveSearchButton: React.FC<SaveSearchButtonProps> = ({ currentFilters, onSuccess }) => {
  const [showModal, setShowModal] = useState(false);
  const [searchName, setSearchName] = useState('');
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [notificationFrequency, setNotificationFrequency] = useState<'immediate' | 'daily' | 'weekly'>('immediate');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const hasFilters = Object.values(currentFilters).some(v => v !== undefined && v !== '' && v !== null);

  const handleSave = async () => {
    if (!searchName.trim()) {
      setError('Please enter a name for this search');
      return;
    }

    setSaving(true);
    setError('');

    try {
      await axios.post(
        '/api/saved-searches/',
        {
          name: searchName,
          make: currentFilters.make || null,
          model: currentFilters.model || null,
          year_min: currentFilters.yearMin || null,
          year_max: currentFilters.yearMax || null,
          price_min: currentFilters.priceMin || null,
          price_max: currentFilters.priceMax || null,
          condition: currentFilters.condition || null,
          mileage_max: currentFilters.mileageMax || null,
          email_notifications: emailNotifications,
          notification_frequency: notificationFrequency,
        },
        { withCredentials: true }
      );

      setShowModal(false);
      setSearchName('');
      onSuccess?.();
      
      // Show success message
      alert('Search saved successfully! You\'ll receive notifications when new matching vehicles arrive.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save search');
    } finally {
      setSaving(false);
    }
  };

  const getCriteriaDisplay = () => {
    const criteria: string[] = [];
    if (currentFilters.make) criteria.push(`${currentFilters.make}`);
    if (currentFilters.model) criteria.push(`${currentFilters.model}`);
    if (currentFilters.yearMin || currentFilters.yearMax) {
      if (currentFilters.yearMin && currentFilters.yearMax) {
        criteria.push(`${currentFilters.yearMin}-${currentFilters.yearMax}`);
      } else if (currentFilters.yearMin) {
        criteria.push(`${currentFilters.yearMin}+`);
      } else {
        criteria.push(`up to ${currentFilters.yearMax}`);
      }
    }
    if (currentFilters.priceMin || currentFilters.priceMax) {
      if (currentFilters.priceMin && currentFilters.priceMax) {
        criteria.push(`$${currentFilters.priceMin.toLocaleString()}-$${currentFilters.priceMax.toLocaleString()}`);
      } else if (currentFilters.priceMin) {
        criteria.push(`$${currentFilters.priceMin.toLocaleString()}+`);
      } else if (currentFilters.priceMax) {
        criteria.push(`up to $${currentFilters.priceMax.toLocaleString()}`);
      }
    }
    if (currentFilters.condition) criteria.push(currentFilters.condition);
    
    return criteria.join(' • ') || 'All vehicles';
  };

  if (!hasFilters) {
    return (
      <button
        disabled
        className="px-4 py-2 bg-slate-100 text-slate-400 rounded-lg cursor-not-allowed flex items-center gap-2"
        title="Apply filters to save a search"
      >
        <Save className="w-5 h-5" />
        Save Search
      </button>
    );
  }

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition flex items-center gap-2"
      >
        <Save className="w-5 h-5" />
        Save Search
      </button>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">
              Save This Search
            </h2>

            {/* Current Criteria */}
            <div className="mb-4 p-4 bg-slate-50 rounded-lg">
              <p className="text-sm font-medium text-slate-700 mb-1">Search Criteria:</p>
              <p className="text-sm text-slate-600">{getCriteriaDisplay()}</p>
            </div>

            {/* Name Input */}
            <div className="mb-4">
              <label htmlFor="search-name" className="block text-sm font-medium text-slate-700 mb-2">
                Search Name <span className="text-red-500">*</span>
              </label>
              <input
                id="search-name"
                type="text"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="e.g., Toyota Camry under $15k"
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                autoFocus
              />
            </div>

            {/* Email Notifications */}
            <div className="mb-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  className="w-4 h-4 text-primary-600 border-slate-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm text-slate-700">
                  Send email notifications for new matches
                </span>
              </label>
            </div>

            {/* Notification Frequency */}
            {emailNotifications && (
              <div className="mb-4">
                <label htmlFor="notification-frequency" className="block text-sm font-medium text-slate-700 mb-2">
                  Notification Frequency
                </label>
                <select
                  id="notification-frequency"
                  value={notificationFrequency}
                  onChange={(e) => setNotificationFrequency(e.target.value as any)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  aria-label="Notification frequency"
                >
                  <option value="immediate">Immediate (as vehicles are added)</option>
                  <option value="daily">Daily Digest</option>
                  <option value="weekly">Weekly Digest</option>
                </select>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition"
                disabled={saving}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !searchName.trim()}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:bg-slate-300 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save Search'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SaveSearchButton;
