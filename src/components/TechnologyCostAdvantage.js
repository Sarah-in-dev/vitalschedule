import React from 'react';

const TechnologyCostAdvantage = () => {
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">VitalSchedule Technology Cost Advantage</h2>
      
      {/* Architecture Comparison */}
      <div className="mb-10 bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-medium text-gray-700 mb-4">Architecture Advantage</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Traditional Approach */}
          <div className="border border-red-200 rounded-lg p-4">
            <h4 className="text-lg font-medium text-red-700 mb-3">Traditional ML Approach</h4>
            <div className="bg-red-50 p-4 rounded-lg mb-4 h-48 flex flex-col justify-between">
              <div className="border-b border-red-200 p-2 text-center">Custom Data Processing</div>
              <div className="border-b border-red-200 p-2 text-center">Client-Specific Models</div>
              <div className="border-b border-red-200 p-2 text-center">Custom Integration Layer</div>
              <div className="p-2 text-center">Unique User Interface</div>
            </div>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-red-500 mr-2">✖</span>
                <span>Requires rebuilding components for each client</span>
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">✖</span>
                <span>Limited knowledge transfer between implementations</span>
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">✖</span>
                <span>High maintenance burden for each client</span>
              </li>
            </ul>
          </div>
          
          {/* VitalSchedule Approach */}
          <div className="border border-green-200 rounded-lg p-4">
            <h4 className="text-lg font-medium text-green-700 mb-3">VitalSchedule Approach</h4>
            <div className="bg-green-50 p-4 rounded-lg mb-4 h-48 flex flex-col justify-between">
              <div className="border-b border-green-200 p-2 text-center">Shared Data Processing Engine</div>
              <div className="border-b border-green-200 p-2 text-center">Transfer Learning Models + Client Fine-Tuning</div>
              <div className="border-b border-green-200 p-2 text-center">Pre-Built EHR Connectors</div>
              <div className="p-2 text-center">Configurable UI Components</div>
            </div>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>80% reusable components across all clients</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Models improve with each implementation</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Centralized maintenance and updates</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Cost Comparison */}
      <div className="mb-10 bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-medium text-gray-700 mb-4">Implementation Cost Comparison</h3>
        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                Development Cost
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold inline-block text-blue-600">
                Savings: 40-60%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-8 mb-4 text-xs flex rounded-full">
            <div style={{ width: "100%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-red-500 relative">
              <div className="absolute inset-0 flex items-center justify-center text-white font-semibold">
                Custom ML Implementation: $1.2M - $1.8M
              </div>
            </div>
          </div>
          <div className="overflow-hidden h-8 mb-4 text-xs flex rounded-full">
            <div style={{ width: "45%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500">
              <span className="text-white font-semibold">VitalSchedule: $550K - $750K</span>
            </div>
            <div style={{ width: "55%" }} className="shadow-none flex flex-col text-center whitespace-nowrap justify-center bg-gray-200">
            </div>
          </div>
        </div>
        
        <div className="relative pt-1 mt-8">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                Annual Maintenance Cost
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold inline-block text-blue-600">
                Savings: 50-70%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-8 mb-4 text-xs flex rounded-full">
            <div style={{ width: "100%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-red-500 relative">
              <div className="absolute inset-0 flex items-center justify-center text-white font-semibold">
                Custom Solution Maintenance: $300K - $450K annually
              </div>
            </div>
          </div>
          <div className="overflow-hidden h-8 mb-4 text-xs flex rounded-full">
            <div style={{ width: "30%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500">
              <span className="text-white font-semibold">VitalSchedule: $95K - $125K annually</span>
            </div>
            <div style={{ width: "70%" }} className="shadow-none flex flex-col text-center whitespace-nowrap justify-center bg-gray-200">
            </div>
          </div>
        </div>
      </div>
      
      {/* Cost Efficiency Drivers */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-medium text-gray-700 mb-4">How We Maintain Cost Efficiency</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="border border-blue-100 rounded-lg p-4 bg-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Transfer Learning</h4>
            <p className="text-sm text-gray-600">Our models start with healthcare-specific pre-training, requiring 70% less client data for accurate predictions.</p>
          </div>
          <div className="border border-blue-100 rounded-lg p-4 bg-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Pre-Built Connectors</h4>
            <p className="text-sm text-gray-600">Ready-made integrations for major EHR systems eliminate 8-12 weeks of custom development work.</p>
          </div>
          <div className="border border-blue-100 rounded-lg p-4 bg-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Multi-Tenant Architecture</h4>
            <p className="text-sm text-gray-600">Shared infrastructure and distributed R&D costs reduce per-client expense by 65% at scale.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnologyCostAdvantage;
