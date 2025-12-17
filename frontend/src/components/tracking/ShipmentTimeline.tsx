import React from 'react';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { format } from 'date-fns';

interface Milestone {
  id: number;
  milestone_type: string;
  milestone_type_display: string;
  title: string;
  description: string;
  location: string;
  completed_at: string | null;
  is_completed: boolean;
  order: number;
}

interface ShipmentTimelineProps {
  milestones: Milestone[];
}

export const ShipmentTimeline: React.FC<ShipmentTimelineProps> = ({ milestones }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Shipment Progress</h2>
      
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-300" />
        
        {milestones.map((milestone, index) => (
          <div key={milestone.id} className="relative flex gap-4 mb-8 last:mb-0">
            {/* Icon */}
            <div className={`relative z-10 flex-shrink-0 ${
              milestone.is_completed
                ? 'text-green-600'
                : index === milestones.findIndex(m => !m.is_completed)
                ? 'text-blue-600'
                : 'text-gray-400'
            }`}>
              {milestone.is_completed ? (
                <CheckCircle className="w-12 h-12 bg-white" />
              ) : index === milestones.findIndex(m => !m.is_completed) ? (
                <Clock className="w-12 h-12 bg-white animate-pulse" />
              ) : (
                <Circle className="w-12 h-12 bg-white" />
              )}
            </div>
            
            {/* Content */}
            <div className="flex-1 pb-8">
              <div className={`p-4 rounded-lg border-2 ${
                milestone.is_completed
                  ? 'border-green-500 bg-green-50'
                  : index === milestones.findIndex(m => !m.is_completed)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 bg-gray-50'
              }`}>
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {milestone.title}
                    </h3>
                    <p className="text-sm text-gray-600">{milestone.milestone_type_display}</p>
                  </div>
                  {milestone.is_completed && milestone.completed_at && (
                    <span className="text-sm text-green-600 font-medium">
                      {format(new Date(milestone.completed_at), 'MMM d, yyyy HH:mm')}
                    </span>
                  )}
                </div>
                
                {milestone.description && (
                  <p className="text-gray-700 mb-2">{milestone.description}</p>
                )}
                
                {milestone.location && (
                  <p className="text-sm text-gray-600">
                    📍 {milestone.location}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
