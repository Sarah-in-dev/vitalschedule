import React from 'react';
import PredictiveRxTechnology from '../components/PredictiveRxTechnology';

const TechnologyOverview = () => {
  return (
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold my-6">PredictiveRx AI Technology</h1>
      <p className="mb-6 text-gray-600">
        Our unified predictive intelligence platform uses advanced machine learning to transform healthcare outcomes.
        Learn how our technology works across all our predictive modules.
      </p>
      
      <PredictiveRxTechnology />
    </div>
  );
};

export default TechnologyOverview;
