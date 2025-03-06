import React from 'react';
import OperationalDashboard from '../components/Dashboard/OperationalDashboard';

const Dashboard = () => {
  return (
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold my-6">Operational Dashboard</h1>
      <p className="mb-6 text-gray-600">
        The VitalSchedule operational dashboard provides staff with real-time risk assessment 
        and actionable intervention recommendations.
      </p>
      
      <OperationalDashboard />
    </div>
  );
};

export default Dashboard;
