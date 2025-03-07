import React, { useState } from 'react';

const PredictiveAnalysis = () => {
  const [activeTab, setActiveTab] = useState('predictors');
  const [selectedFactor, setSelectedFactor] = useState(null);
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  
  // Risk factor data
  const riskFactors = [
    { 
      id: 1,
      factor: 'Previous no-show history', 
      importance: 0.69, 
      description: 'Pattern of missed appointments is the strongest predictor of future behavior',
      details: 'Patients with 3+ no-shows in the past 6 months have a 76% chance of missing their next appointment if no intervention is made.',
      dataPoints: ['No-show count', 'No-show rate', 'Consecutive no-shows', 'Recent no-shows (last 60 days)']
    },
    { 
      id: 2,
      factor: 'Appointment lead time', 
      importance: 0.31, 
      description: 'Longer wait times between scheduling and appointment date increase no-show probability',
      details: 'Each additional week of lead time increases no-show probability by approximately 5%. Appointments scheduled more than 30 days in advance have a baseline no-show rate 62% higher than same-week appointments.',
      dataPoints: ['Days between scheduling and appointment', 'Same-day appointment flag', 'Scheduling source']
    },
    { 
      id: 3,
      factor: 'Appointment type', 
      importance: 0.09, 
      description: 'Behavioral health appointments have significantly higher no-show rates than other types',
      details: 'Behavioral health appointments experience a 40% average no-show rate compared to 20% for primary care.',
      dataPoints: ['Service line', 'Provider specialty', 'Procedure type', 'Expected duration', 'First appointment flag']
    },
    { 
      id: 4,
      factor: 'Day and time', 
      importance: 0.07, 
      description: 'Specific day-time combinations show consistent patterns of higher no-show risk',
      details: 'Monday mornings and Friday afternoons have the highest no-show rates (32% and 29% respectively).',
      dataPoints: ['Day of week', 'Time of day', 'First/last appointment of day']
    },
    { 
      id: 5,
      factor: 'Distance and transportation', 
      importance: 0.05, 
      description: 'Patients living farther from the clinic or with limited transportation access miss more appointments',
      details: 'Patients living more than 10 miles from the clinic have a 27% higher no-show rate.',
      dataPoints: ['Distance in miles', 'Transit score', 'Car ownership flag', 'Neighborhood walkability score']
    }
  ];
  
  // Intervention strategies data
  const interventionStrategies = [
    {
      id: 1,
      intervention: 'Multi-channel reminders',
      effectiveness: 0.25,
      description: 'Personalized reminder system using patient preferences and response patterns',
      details: 'Our system goes beyond basic reminders by analyzing individual response patterns to determine optimal timing, channel, and content.',
      implementation: [
        'Baseline: Automated text message 2 days before appointment',
        'Medium risk: Two reminders (3 days and 1 day prior) via preferred channel',
        'High risk: Three reminders via multiple channels',
        'Ultra-high risk: All above plus personal call from staff'
      ]
    },
    {
      id: 2,
      intervention: 'Transportation assistance',
      effectiveness: 0.40,
      description: 'Coordinated transportation solutions based on specific patient barriers',
      details: 'For patients with identified transportation barriers, providing logistics support reduces no-shows by up to 40%.',
      implementation: [
        'Transportation barrier identification during scheduling',
        'Automated eligibility check for transportation benefits',
        'Integration with rideshare services and medical transport',
        'Weather-triggered transportation contingency planning'
      ]
    },
    {
      id: 3,
      intervention: 'Strategic scheduling',
      effectiveness: 0.35,
      description: 'Machine learning-optimized scheduling based on individual attendance patterns',
      details: 'By analyzing historical attendance patterns, our system recommends optimal appointment slots for each patient.',
      implementation: [
        'Patient-specific day and time recommendations',
        'Lead time optimization based on appointment type',
        'Provider continuity prioritization',
        'Clustered scheduling for patients with transportation barriers'
      ]
    },
    {
      id: 4,
      intervention: 'Barrier-specific support',
      effectiveness: 0.30,
      description: 'Targeted support services addressing specific attendance barriers',
      details: 'Our system identifies specific barriers for each patient and triggers appropriate support services.',
      implementation: [
        'Childcare coordination for parents with young children',
        'Interpreter scheduling for patients with language barriers',
        'Benefits navigation for insurance/payment concerns',
        'Social work referral for complex SDOH barriers'
      ]
    }
  ];
  
  // Patient interaction sequence data
  const interactionSequences = [
    {
      id: 1,
      patientType: 'High-risk behavioral health patient with transportation barriers',
      sequence: [
        { day: -14, action: 'Optimal scheduling with provider continuity' },
        { day: -10, action: 'Transportation needs assessment' },
        { day: -7, action: 'First reminder with appointment purpose' },
        { day: -5, action: 'Transportation confirmation' },
        { day: -3, action: 'Second reminder with preparation instructions' },
        { day: -1, action: 'Final reminder with transportation details' },
        { day: 0, action: 'Day-of appointment confirmation' }
      ]
    },
    {
      id: 2,
      patientType: 'Mother with multiple children and work constraints',
      sequence: [
        { day: -14, action: 'Scheduling optimized for work schedule' },
        { day: -7, action: 'First reminder with calendar option' },
        { day: -3, action: 'Second reminder with childcare options' },
        { day: -1, action: 'Final reminder with preparation guidance' },
        { day: 0, action: 'Child-friendly waiting experience' }
      ]
    }
  ];
  
  // Helper for generating progress bar color based on value
  const getProgressColor = (value) => {
    if (value < 0.2) return "bg-green-500";
    if (value < 0.4) return "bg-blue-500";
    if (value < 0.6) return "bg-yellow-500";
    return "bg-red-500";
  };
  
  return (
    <div className="p-4 max-w-6xl mx-auto bg-white shadow rounded-lg">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Advanced Predictive Analysis</h2>
      <p className="text-gray-600 mb-6">
        VitalSchedule analyzes 40+ data points to predict no-shows and recommend personalized interventions
      </p>
      
      {/* Tabs navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex">
          <button
            onClick={() => setActiveTab('predictors')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'predictors'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500'
            }`}
          >
            Risk Predictors
          </button>
          <button
            onClick={() => setActiveTab('interventions')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'interventions'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500'
            }`}
          >
            Smart Interventions
          </button>
          <button
            onClick={() => setActiveTab('sequences')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'sequences'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500'
            }`}
          >
            Interaction Sequences
          </button>
        </nav>
      </div>
      
      {/* Risk Predictors Tab */}
      {activeTab === 'predictors' && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Key Risk Factors</h3>
              <div className="space-y-4">
                {riskFactors.map((factor) => (
                  <div 
                    key={factor.id}
                    className={`p-3 border rounded-lg cursor-pointer ${selectedFactor && selectedFactor.id === factor.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                    onClick={() => setSelectedFactor(factor)}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium">{factor.factor}</span>
                      <span className="text-sm text-gray-500">{(factor.importance * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div 
                        className={`${getProgressColor(factor.importance)} h-2 rounded-full`}
                        style={{ width: `${factor.importance * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{factor.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="md:col-span-2">
              {selectedFactor ? (
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-medium text-gray-800 mb-4">{selectedFactor.factor}</h3>
                  <p className="text-gray-700 mb-6">{selectedFactor.details}</p>
                  
                  <div className="mb-6">
                    <h4 className="text-lg font-medium text-gray-700 mb-2">Data Points Analyzed</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedFactor.dataPoints.map((point, index) => (
                        <span key={index} className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {point}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 p-6 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Select a risk factor to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Interventions Tab */}
      {activeTab === 'interventions' && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Smart Intervention Strategies</h3>
              <div className="space-y-4">
                {interventionStrategies.map((strategy) => (
                  <div 
                    key={strategy.id}
                    className={`p-3 border rounded-lg cursor-pointer ${selectedIntervention && selectedIntervention.id === strategy.id ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}
                    onClick={() => setSelectedIntervention(strategy)}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium">{strategy.intervention}</span>
                      <span className="text-sm text-gray-500">{(strategy.effectiveness * 100).toFixed(0)}% effective</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${strategy.effectiveness * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{strategy.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="md:col-span-2">
              {selectedIntervention ? (
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-medium text-gray-800 mb-4">{selectedIntervention.intervention}</h3>
                  <p className="text-gray-700 mb-6">{selectedIntervention.details}</p>
                  
                  <div className="mb-6">
                    <h4 className="text-lg font-medium text-gray-700 mb-2">Implementation Approach</h4>
                    <ul className="space-y-2 ml-5 list-disc">
                      {selectedIntervention.implementation.map((step, index) => (
                        <li key={index} className="text-gray-700">{step}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 p-6 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Select an intervention strategy to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Interaction Sequences Tab */}
      {activeTab === 'sequences' && (
        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-4">Personalized Interaction Sequences</h3>
          <p className="text-gray-600 mb-6">
            VitalSchedule creates optimized interaction sequences based on patient profiles and risk factors.
          </p>
          
          <div className="grid grid-cols-1 gap-6">
            {interactionSequences.map((sequence) => (
              <div key={sequence.id} className="border rounded-lg overflow-hidden">
                <div className="bg-gray-100 px-4 py-3 border-b">
                  <h4 className="font-medium text-gray-800">{sequence.patientType}</h4>
                </div>
                <div className="p-4">
                  <div className="relative">
                    {sequence.sequence.map((step, index) => (
                      <div key={index} className="mb-4 flex items-start">
                        <div className="flex-shrink-0 w-12 text-center">
                          <div className={`inline-flex items-center justify-center h-8 w-8 rounded-full ${step.day === 0 ? 'bg-green-500' : 'bg-blue-500'} text-white text-sm font-medium`}>
                            {step.day === 0 ? 'Day' : step.day}
                          </div>
                        </div>
                        <div className="ml-4 flex-grow">
                          <div className={`p-3 rounded-lg ${step.day === 0 ? 'bg-green-50 border border-green-200' : 'bg-blue-50 border border-blue-200'}`}>
                            {step.action}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictiveAnalysis;
