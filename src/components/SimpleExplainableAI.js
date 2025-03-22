import React, { useState } from 'react';

const SimpleExplainableAI = () => {
  const [activeTab, setActiveTab] = useState('factors');
  const [selectedCase, setSelectedCase] = useState('high');
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  
  // Sample case data
  const cases = {
    high: {
      id: 'P-1234',
      title: 'High Risk Case',
      score: 78,
      factors: [
        { name: 'History patterns', value: 35, description: 'Multiple previous instances' },
        { name: 'Clinical complexity', value: 23, description: '6+ medications, 3 chronic conditions' },
        { name: 'Access barriers', value: 15, description: 'Transportation limitations' },
        { name: 'Timing', value: 5, description: 'Monday morning appointment' }
      ],
      interventions: [
        { name: 'Transportation assistance', impact: -28, certainty: 'high' },
        { name: 'Preparation call', impact: -15, certainty: 'medium' },
        { name: 'Reminder sequence', impact: -12, certainty: 'high' }
      ],
      similarCases: 156,
      confidence: 85
    },
    medium: {
      id: 'P-5678',
      title: 'Medium Risk Case',
      score: 52,
      factors: [
        { name: 'Clinical complexity', value: 22, description: '4 medications, 2 chronic conditions' },
        { name: 'History patterns', value: 18, description: 'One previous instance' },
        { name: 'Lead time', value: 12, description: 'Scheduled 28 days in advance' }
      ],
      interventions: [
        { name: 'Phone reminder', impact: -18, certainty: 'high' },
        { name: 'Rescheduling', impact: -22, certainty: 'medium' }
      ],
      similarCases: 214,
      confidence: 78
    },
    low: {
      id: 'P-9012',
      title: 'Low Risk Case',
      score: 23,
      factors: [
        { name: 'Lead time', value: 10, description: 'Scheduled 14 days in advance' },
        { name: 'History patterns', value: 8, description: 'No previous instances' },
        { name: 'Timing', value: 5, description: 'Tuesday afternoon appointment' }
      ],
      interventions: [
        { name: 'Standard reminder', impact: -8, certainty: 'high' }
      ],
      similarCases: 389,
      confidence: 91
    }
  };
  
  // Get active case
  const activeCase = cases[selectedCase];
  
  // Helper functions for styling
  const getRiskColor = (score) => {
    if (score < 30) return 'bg-green-600';
    if (score < 60) return 'bg-yellow-500';
    return 'bg-red-600';
  };
  
  const getTextColor = (score) => {
    if (score < 30) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getLightBgColor = (score) => {
    if (score < 30) return 'bg-green-50';
    if (score < 60) return 'bg-yellow-50';
    return 'bg-red-50';
  };
  
  // Calculate updated risk score
  const calculateUpdatedScore = () => {
    if (!selectedIntervention) return activeCase.score;
    
    const intervention = activeCase.interventions.find(i => i.name === selectedIntervention);
    return Math.max(0, activeCase.score + (intervention ? intervention.impact : 0));
  };
  
  return (
    <div className="p-6 max-w-6xl mx-auto bg-white shadow rounded-lg">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-800">Explainable AI Technology</h2>
        <p className="text-gray-600 mt-2">
          Transparent insights into how our system generates predictions and recommends interventions
        </p>
      </div>
      
      {/* Case Selector */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Example Cases</h3>
        <div className="flex flex-wrap gap-3">
          {Object.entries(cases).map(([key, caseData]) => (
            <button
              key={key}
              onClick={() => {
                setSelectedCase(key);
                setSelectedIntervention(null);
              }}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCase === key
                  ? getRiskColor(caseData.score) + ' text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {caseData.title}
            </button>
          ))}
        </div>
      </div>
      
      {/* Natural Language Explanation */}
      <div className={`p-4 rounded-lg border mb-6 ${getLightBgColor(activeCase.score)}`}>
        <p className="text-gray-700">
          {selectedIntervention ? (
            <>
              The risk would decrease from <strong>{activeCase.score}%</strong> to <strong>{calculateUpdatedScore()}%</strong> if <strong>{selectedIntervention}</strong> is implemented. 
              This intervention addresses key risk factors and has been effective for similar cases.
            </>
          ) : (
            <>
              This case has a <strong>{activeCase.score}%</strong> risk score based on patterns observed in <strong>{activeCase.similarCases}</strong> similar 
              cases with <strong>{activeCase.confidence}%</strong> confidence.
            </>
          )}
        </p>
      </div>
      
      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('factors')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'factors'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Factor Breakdown
          </button>
          <button
            onClick={() => setActiveTab('what-if')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'what-if'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            What-If Analysis
          </button>
          <button
            onClick={() => setActiveTab('similar')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'similar'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Similar Cases
          </button>
          <button
            onClick={() => setActiveTab('uncertainty')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'uncertainty'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Uncertainty
          </button>
        </div>
      </div>
      
      {/* Factor Breakdown Tab */}
      {activeTab === 'factors' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Risk Score */}
          <div className="md:col-span-1">
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Overall Risk Score</h3>
              <div className="flex justify-center mb-4">
                <div className={`w-32 h-32 rounded-full ${getLightBgColor(activeCase.score)} border flex items-center justify-center`}>
                  <span className={`text-4xl font-bold ${getTextColor(activeCase.score)}`}>{activeCase.score}%</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 text-center">
                ID: {activeCase.id}<br />
                Based on {activeCase.similarCases} similar cases<br />
                {activeCase.confidence}% confidence
              </p>
            </div>
          </div>
          
          {/* Factor Analysis */}
          <div className="md:col-span-2">
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Factor Contribution Analysis</h3>
              
              <div className="space-y-4">
                {activeCase.factors.map(factor => (
                  <div key={factor.name} className="relative">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{factor.name}</span>
                      <span className="text-sm font-medium text-gray-700">{factor.value}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className="h-2.5 rounded-full bg-blue-600" 
                        style={{ width: `${(factor.value / activeCase.score) * 100}%` }}
                      ></div>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">{factor.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* What-If Analysis Tab */}
      {activeTab === 'what-if' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Score Comparison */}
          <div className="md:col-span-1">
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Risk Score Comparison</h3>
              
              <div className="flex justify-between items-center space-x-4 mb-6">
                {/* Current Score */}
                <div className="text-center">
                  <p className="text-sm text-gray-500 mb-2">Current</p>
                  <div className={`w-20 h-20 rounded-full ${getLightBgColor(activeCase.score)} border flex items-center justify-center mx-auto`}>
                    <span className={`text-xl font-bold ${getTextColor(activeCase.score)}`}>{activeCase.score}%</span>
                  </div>
                </div>
                
                {/* Arrow */}
                <div className="text-gray-400">→</div>
                
                {/* New Score */}
                <div className="text-center">
                  <p className="text-sm text-gray-500 mb-2">With Intervention</p>
                  <div className={`w-20 h-20 rounded-full ${getLightBgColor(calculateUpdatedScore())} border flex items-center justify-center mx-auto`}>
                    <span className={`text-xl font-bold ${getTextColor(calculateUpdatedScore())}`}>{calculateUpdatedScore()}%</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded text-sm text-gray-600">
                {selectedIntervention ? (
                  <p>
                    Applying <strong>{selectedIntervention}</strong> would reduce the risk score by approximately 
                    <strong className="text-green-600"> {Math.abs(activeCase.interventions.find(i => i.name === selectedIntervention)?.impact || 0)}%</strong>.
                  </p>
                ) : (
                  <p>Select an intervention to see its potential impact on the risk score.</p>
                )}
              </div>
            </div>
          </div>
          
          {/* Intervention Selection */}
          <div className="md:col-span-2">
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Select Intervention to Simulate</h3>
              
              <div className="space-y-4">
                {activeCase.interventions.map(intervention => (
                  <div 
                    key={intervention.name}
                    onClick={() => setSelectedIntervention(
                      selectedIntervention === intervention.name ? null : intervention.name
                    )}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedIntervention === intervention.name 
                        ? 'border-blue-400 bg-blue-50' 
                        : 'border-gray-200 hover:border-blue-200 hover:bg-blue-50'
                    }`}
                  >
                    <div className="flex justify-between mb-1">
                      <span className="font-medium text-gray-700">{intervention.name}</span>
                      <span className="text-green-600 font-medium">{intervention.impact}%</span>
                    </div>
                    
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>Impact on risk score</span>
                      <span>Certainty: {intervention.certainty}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Similar Cases Tab */}
      {activeTab === 'similar' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="md:col-span-1">
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Similar Case Summary</h3>
              <div className="space-y-4">
                <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                  <p className="text-sm text-gray-700 mb-2">
                    This prediction is based on patterns observed in <strong>{activeCase.similarCases}</strong> similar cases.
                  </p>
                  <p className="text-sm text-gray-600">
                    Our model achieved high accuracy in predicting outcomes for cases with these characteristics.
                  </p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Key Similarity Factors:</h4>
                  <ul className="text-sm text-gray-600 space-y-1 list-disc pl-5">
                    {activeCase.factors.slice(0, 3).map(factor => (
                      <li key={factor.name}>{factor.name}: {factor.description}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          <div className="md:col-span-2">
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Anonymous Similar Cases</h3>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Case ID</th>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key Factors</th>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Predicted</th>
                      <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actual</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {[...Array(3)].map((_, idx) => (
                      <tr key={idx} className="text-sm">
                        <td className="px-3 py-2 whitespace-nowrap text-gray-900 font-medium">Case #{Math.floor(Math.random() * 9000) + 1000}</td>
                        <td className="px-3 py-2 text-gray-500">
                          {activeCase.factors[0].name}, {activeCase.factors[1].name}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${getLightBgColor(activeCase.score)} ${getTextColor(activeCase.score)}`}>
                            {activeCase.score}%
                          </span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700">
                            {idx % 3 === 0 ? 'False' : 'True'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="text-center mt-4">
                <p className="text-sm text-gray-500">Showing 3 of {activeCase.similarCases} similar cases</p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Uncertainty Tab */}
      {activeTab === 'uncertainty' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Prediction Confidence</h3>
              
              <div className="mb-6">
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Confidence Level</span>
                  <span className="text-sm font-medium text-gray-700">{activeCase.confidence}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="h-2.5 rounded-full bg-blue-600" 
                    style={{ width: `${activeCase.confidence}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700">Confidence Factors</h4>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Data completeness</span>
                  <span className="font-medium text-gray-700">High</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Similar historical cases</span>
                  <span className="font-medium text-gray-700">{activeCase.similarCases} cases</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Model validation performance</span>
                  <span className="font-medium text-gray-700">Good</span>
                </div>
              </div>
            </div>
          </div>
          
          <div>
            <div className="bg-white border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Prediction Range</h3>
              
              <div className="bg-blue-50 p-4 rounded-lg mb-4">
                <p className="text-sm text-gray-700">
                  <strong>Risk score:</strong> {activeCase.score}% (±{Math.round((100 - activeCase.confidence) / 2)}%)
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  There is a 95% probability that the true risk falls between {
                    Math.max(0, activeCase.score - Math.round((100 - activeCase.confidence) / 2))
                  }% and {
                    Math.min(100, activeCase.score + Math.round((100 - activeCase.confidence) / 2))
                  }%.
                </p>
              </div>
              
              <div className="p-4 border rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Uncertainty Considerations</h4>
                <p className="text-sm text-gray-600">
                  While this prediction has {activeCase.confidence}% confidence overall, specific factors may have 
                  different levels of certainty. Interventions marked with "medium" certainty may have more variable 
                  outcomes than those with "high" certainty.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Technology Explanation Section */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-medium text-gray-700 mb-4">How Our Explainable AI Works</h3>
        <p className="text-gray-600 mb-4">
          Unlike "black box" AI systems, PredictiveRx's technology makes its reasoning transparent. Our explainable AI approach 
          allows healthcare professionals to understand exactly why a prediction was made and what factors contributed to it.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Factor Attribution</h4>
            <p className="text-gray-600">
              We use advanced techniques like SHAP (SHapley Additive exPlanations) values to quantify how each factor 
              contributes to a prediction, enabling targeted interventions.
            </p>
          </div>
          
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Confidence Metrics</h4>
            <p className="text-gray-600">
              Our system measures and communicates uncertainty, helping users understand when predictions are highly reliable 
              versus when they should be considered with more caution.
            </p>
          </div>
          
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Case-Based Reasoning</h4>
            <p className="text-gray-600">
              By showing similar historical cases, we provide context for predictions and build trust by demonstrating the 
              system's reasoning and past performance.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleExplainableAI;
