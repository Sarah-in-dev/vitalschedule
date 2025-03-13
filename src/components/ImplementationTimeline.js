import React from 'react';

const ImplementationTimeline = () => {
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Implementation Timeline Advantage</h2>
      
      <div className="bg-white p-6 rounded-lg shadow mb-10">
        <h3 className="text-xl font-medium text-gray-700 mb-4">Time-to-Value Comparison</h3>
        
        {/* Traditional Approach Timeline */}
        <div className="mb-12">
          <div className="flex items-center mb-2">
            <div className="w-1/3">
              <h4 className="text-lg font-medium text-red-700">Traditional ML Approach</h4>
              <p className="text-sm text-gray-500">12-18 month implementation</p>
            </div>
            <div className="w-2/3 h-10 bg-gray-200 rounded-full relative">
              <div className="absolute inset-0 flex items-center justify-around">
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-red-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Start</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-yellow-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Discovery<br />3-4 months</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-yellow-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Development<br />5-8 months</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-yellow-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Testing<br />2-3 months</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-yellow-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Training<br />1-2 months</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-red-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Value<br />Realization</div>
                </div>
              </div>
            </div>
          </div>
          <div className="pl-1/3 ml-10 mt-12">
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <h5 className="font-medium text-red-700 mb-2">Why So Long?</h5>
              <ul className="text-sm space-y-2">
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Custom model development from scratch</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Manual feature engineering and selection</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Custom EHR integration development</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  <span>Extended data collection requirements</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* VitalSchedule Approach Timeline */}
        <div>
          <div className="flex items-center mb-2">
            <div className="w-1/3">
              <h4 className="text-lg font-medium text-green-700">VitalSchedule Approach</h4>
              <p className="text-sm text-gray-500">4-6 month implementation</p>
            </div>
            <div className="w-2/3 h-10 bg-gray-200 rounded-full relative">
              <div className="absolute inset-0 flex items-center justify-around">
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-green-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Start</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-blue-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Discovery<br />3-4 weeks</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-blue-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Configuration<br />4-6 weeks</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-blue-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Integration<br />4-6 weeks</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-blue-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Training<br />2-3 weeks</div>
                </div>
                <div className="relative">
                  <div className="w-6 h-6 rounded-full bg-green-500"></div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">Value<br />Realization</div>
                </div>
              </div>
            </div>
          </div>
          <div className="pl-1/3 ml-10 mt-12">
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <h5 className="font-medium text-green-700 mb-2">How We Accelerate Implementation</h5>
              <ul className="text-sm space-y-2">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span>Pre-built prediction models requiring only fine-tuning</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span>Ready-made EHR connectors for major systems</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span>Standardized implementation methodology with predefined milestones</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span>Minimal historical data requirements (6-12 months vs 2+ years)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      {/* Key Milestones Comparison */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-medium text-gray-700 mb-4">Key Milestones Comparison</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="border px-4 py-2 bg-gray-50">Milestone</th>
                <th className="border px-4 py-2 bg-gray-50">Traditional Approach</th>
                <th className="border px-4 py-2 bg-gray-50">VitalSchedule</th>
                <th className="border px-4 py-2 bg-gray-50">Time Saved</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border px-4 py-2 font-medium">First data integration</td>
                <td className="border px-4 py-2 text-red-700">Week 10-12</td>
                <td className="border px-4 py-2 text-green-700">Week 3-4</td>
                <td className="border px-4 py-2 text-blue-700">8 weeks</td>
              </tr>
              <tr>
                <td className="border px-4 py-2 font-medium">Initial model training</td>
                <td className="border px-4 py-2 text-red-700">Week 20-24</td>
                <td className="border px-4 py-2 text-green-700">Week 5-6</td>
                <td className="border px-4 py-2 text-blue-700">18 weeks</td>
              </tr>
              <tr>
                <td className="border px-4 py-2 font-medium">User acceptance testing</td>
                <td className="border px-4 py-2 text-red-700">Week 36-40</td>
                <td className="border px-4 py-2 text-green-700">Week 12-14</td>
                <td className="border px-4 py-2 text-blue-700">26 weeks</td>
              </tr>
              <tr>
                <td className="border px-4 py-2 font-medium">First department live</td>
                <td className="border px-4 py-2 text-red-700">Week 48-52</td>
                <td className="border px-4 py-2 text-green-700">Week 16-18</td>
                <td className="border px-4 py-2 text-blue-700">34 weeks</td>
              </tr>
              <tr>
                <td className="border px-4 py-2 font-medium">Full deployment</td>
                <td className="border px-4 py-2 text-red-700">Week 52-72</td>
                <td className="border px-4 py-2 text-green-700">Week 20-24</td>
                <td className="border px-4 py-2 text-blue-700">48 weeks</td>
              </tr>
              <tr>
                <td className="border px-4 py-2 font-medium">First ROI measurement</td>
                <td className="border px-4 py-2 text-red-700">Week 72-80</td>
                <td className="border px-4 py-2 text-green-700">Week 24-28</td>
                <td className="border px-4 py-2 text-blue-700">52 weeks</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ImplementationTimeline;
