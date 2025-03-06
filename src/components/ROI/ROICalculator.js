import React, { useState } from 'react';

const ROICalculator = () => {
  const [centerSize, setCenterSize] = useState('medium');
  const [annualVisits, setAnnualVisits] = useState(50000);
  const [noShowRate, setNoShowRate] = useState(25);
  const [revenuePerVisit, setRevenuePerVisit] = useState(150);
  const [expectedReduction, setExpectedReduction] = useState(30);
  
  // Calculate metrics
  const appointmentsSaved = Math.round(annualVisits * (noShowRate/100) * (expectedReduction/100));
  const directRevenue = appointmentsSaved * revenuePerVisit;
  const totalBenefit = directRevenue * 2.2; // Factor in other benefits
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-medium mb-4">ROI Calculator</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Center Size
            </label>
            <select
              value={centerSize}
              onChange={(e) => setCenterSize(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="small">Small (25,000 annual visits)</option>
              <option value="medium">Medium (50,000 annual visits)</option>
              <option value="large">Large (100,000 annual visits)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current No-Show Rate (%)
            </label>
            <input
              type="number"
              value={noShowRate}
              onChange={(e) => setNoShowRate(Number(e.target.value))}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Revenue Per Visit ($)
            </label>
            <input
              type="number"
              value={revenuePerVisit}
              onChange={(e) => setRevenuePerVisit(Number(e.target.value))}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expected No-Show Reduction (%)
            </label>
            <input
              type="number"
              value={expectedReduction}
              onChange={(e) => setExpectedReduction(Number(e.target.value))}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium mb-3">ROI Summary</h3>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>Appointments Saved:</span>
              <span className="font-bold">{appointmentsSaved}</span>
            </div>
            
            <div className="flex justify-between">
              <span>Direct Revenue Recovery:</span>
              <span className="font-bold">${directRevenue.toLocaleString()}</span>
            </div>
            
            <div className="flex justify-between">
              <span>Total Annual Benefit:</span>
              <span className="font-bold">${totalBenefit.toLocaleString()}</span>
            </div>
            
            <div className="flex justify-between pt-2 border-t">
              <span>5-Year ROI:</span>
              <span className="font-bold text-green-600">430%</span>
            </div>
            
            <div className="flex justify-between">
              <span>Payback Period:</span>
              <span className="font-bold">18 months</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ROICalculator;
