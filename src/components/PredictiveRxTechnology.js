import React, { useState } from 'react';

const PredictiveRxTechnology = () => {
  const [expandedStep, setExpandedStep] = useState(null);
  const [expandedModule, setExpandedModule] = useState('noshow');
  
  const toggleStep = (step) => {
    setExpandedStep(expandedStep === step ? null : step);
  };
  
  // Define the core technology steps
  const technologySteps = [
    {
      id: 'data',
      title: 'Data Foundation',
      description: 'Our platform combines comprehensive pre-trained healthcare datasets with your organization-specific data.',
      details: [
        'Secure integration with your EHR and practice management systems',
        'Proprietary data processing pipeline for normalization and enrichment',
        'Integration of social determinants of health and contextual factors',
        'Continuous data validation and quality assurance protocols'
      ]
    },
    {
      id: 'ml',
      title: 'ML Engine',
      description: 'Our advanced machine learning engine identifies complex patterns to predict healthcare outcomes.',
      details: [
        'Gradient boosting architecture optimized for healthcare applications',
        'Transfer learning from broader datasets to your specific population',
        'Multi-factor analysis examining 40+ variables simultaneously',
        'Adaptive model training that improves with additional data'
      ]
    },
    {
      id: 'risk',
      title: 'Risk Assessment',
      description: 'The system generates personalized risk scores with detailed factor analysis.',
      details: [
        'Probability scoring on a 0-100% scale',
        'Factor contribution analysis showing key drivers',
        'Risk stratification into actionable categories',
        'Confidence intervals based on data completeness'
      ]
    },
    {
      id: 'intervention',
      title: 'Smart Interventions',
      description: 'Evidence-based intervention recommendations targeted to specific risk factors.',
      details: [
        'Factor-matched intervention suggestions',
        'ROI-optimized recommendation prioritization',
        'Workflow integration for seamless action',
        'Personalized approaches based on patient characteristics'
      ]
    },
    {
      id: 'learning',
      title: 'Continuous Learning',
      description: 'The system continuously improves by analyzing intervention outcomes.',
      details: [
        'Outcome tracking to measure intervention effectiveness',
        'Automated model retraining on new data',
        'Population-specific optimization',
        'Quarterly model updates incorporating latest clinical research'
      ]
    }
  ];
  
  // Define the available modules
  const modules = [
    {
      id: 'noshow',
      name: 'PredictiveRx No-Show',
      description: 'Predicts missed appointments to optimize scheduling efficiency and improve care continuity.',
      keyFactors: ['Patient history patterns', 'Scheduling characteristics', 'Access barriers', 'Appointment specifications', 'Environmental conditions'],
      outcomes: ['Reduced missed appointments', 'Improved provider productivity', 'Enhanced patient engagement', 'Increased revenue'],
      color: 'blue'
    },
    {
      id: 'readmission',
      name: 'PredictiveRx Readmission',
      description: 'Identifies patients at risk of hospital readmission to enable targeted transitional care interventions.',
      keyFactors: ['Clinical history patterns', 'Post-discharge factors', 'Support system indicators', 'Condition complexity factors', 'Care transition metrics'],
      outcomes: ['Reduced readmission rates', 'Improved care transitions', 'Decreased penalties', 'Better patient outcomes'],
      color: 'green'
    },
    {
      id: 'future',
      name: 'Future Modules',
      description: 'The PredictiveRx AI platform will expand to address additional healthcare challenges.',
      keyFactors: ['PredictiveRx Adherence - treatment compliance prediction', 'PredictiveRx Outcomes - intervention response prediction', 'PredictiveRx Utilization - resource optimization'],
      outcomes: ['Unified predictive intelligence across the care continuum', 'Comprehensive risk management', 'Improved population health outcomes'],
      color: 'purple'
    }
  ];
  
  return (
    <div className="p-6 max-w-6xl mx-auto bg-white shadow rounded-lg">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-800">PredictiveRx AI Technology</h2>
        <p className="text-gray-600 mt-2">
          Our unified predictive intelligence platform applies advanced machine learning to transform healthcare outcomes.
        </p>
      </div>
      
      {/* Main Technology Flow Diagram - SVG Workflow Diagram */}
      <div className="mb-10">
        <h3 className="text-lg font-medium text-gray-700 mb-6">How Our Technology Works</h3>
        
        <div className="overflow-auto pb-4">
          {/* SVG Workflow Diagram - Desktop Version (hidden on very small screens) */}
          <div className="hidden sm:block min-w-max">
            <svg width="800" height="240" viewBox="0 0 800 240" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Background Boxes */}
              <rect x="10" y="40" width="140" height="160" rx="8" fill="#F3F4F6" stroke="#E5E7EB" strokeWidth="1.5" />
              <rect x="170" y="40" width="140" height="160" rx="8" fill="#F3F4F6" stroke="#E5E7EB" strokeWidth="1.5" />
              <rect x="330" y="40" width="140" height="160" rx="8" fill="#F3F4F6" stroke="#E5E7EB" strokeWidth="1.5" />
              <rect x="490" y="40" width="140" height="160" rx="8" fill="#F3F4F6" stroke="#E5E7EB" strokeWidth="1.5" />
              <rect x="650" y="40" width="140" height="160" rx="8" fill="#F3F4F6" stroke="#E5E7EB" strokeWidth="1.5" />
              
              {/* Connecting Arrows */}
              <path d="M150 120 L170 120" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M310 120 L330 120" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M470 120 L490 120" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M630 120 L650 120" stroke="#9CA3AF" strokeWidth="2" />
              
              {/* Arrow tips */}
              <path d="M165 120 L170 120 L168 118" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M165 120 L170 120 L168 122" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M325 120 L330 120 L328 118" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M325 120 L330 120 L328 122" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M485 120 L490 120 L488 118" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M485 120 L490 120 L488 122" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M645 120 L650 120 L648 118" stroke="#9CA3AF" strokeWidth="2" />
              <path d="M645 120 L650 120 L648 122" stroke="#9CA3AF" strokeWidth="2" />
              
              {/* Feedback Loop Arrow */}
              <path d="M720 200 C720 220, 400 240, 80 200" stroke="#9CA3AF" strokeWidth="1.5" strokeDasharray="4 2" />
              <path d="M85 199 L80 200 L85 201" stroke="#9CA3AF" strokeWidth="1.5" />
              
              {/* Icons and Labels */}
              <circle cx="80" cy="80" r="24" fill="#DBEAFE" />
              <text x="80" y="84" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#3B82F6">DB</text>
              
              <circle cx="240" cy="80" r="24" fill="#DBEAFE" />
              <text x="240" y="84" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#3B82F6">ML</text>
              
              <circle cx="400" cy="80" r="24" fill="#DBEAFE" />
              <text x="400" y="84" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#3B82F6">RA</text>
              
              <circle cx="560" cy="80" r="24" fill="#DBEAFE" />
              <text x="560" y="84" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#3B82F6">SI</text>
              
              <circle cx="720" cy="80" r="24" fill="#DBEAFE" />
              <text x="720" y="84" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#3B82F6">CL</text>
              
              {/* Labels */}
              <text x="80" y="130" textAnchor="middle" fontSize="14" fontWeight="500" fill="#374151">Data Foundation</text>
              <text x="240" y="130" textAnchor="middle" fontSize="14" fontWeight="500" fill="#374151">ML Engine</text>
              <text x="400" y="130" textAnchor="middle" fontSize="14" fontWeight="500" fill="#374151">Risk Assessment</text>
              <text x="560" y="130" textAnchor="middle" fontSize="14" fontWeight="500" fill="#374151">Smart Interventions</text>
              <text x="720" y="130" textAnchor="middle" fontSize="14" fontWeight="500" fill="#374151">Continuous Learning</text>
              
              {/* Sub-labels */}
              <text x="80" y="150" textAnchor="middle" fontSize="10" fill="#6B7280" width="120">Healthcare data + Your data</text>
              <text x="240" y="150" textAnchor="middle" fontSize="10" fill="#6B7280">Pattern identification</text>
              <text x="400" y="150" textAnchor="middle" fontSize="10" fill="#6B7280">Probability calculation</text>
              <text x="560" y="150" textAnchor="middle" fontSize="10" fill="#6B7280">Targeted recommendations</text>
              <text x="720" y="150" textAnchor="middle" fontSize="10" fill="#6B7280">Outcome-based improvement</text>
              
              {/* Feedback Loop Label */}
              <text x="400" y="220" textAnchor="middle" fontSize="10" fontStyle="italic" fill="#6B7280">Continuous learning feedback loop</text>
              
              {/* Clickable areas for interaction */}
              <rect x="10" y="40" width="140" height="160" rx="8" fillOpacity="0" stroke="none" onClick={() => toggleStep('data')} style={{cursor: 'pointer'}} />
              <rect x="170" y="40" width="140" height="160" rx="8" fillOpacity="0" stroke="none" onClick={() => toggleStep('ml')} style={{cursor: 'pointer'}} />
              <rect x="330" y="40" width="140" height="160" rx="8" fillOpacity="0" stroke="none" onClick={() => toggleStep('risk')} style={{cursor: 'pointer'}} />
              <rect x="490" y="40" width="140" height="160" rx="8" fillOpacity="0" stroke="none" onClick={() => toggleStep('intervention')} style={{cursor: 'pointer'}} />
              <rect x="650" y="40" width="140" height="160" rx="8" fillOpacity="0" stroke="none" onClick={() => toggleStep('learning')} style={{cursor: 'pointer'}} />
            </svg>
          </div>
          
          {/* Mobile Flow Diagram (vertical, shown only on very small screens) */}
          <div className="sm:hidden space-y-4">
            {technologySteps.map((step, index) => (
              <React.Fragment key={step.id}>
                <div 
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors"
                  onClick={() => toggleStep(step.id)}
                >
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                      <span className="text-blue-600 font-bold">{step.title.substring(0, 2)}</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">{step.title}</h4>
                      <p className="text-xs text-gray-500">{step.description.split(' ').slice(0, 5).join(' ')}...</p>
                    </div>
                  </div>
                </div>
                
                {/* Connector Arrow (except after last item) */}
                {index < technologySteps.length - 1 && (
                  <div className="flex justify-center">
                    <span className="text-gray-400 text-2xl">↓</span>
                  </div>
                )}
              </React.Fragment>
            ))}
            
            {/* Mobile Feedback Loop Indicator */}
            <div className="flex justify-center items-center text-gray-500 text-xs">
              <span>⟲</span>
              <span className="ml-1">Continuous learning feedback loop</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Expanded Step Details (if any step is expanded) */}
      {expandedStep && (
        <div className="mb-10 p-4 bg-blue-50 rounded-lg border border-blue-200">
          {technologySteps.map(step => (
            step.id === expandedStep ? (
              <div key={step.id}>
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                    <span className="text-blue-600 font-bold">{step.title.substring(0, 2)}</span>
                  </div>
                  <h4 className="text-lg font-medium text-gray-800">{step.title}</h4>
                </div>
                
                <p className="text-gray-700 mb-4">{step.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {step.details.map((detail, idx) => (
                    <div key={idx} className="flex items-start">
                      <div className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-200 flex items-center justify-center mt-0.5 mr-2">
                        <span className="text-blue-700 text-xs">✓</span>
                      </div>
                      <span className="text-gray-600">{detail}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null
          ))}
        </div>
      )}
      
      {/* Module Selector */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Our Predictive Modules</h3>
        <div className="flex flex-wrap gap-3">
          {modules.map(module => (
            <button
              key={module.id}
              onClick={() => setExpandedModule(module.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors 
                ${expandedModule === module.id 
                  ? module.color === 'blue' 
                    ? 'bg-blue-600 text-white' 
                    : module.color === 'green' 
                      ? 'bg-green-600 text-white' 
                      : 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              {module.name}
            </button>
          ))}
        </div>
      </div>
      
      {/* Module Details */}
      {modules.map(module => (
        module.id === expandedModule ? (
          <div 
            key={module.id} 
            className={`p-5 rounded-lg border ${
              module.color === 'blue' 
                ? 'bg-blue-50 border-blue-200' 
                : module.color === 'green'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-purple-50 border-purple-200'
            }`}
          >
            <h3 className={`text-lg font-medium mb-3 ${
              module.color === 'blue' 
                ? 'text-blue-700' 
                : module.color === 'green'
                  ? 'text-green-700'
                  : 'text-purple-700'
            }`}>{module.name}</h3>
            
            <p className="text-gray-700 mb-4">{module.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Key Predictive Factors</h4>
                <ul className="space-y-1">
                  {module.keyFactors.map((factor, idx) => (
                    <li key={idx} className="flex items-start">
                      <div className={`flex-shrink-0 w-5 h-5 rounded-full ${
                        module.color === 'blue' 
                          ? 'bg-blue-100 text-blue-600' 
                          : module.color === 'green'
                            ? 'bg-green-100 text-green-600'
                            : 'bg-purple-100 text-purple-600'
                        } flex items-center justify-center mt-0.5 mr-2`}>
                        <span className="text-xs">•</span>
                      </div>
                      <span className="text-gray-600">{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Expected Outcomes</h4>
                <ul className="space-y-1">
                  {module.outcomes.map((outcome, idx) => (
                    <li key={idx} className="flex items-start">
                      <div className={`flex-shrink-0 w-5 h-5 rounded-full ${
                        module.color === 'blue' 
                          ? 'bg-blue-100 text-blue-600' 
                          : module.color === 'green'
                            ? 'bg-green-100 text-green-600'
                            : 'bg-purple-100 text-purple-600'
                        } flex items-center justify-center mt-0.5 mr-2`}>
                        <span className="text-xs">✓</span>
                      </div>
                      <span className="text-gray-600">{outcome}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ) : null
      ))}
      
      {/* Technical Notes */}
      <div className="mt-10 pt-6 border-t border-gray-200">
        <h3 className="text-md font-medium text-gray-700 mb-3">Platform Architecture</h3>
        <p className="text-sm text-gray-600">
          The PredictiveRx AI platform utilizes a unified machine learning architecture that powers all our predictive modules. 
          This shared foundation enables rapid deployment of new prediction models while maintaining consistent performance, 
          reliability, and security standards. Each application leverages the same core technology stack with domain-specific 
          data models and intervention frameworks tailored to the particular healthcare challenge.
        </p>
      </div>
    </div>
  );
};

export default PredictiveRxTechnology;
