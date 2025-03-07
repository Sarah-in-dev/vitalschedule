import React from 'react';
import ROICalculator from '../components/ROI/ROICalculator';

const ROI = () => {
  return (
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold my-6">ROI Calculator</h1>
      <p className="mb-6 text-gray-600">
        Estimate the financial impact of reducing no-shows at your Community Health Center.
      </p>
      
      <ROICalculator />
    </div>
  );
};

export default ROI;
