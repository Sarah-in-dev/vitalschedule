import React, { useState } from 'react';

const OperationalDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  
  // Sample appointments data
  const appointments = [
    { id: 1, patient: 'Sarah Johnson', time: '9:00 AM', type: 'Primary Care', provider: 'Dr. Martinez', riskScore: 0.78, factors: ['Previous no-shows', 'Transportation barrier', 'Lead time > 30 days'] },
    { id: 2, patient: 'Robert Chen', time: '9:30 AM', type: 'Primary Care', provider: 'Dr. Martinez', riskScore: 0.15, factors: ['Consistent attendance', 'Short lead time', 'Lives nearby'] },
    { id: 3, patient: 'Maria Garcia', time: '10:00 AM', type: 'Behavioral Health', provider: 'Dr. Washington', riskScore: 0.82, factors: ['Previous no-shows', 'Medicaid insurance', 'Bad weather forecast', 'Friday appointment'] },
    { id: 4, patient: 'James Wilson', time: '10:30 AM', type: 'Dental', provider: 'Dr. Patel', riskScore: 0.32, factors: ['Previous cancellation', 'Lives 15 miles away'] },
    { id: 5, patient: 'Alice Thompson', time: '11:00 AM', type: 'Primary Care', provider: 'Dr. Martinez', riskScore: 0.68, factors: ['Two recent no-shows', 'Public transit dependent', 'Medicaid insurance'] }
  ];

  // Completed interventions data
  const completedInterventions = [
    { id: 1, patient: 'Maria Garcia', intervention: 'Phone call reminder', outcome: 'Confirmed attendance' },
    { id: 2, patient: 'Emma Davis', intervention: 'Transportation arrangement', outcome: 'Transportation confirmed' },
    { id: 3, patient: 'Sarah Johnson', intervention: 'SMS reminder', outcome: 'No response' },
    { id: 4, patient: 'Thomas Rodriguez', intervention: 'Phone call reminder', outcome: 'Left voicemail' },
    { id: 5, patient: 'Alice Thompson', intervention: 'SMS reminder', outcome: 'Confirmed attendance' }
  ];

  // Intervention effectiveness data
  const interventionEffectiveness = [
    { type: 'Personal phone call', successRate: 0.75 },
    { type: 'Transportation assistance', successRate: 0.86 },
    { type: 'SMS reminder', successRate: 0.55 },
    { type: 'Email reminder', successRate: 0.50 },
    { type: 'Appointment rescheduling', successRate: 0.70 }
  ];

  // Department improvement data
  const departmentImprovements = [
    { name: 'Primary Care', beforeRate: 0.25, afterRate: 0.18 },
    { name: 'Behavioral Health', beforeRate: 0.40, afterRate: 0.24 },
    { name: 'Dental', beforeRate: 0.30, afterRate: 0.20 },
    { name: 'Specialty', beforeRate: 0.20, afterRate: 0.14 }
  ];

  // Helper for risk styling
  const getRiskClass = (score) => {
    if (score < 0.3) return "bg-green-100 text-green-800";
    if (score < 0.7) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const getRiskLabel = (score) => {
    if (score < 0.3) return "Low";
    if (score < 0.7) return "Medium";
    return "High";
  };

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {/* Header */}
        <div className="px-4 py-5 border-b border-gray-200 sm:px-6 flex justify-between items-center">
          <div>
            <h1 className="text-lg font-medium text-gray-900">VitalSchedule Dashboard</h1>
            <p className="mt-1 text-sm text-gray-500">Predictive No-Show Analytics</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">March 6, 2025</p>
            <p className="text-sm text-gray-500">Current No-Show Rate: <span className="text-green-600 font-medium">17%</span></p>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('appointments')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'appointments'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Today's Appointments
            </button>
            <button
              onClick={() => setActiveTab('interventions')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'interventions'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Intervention Tracking
            </button>
            <button
              onClick={() => setActiveTab('impact')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'impact'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Impact Analysis
            </button>
          </nav>
        </div>
        
        {/* Tab Content */}
        <div className="p-4">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-red-50 p-4 rounded-lg">
                  <p className="text-lg font-bold text-red-700">3</p>
                  <p className="text-sm text-red-600">High Risk Appointments</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <p className="text-lg font-bold text-yellow-700">2</p>
                  <p className="text-sm text-yellow-600">Medium Risk Appointments</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-lg font-bold text-green-700">3</p>
                  <p className="text-sm text-green-600">Low Risk Appointments</p>
                </div>
              </div>
              
              <div className="mb-6">
                <h2 className="text-lg font-medium mb-4">Today's Improvement Summary</h2>
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Expected No-Shows</p>
                      <div className="flex items-center justify-center mt-1">
                        <p className="text-lg font-bold text-gray-800">2.2</p>
                        <p className="text-xs text-gray-500 ml-1">(28% baseline)</p>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Predicted No-Shows</p>
                      <div className="flex items-center justify-center mt-1">
                        <p className="text-lg font-bold text-blue-700">1.4</p>
                        <p className="text-xs text-gray-500 ml-1">(with interventions)</p>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Appointments Saved</p>
                      <div className="flex items-center justify-center mt-1">
                        <p className="text-lg font-bold text-green-700">0.8</p>
                        <p className="text-xs text-gray-500 ml-1">(≈ $120 revenue)</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border rounded-lg p-4">
                  <h2 className="text-lg font-medium mb-4">Recommended Actions</h2>
                  <ul className="space-y-2">
                    <li className="flex items-center justify-between p-2 bg-red-50 rounded border border-red-200">
                      <div className="flex items-center">
                        <span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>
                        <span>Call Maria Garcia to confirm 10:00 AM appointment</span>
                      </div>
                      <button className="px-2 py-1 bg-red-600 text-white rounded text-xs">Urgent</button>
                    </li>
                    <li className="flex items-center justify-between p-2 bg-red-50 rounded border border-red-200">
                      <div className="flex items-center">
                        <span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>
                        <span>Arrange transportation for Emma Davis</span>
                      </div>
                      <button className="px-2 py-1 bg-red-600 text-white rounded text-xs">Urgent</button>
                    </li>
                    <li className="flex items-center justify-between p-2 bg-yellow-50 rounded border border-yellow-200">
                      <div className="flex items-center">
                        <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>
                        <span>Send SMS reminder to Alice Thompson</span>
                      </div>
                      <button className="px-2 py-1 bg-yellow-600 text-white rounded text-xs">Important</button>
                    </li>
                  </ul>
                </div>
                
                <div className="border rounded-lg p-4">
                  <h2 className="text-lg font-medium mb-4">Weekly No-Show Improvement</h2>
                  <div className="flex items-center justify-center h-40">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">39%</p>
                      <p className="text-sm text-gray-600">reduction in no-shows</p>
                      <p className="text-xs text-gray-500 mt-2">Current week vs baseline</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Appointments Tab */}
          {activeTab === 'appointments' && (
            <div>
              <table className="min-w-full divide-y divide-gray-200 mb-6">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Patient
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {appointments.map((appointment) => (
                    <tr key={appointment.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedAppointment(appointment)}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{appointment.patient}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{appointment.time}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{appointment.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${getRiskClass(appointment.riskScore)}`}>
                          {getRiskLabel(appointment.riskScore)} ({Math.round(appointment.riskScore * 100)}%)
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button className="text-blue-600 hover:text-blue-900" onClick={() => setSelectedAppointment(appointment)}>
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {selectedAppointment && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-medium mb-2">{selectedAppointment.patient}</h3>
                  <p className="text-sm text-gray-500 mb-4">{selectedAppointment.time} - {selectedAppointment.type} with {selectedAppointment.provider}</p>
                  
                  <div className="mb-4">
                    <h4 className="text-sm font-medium mb-1">Risk Assessment</h4>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                      <div 
                        className={`h-2.5 rounded-full ${
                          selectedAppointment.riskScore < 0.3 ? 'bg-green-500' : 
                          selectedAppointment.riskScore < 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${selectedAppointment.riskScore * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600">
                      This appointment has a <strong>{Math.round(selectedAppointment.riskScore * 100)}%</strong> chance of being a no-show.
                    </p>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="text-sm font-medium mb-1">Contributing Factors</h4>
                    <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                      {selectedAppointment.factors.map((factor, index) => (
                        <li key={index}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {selectedAppointment.riskScore > 0.5 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium mb-2">Recommended Interventions</h4>
                      <ul className="space-y-2">
                        <li className="flex justify-between items-center p-2 bg-blue-50 rounded border border-blue-200">
                          <span>Phone call reminder</span>
                          <button className="px-2 py-1 bg-blue-600 text-white rounded text-xs">Apply</button>
                        </li>
                        {selectedAppointment.riskScore > 0.7 && (
                          <li className="flex justify-between items-center p-2 bg-blue-50 rounded border border-blue-200">
                            <span>Transportation assistance</span>
                            <button className="px-2 py-1 bg-blue-600 text-white rounded text-xs">Apply</button>
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                  
                  <div className="flex justify-end">
                    <button 
                      className="px-4 py-2 bg-blue-600 text-white rounded text-sm"
                      onClick={() => setSelectedAppointment(null)}
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Interventions Tracking Tab */}
          {activeTab === 'interventions' && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Recently Completed Interventions</h3>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Intervention</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Outcome</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {completedInterventions.map((item) => (
                          <tr key={item.id}>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{item.patient}</td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{item.intervention}</td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{item.outcome}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-4">Intervention Effectiveness</h3>
                  <div className="space-y-4">
                    {interventionEffectiveness.map((intervention, index) => (
                      <div key={index} className="bg-white p-3 border rounded-lg">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium">{intervention.type}</span>
                          <span className="text-sm text-gray-500">{Math.round(intervention.successRate * 100)}% success rate</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${intervention.successRate * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-4">Intervention Timeline</h3>
                <div className="bg-white p-4 border rounded-lg">
                  <div className="space-y-6">
                    <div className="flex">
                      <div className="flex-shrink-0 w-12 text-center">
                        <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white text-sm font-medium">
                          14d
                        </div>
                      </div>
                      <div className="ml-4">
                        <h4 className="text-md font-medium">Initial Scheduling Phase</h4>
                        <p className="text-sm text-gray-600 mt-1">Strategic appointment scheduling based on patient history and optimal patterns.</p>
                        <p className="text-sm text-green-600 mt-1">25% reduction in no-shows</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex-shrink-0 w-12 text-center">
                        <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white text-sm font-medium">
                          7d
                        </div>
                      </div>
                      <div className="ml-4">
                        <h4 className="text-md font-medium">First Reminder Phase</h4>
                        <p className="text-sm text-gray-600 mt-1">Initial appointment reminder via preferred channel.</p>
                        <p className="text-sm text-green-600 mt-1">15% reduction in no-shows</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex-shrink-0 w-12 text-center">
                        <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white text-sm font-medium">
                          3d
                        </div>
                      </div>
                      <div className="ml-4">
                        <h4 className="text-md font-medium">Barrier Resolution Phase</h4>
                        <p className="text-sm text-gray-600 mt-1">Targeted interventions to address specific barriers.</p>
                        <p className="text-sm text-green-600 mt-1">40% reduction in no-shows</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex-shrink-0 w-12 text-center">
                        <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white text-sm font-medium">
                          1d
                        </div>
                      </div>
                      <div className="ml-4">
                        <h4 className="text-md font-medium">Final Confirmation Phase</h4>
                        <p className="text-sm text-gray-600 mt-1">Final reminder with confirmation request.</p>
                        <p className="text-sm text-green-600 mt-1">18% reduction in no-shows</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Impact Analysis Tab */}
          {activeTab === 'impact' && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-4 border rounded-lg">
                  <h3 className="text-lg font-medium mb-4">Department Improvements</h3>
                  <table className="min-w-full">
                    <thead>
                      <tr>
                        <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider pb-2">Department</th>
                        <th className="text-center text-xs font-medium text-gray-500 uppercase tracking-wider pb-2">Before</th>
                        <th className="text-center text-xs font-medium text-gray-500 uppercase tracking-wider pb-2">Current</th>
                        <th className="text-center text-xs font-medium text-gray-500 uppercase tracking-wider pb-2">Improvement</th>
                      </tr>
                    </thead>
                    <tbody>
                      {departmentImprovements.map((dept, index) => (
                        <tr key={index} className="border-t">
                          <td className="py-3 text-sm font-medium text-gray-900">{dept.name}</td>
                          <td className="py-3 text-center text-sm text-gray-500">{Math.round(dept.beforeRate * 100)}%</td>
                          <td className="py-3 text-center text-sm text-gray-500">{Math.round(dept.afterRate * 100)}%</td>
                          <td className="py-3 text-center text-sm text-green-600 font-medium">
                            {Math.round((dept.beforeRate - dept.afterRate) / dept.beforeRate * 100)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="bg-white p-4 border rounded-lg">
                  <h3 className="text-lg font-medium mb-4">Monthly Impact Summary</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-sm text-gray-600">Appointments Saved</p>
                      <p className="text-xl font-bold text-green-700">86</p>
                      <p className="text-xs text-gray-500">This month</p>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-sm text-gray-600">Revenue Recovered</p>
                      <p className="text-xl font-bold text-green-700">$12,900</p>
                      <p className="text-xs text-gray-500">This month</p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-sm text-gray-600">Provider Hours Saved</p>
                      <p className="text-xl font-bold text-blue-700">43</p>
                      <p className="text-xs text-gray-500">This month</p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-sm text-gray-600">Staff Time Saved</p>
                      <p className="text-xl font-bold text-blue-700">64 hrs</p>
                      <p className="text-xs text-gray-500">This month</p>
                    </div>
                  </div>
                  
                  <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-700">Patient Satisfaction Impact</h4>
                    <p className="text-sm text-gray-600 mt-1">Patient satisfaction scores increased by 18% since implementation</p>
                    <p className="text-sm text-gray-600 mt-1">Wait time for appointments decreased by 4.5 days on average</p>
                  </div>
                </div>
                
                <div className="bg-white p-4 border rounded-lg md:col-span-2">
                  <h3 className="text-lg font-medium mb-4">Continuous Improvement Metrics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="border rounded-lg p-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Prediction Accuracy</h4>
                      <p className="text-xl font-bold text-gray-900">84%</p>
                      <p className="text-xs text-gray-500">Up from 76% at launch</p>
                      <p className="text-sm text-gray-600 mt-2">Model continues to learn from intervention outcomes</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Cost Per Intervention</h4>
                      <p className="text-xl font-bold text-gray-900">$4.73</p>
                      <p className="text-xs text-gray-500">Down from $7.20 at launch</p>
                      <p className="text-sm text-gray-600 mt-2">Improved targeting reduces unnecessary interventions</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Return on Investment</h4>
                      <p className="text-xl font-bold text-gray-900">11.2x</p>
                      <p className="text-xs text-gray-500">Up from 8.5x at launch</p>
                      <p className="text-sm text-gray-600 mt-2">For every $1 spent on interventions, $11.20 revenue is recovered</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperationalDashboard;
