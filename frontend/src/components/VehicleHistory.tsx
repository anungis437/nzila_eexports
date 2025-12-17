import React from 'react';
import {
  Shield, ShieldCheck, ShieldAlert, AlertTriangle, Users, Wrench,
  AlertCircle, CheckCircle, XCircle
} from 'lucide-react';
import axios from 'axios';

interface AccidentRecord {
  id: number;
  accident_date: string;
  damage_severity: string;
  damage_areas: string[];
  repair_cost: number | null;
  insurance_claim: boolean;
  description: string;
}

interface ServiceRecord {
  id: number;
  service_date: string;
  service_type: string;
  service_type_display: string;
  odometer_reading: number;
  service_cost: number | null;
}

interface OwnershipRecord {
  id: number;
  owner_number: number;
  ownership_start: string;
  ownership_end: string | null;
  ownership_type: string;
  ownership_type_display: string;
  state_province: string;
}

interface VehicleHistoryReport {
  id: number;
  vehicle_vin: string;
  vehicle_make: string;
  vehicle_model: string;
  vehicle_year: number;
  title_status: string;
  title_status_display: string;
  accident_severity: string;
  total_accidents: number;
  total_owners: number;
  trust_score: number;
  is_clean_title: boolean;
  has_accidents: boolean;
  is_one_owner: boolean;
  odometer_rollback: boolean;
  odometer_verified: boolean;
  structural_damage: boolean;
  frame_damage: boolean;
  airbag_deployment: boolean;
  recalls_outstanding: number;
  total_service_records: number;
  accident_records: AccidentRecord[];
  service_records: ServiceRecord[];
  ownership_records: OwnershipRecord[];
  report_confidence: string;
}

interface VehicleHistoryProps {
  vehicleId: number;
  language: 'en' | 'fr';
}

export const VehicleHistory: React.FC<VehicleHistoryProps> = ({ vehicleId, language }) => {
  const [report, setReport] = React.useState<VehicleHistoryReport | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/vehicle-history/reports/by-vehicle/${vehicleId}/`);
        setReport(response.data);
        setError(null);
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError(language === 'fr' ? 'Aucun rapport d\'historique disponible' : 'No history report available');
        } else {
          setError(language === 'fr' ? 'Erreur de chargement' : 'Failed to load history');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [vehicleId, language]);

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  // Trust score color
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return language === 'fr' ? 'Excellent' : 'Excellent';
    if (score >= 60) return language === 'fr' ? 'Bon' : 'Good';
    if (score >= 40) return language === 'fr' ? 'Moyen' : 'Fair';
    return language === 'fr' ? 'Faible' : 'Poor';
  };

  return (
    <div className="space-y-6">
      {/* Header with Trust Score */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-6 h-6" />
              <h2 className="text-2xl font-bold">
                {language === 'fr' ? 'Rapport d\'historique' : 'Vehicle History Report'}
              </h2>
            </div>
            <p className="text-blue-100">
              {report.vehicle_year} {report.vehicle_make} {report.vehicle_model} • VIN: {report.vehicle_vin}
            </p>
          </div>
          <div className="text-center">
            <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white ${getScoreColor(report.trust_score)} font-bold text-xl`}>
              {report.trust_score}/100
            </div>
            <p className="text-sm text-blue-100 mt-1">{getScoreLabel(report.trust_score)}</p>
          </div>
        </div>
      </div>

      {/* Quick Facts Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Title Status */}
        <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            {report.is_clean_title ? (
              <ShieldCheck className="w-5 h-5 text-green-600" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-red-600" />
            )}
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Titre' : 'Title'}
            </span>
          </div>
          <p className={`font-semibold ${report.is_clean_title ? 'text-green-600' : 'text-red-600'}`}>
            {report.title_status_display}
          </p>
        </div>

        {/* Accidents */}
        <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-gray-600" />
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Accidents' : 'Accidents'}
            </span>
          </div>
          <p className={`font-semibold ${report.has_accidents ? 'text-orange-600' : 'text-green-600'}`}>
            {report.total_accidents === 0
              ? (language === 'fr' ? 'Aucun' : 'None')
              : `${report.total_accidents} ${language === 'fr' ? 'signalé(s)' : 'reported'}`
            }
          </p>
        </div>

        {/* Owners */}
        <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-gray-600" />
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Propriétaires' : 'Owners'}
            </span>
          </div>
          <p className={`font-semibold ${report.is_one_owner ? 'text-green-600' : 'text-gray-900'}`}>
            {report.total_owners} {report.total_owners === 1 ? (language === 'fr' ? 'propriétaire' : 'owner') : (language === 'fr' ? 'propriétaires' : 'owners')}
          </p>
        </div>

        {/* Service Records */}
        <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Wrench className="w-5 h-5 text-gray-600" />
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Entretien' : 'Service'}
            </span>
          </div>
          <p className="font-semibold text-gray-900">
            {report.total_service_records} {language === 'fr' ? 'dossiers' : 'records'}
          </p>
        </div>
      </div>

      {/* Red Flags (if any) */}
      {(report.odometer_rollback || report.structural_damage || report.frame_damage || report.recalls_outstanding > 0) && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h3 className="font-semibold text-red-900">
              {language === 'fr' ? 'Alertes importantes' : 'Important Alerts'}
            </h3>
          </div>
          <ul className="space-y-2">
            {report.odometer_rollback && (
              <li className="flex items-center gap-2 text-red-800">
                <XCircle className="w-4 h-4" />
                {language === 'fr' ? 'Retour de compteur kilométrique détecté' : 'Odometer rollback detected'}
              </li>
            )}
            {report.structural_damage && (
              <li className="flex items-center gap-2 text-red-800">
                <XCircle className="w-4 h-4" />
                {language === 'fr' ? 'Dommages structurels signalés' : 'Structural damage reported'}
              </li>
            )}
            {report.frame_damage && (
              <li className="flex items-center gap-2 text-red-800">
                <XCircle className="w-4 h-4" />
                {language === 'fr' ? 'Dommages au châssis signalés' : 'Frame damage reported'}
              </li>
            )}
            {report.recalls_outstanding > 0 && (
              <li className="flex items-center gap-2 text-red-800">
                <XCircle className="w-4 h-4" />
                {report.recalls_outstanding} {language === 'fr' ? 'rappels en attente' : 'outstanding recalls'}
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Green Checkmarks */}
      {(report.is_clean_title && !report.has_accidents && report.is_one_owner && report.odometer_verified) && (
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {report.is_clean_title && (
              <li className="flex items-center gap-2 text-green-800">
                <CheckCircle className="w-4 h-4" />
                {language === 'fr' ? 'Titre propre' : 'Clean title'}
              </li>
            )}
            {!report.has_accidents && (
              <li className="flex items-center gap-2 text-green-800">
                <CheckCircle className="w-4 h-4" />
                {language === 'fr' ? 'Aucun accident signalé' : 'No accidents reported'}
              </li>
            )}
            {report.is_one_owner && (
              <li className="flex items-center gap-2 text-green-800">
                <CheckCircle className="w-4 h-4" />
                {language === 'fr' ? 'Un seul propriétaire' : 'One owner'}
              </li>
            )}
            {report.odometer_verified && (
              <li className="flex items-center gap-2 text-green-800">
                <CheckCircle className="w-4 h-4" />
                {language === 'fr' ? 'Compteur vérifié' : 'Odometer verified'}
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Accident History Timeline */}
      {report.accident_records.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            {language === 'fr' ? 'Historique des accidents' : 'Accident History'}
          </h3>
          <div className="space-y-4">
            {report.accident_records.map((accident) => (
              <div key={accident.id} className="border-l-4 border-orange-300 pl-4 py-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">
                    {new Date(accident.accident_date).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    accident.damage_severity === 'severe' ? 'bg-red-100 text-red-800' :
                    accident.damage_severity === 'moderate' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {accident.damage_severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {language === 'fr' ? 'Zones endommagées' : 'Damage areas'}: {accident.damage_areas.join(', ')}
                </p>
                {accident.repair_cost && (
                  <p className="text-sm text-gray-600 mt-1">
                    {language === 'fr' ? 'Coût de réparation' : 'Repair cost'}: ${accident.repair_cost.toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Service History */}
      {report.service_records.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-blue-600" />
            {language === 'fr' ? 'Historique d\'entretien' : 'Service History'}
          </h3>
          <div className="space-y-3">
            {report.service_records.slice(0, 5).map((service) => (
              <div key={service.id} className="flex items-center justify-between py-2 border-b border-gray-100">
                <div>
                  <p className="font-medium text-gray-900">{service.service_type_display}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(service.service_date).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-US')} •{' '}
                    {service.odometer_reading.toLocaleString()} {language === 'fr' ? 'km' : 'mi'}
                  </p>
                </div>
                {service.service_cost && (
                  <span className="text-gray-700 font-medium">${service.service_cost.toLocaleString()}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Ownership Timeline */}
      {report.ownership_records.length > 0 && (
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-600" />
            {language === 'fr' ? 'Historique de propriété' : 'Ownership History'}
          </h3>
          <div className="space-y-4">
            {report.ownership_records.map((ownership) => (
              <div key={ownership.id} className="border-l-4 border-purple-300 pl-4 py-2">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-gray-900">
                    {language === 'fr' ? 'Propriétaire' : 'Owner'} #{ownership.owner_number}
                  </span>
                  <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs">
                    {ownership.ownership_type_display}
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {new Date(ownership.ownership_start).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-US')} -{' '}
                  {ownership.ownership_end 
                    ? new Date(ownership.ownership_end).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-US')
                    : (language === 'fr' ? 'Présent' : 'Present')
                  }
                </p>
                {ownership.state_province && (
                  <p className="text-sm text-gray-600">{ownership.state_province}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Badge component for vehicle cards
export const HistoryBadge: React.FC<{ report: { trust_score: number; is_clean_title: boolean; has_accidents: boolean } }> = ({ report }) => {
  const getColor = () => {
    if (report.trust_score >= 80) return 'bg-green-100 text-green-800';
    if (report.trust_score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getColor()}`}>
      <Shield className="w-3 h-3" />
      Score: {report.trust_score}/100
    </div>
  );
};
