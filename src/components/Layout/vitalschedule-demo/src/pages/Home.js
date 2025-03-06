import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">VitalSchedule Demo</h1>
      <p className="mb-8 text-gray-600">
        Interactive demonstration of VitalSchedule's predictive no-show analytics for Community Health Centers
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/dashboard" className="p-6 bg-blue-50 rounded-lg shadow hover:shadow-md transition">
          <h2 className="text-xl font-bold text-blue-700 mb-2">Operational Dashboard</h2>
          <p className="text-gray-600">Daily operational view for staff with risk assessment and intervention tracking</p>
        </Link>
        
        <Link to="/analytics" className="p-6 bg-purple-50 rounded-lg shadow hover:shadow-md transition">
          <h2 className="text-xl font-bold text-purple-700 mb-2">Predictive Analysis</h2>
          <p className="text-gray-600">Advanced AI capabilities showing risk factors and intervention strategies</p>
        </Link>
        
        <Link to="/roi" className="p-6 bg-green-50 rounded-lg shadow hover:shadow-md transition">
          <h2 className="text-xl font-bold text-green-700 mb-2">ROI Calculator</h2>
          <p className="text-gray-600">Financial impact analysis with detailed benefits breakdown</p>
        </Link>
      </div>
      
      <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-2">About VitalSchedule</h2>
        <p className="text-gray-600 mb-4">
          VitalSchedule is a predictive analytics solution designed to reduce patient no-shows in Community Health Centers. By analyzing over 40 data points, VitalSchedule identifies at-risk appointments and recommends targeted interventions, resulting in a 25-35% reduction in no-shows.
        </p>
        <ul className="list-disc pl-5 text-gray-600 space-y-1">
          <li>Predict which appointments are at risk of becoming no-shows</li>
          <li>Recommend personalized interventions based on specific risk factors</li>
          <li>Track intervention effectiveness and ROI in real-time</li>
          <li>Integrate seamlessly with existing EHR systems</li>
        </ul>
      </div>
    </div>
  );
};

export default Home;
