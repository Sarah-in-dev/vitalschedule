import React from 'react';
import SimpleExplainableAI from '../components/SimpleExplainableAI';

const ExplainableAI = () => {
  return (
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold my-6">Explainable AI Technology</h1>
      <p className="mb-6 text-gray-600">
        Unlike "black box" AI systems, PredictiveRx's technology makes its reasoning transparent and understandable.
        Explore how our system explains its predictions and recommendations.
      </p>
      
      <SimpleExplainableAI />
    </div>
  );
};

export default ExplainableAI;
