import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import TierDashboard from '@/components/TierDashboard';
import Leaderboard from '@/components/Leaderboard';
import { useAuth } from '@/contexts/AuthContext';

const CommissionsPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');

  // Determine if user is broker or dealer
  const userType = user?.role === 'broker' ? 'broker' : 'dealer';

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Commission Center</h1>
        <p className="text-gray-600 mt-2">
          Track your performance, earnings, and see how you stack up against top performers
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="dashboard">My Dashboard</TabsTrigger>
          <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          <TierDashboard />
        </TabsContent>

        <TabsContent value="leaderboard" className="space-y-6">
          <Leaderboard userType={userType} />
        </TabsContent>
      </Tabs>

      {/* Info Section */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
          <h3 className="text-lg font-bold text-blue-900 mb-3">
            {userType === 'broker' ? '📊 Broker Tier System' : '🚗 Dealer Tier System'}
          </h3>
          {userType === 'broker' ? (
            <div className="space-y-2 text-sm text-blue-800">
              <p><strong>Starter (0-4 deals/month):</strong> 3.0% commission</p>
              <p><strong>Bronze (5-9 deals/month):</strong> 3.5% commission</p>
              <p><strong>Silver (10-19 deals/month):</strong> 4.0% commission</p>
              <p><strong>Gold (20-39 deals/month):</strong> 4.5% commission</p>
              <p><strong>Platinum (40-79 deals/month):</strong> 5.0% commission</p>
              <p><strong>Diamond (80+ deals/month):</strong> 5.5% commission + perks</p>
              <p className="mt-3 font-semibold">🔥 Bonus: Active streak tracking & achievement boosts!</p>
            </div>
          ) : (
            <div className="space-y-2 text-sm text-blue-800">
              <p><strong>Standard (0-9 deals/quarter):</strong> 5.0% commission</p>
              <p><strong>Preferred (10-24 deals/quarter):</strong> 5.5% commission</p>
              <p><strong>Elite (25-49 deals/quarter):</strong> 6.0% commission</p>
              <p><strong>Premier (50+ deals/quarter):</strong> 6.5% commission</p>
              <p className="mt-3 font-semibold">🍁 Canadian Bonuses Available!</p>
            </div>
          )}
        </div>

        {userType === 'dealer' && (
          <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
            <h3 className="text-lg font-bold text-purple-900 mb-3">🍁 Canadian Market Bonuses</h3>
            <div className="space-y-2 text-sm text-purple-800">
              <p><strong>Provincial Bonus (+0.5%):</strong> ON, QC, BC, AB, SK, MB</p>
              <p><strong>Maritime Bonus (+0.75%):</strong> NB, NS, PE, NL (smaller markets)</p>
              <p><strong>Rural Dealer (+1.0%):</strong> Outside major cities</p>
              <p><strong>First Nations Partnership (+1.5%):</strong> Indigenous partnerships</p>
              <p className="mt-3 font-semibold bg-purple-200 p-2 rounded">
                💎 Maximum Rate: 8.5% (Premier + First Nations)
              </p>
              <p className="mt-3 text-xs">
                🎁 <strong>Onboarding Bonuses:</strong> $500 welcome + $1,000 first deal + $2,500 fast start (5 deals in 30 days)
              </p>
            </div>
          </div>
        )}

        {userType === 'broker' && (
          <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
            <h3 className="text-lg font-bold text-green-900 mb-3">💰 Maximize Your Earnings</h3>
            <div className="space-y-2 text-sm text-green-800">
              <p><strong>Consistency Pays:</strong> Maintain deal streaks for achievement boosts</p>
              <p><strong>Volume Matters:</strong> Higher tiers unlock better rates automatically</p>
              <p><strong>Quality Deals:</strong> Higher deal values increase average metrics</p>
              <p className="mt-3 font-semibold">
                📈 Top brokers earn 83% more than starting rate!
              </p>
              <p className="text-xs mt-2">
                Diamond tier (5.5%) vs Starter (3%) = $2,500 extra per $100K deal
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommissionsPage;
