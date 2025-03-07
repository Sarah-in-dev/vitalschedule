import React from 'react';
import PredictiveAnalysis from '../components/Analytics/PredictiveAnalysis';

const Analytics = () => {
  return (
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold my-6">Advanced Predictive Analysis</h1>
      <p className="mb-6 text-gray-600">
        VitalSchedule's AI engine analyzes over 40 data points to predict no-shows and recommend 
        personalized interventions.
      </p>
      
      <PredictiveAnalysis />
    </div>
  );
};

export default Analytics;
