import React, { useState, useEffect } from 'react';

const SimpleROICalculator = () => {
  // Initial state for inputs
  const [inputs, setInputs] = useState({
    centerSize: 'medium',
    annualVisits: 50000,
    currentNoShowRate: 0.25,
    revenuePerVisit: 150,
    expectedNoShowReduction: 0.30,
    implementationCost: 450000,
    annualMaintenanceCost: 95000
  });
  
  // State for calculated results
  const [results, setResults] = useState({
    appointmentsSaved: 0,
    directRevenue: 0,
    providerProductivity: 0,
    frontDeskEfficiency: 0,
    reducedOvertime: 0,
    improvedCollections: 0,
    payerMixOptimization: 0,
    patientRetention: 0,
    totalAnnualBenefit: 0,
    firstYearROI: 0,
    threeYearROI: 0,
    fiveYearROI: 0,
    paybackMonths: 0
  });
  
  // Update implementation costs when center size changes
  useEffect(() => {
    if (inputs.centerSize === 'small') {
      setInputs(prev => ({
        ...prev,
        annualVisits: 25000,
        implementationCost: 350000,
        annualMaintenanceCost: 75000
      }));
    } else if (inputs.centerSize === 'medium') {
      setInputs(prev => ({
        ...prev,
        annualVisits: 50000,
        implementationCost: 450000,
        annualMaintenanceCost: 95000
      }));
    } else if (inputs.centerSize === 'large') {
      setInputs(prev => ({
        ...prev,
        annualVisits: 100000,
        implementationCost: 650000,
        annualMaintenanceCost: 125000
      }));
    }
  }, [inputs.centerSize]);
  
  // Calculate ROI whenever inputs change
  useEffect(() => {
    calculateROI();
  }, [inputs]);
  
  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    
    // Parse input value based on type
    let parsedValue = value;
    
    if (type === 'number' || type === 'select-one') {
      parsedValue = parseFloat(value);
      
      // Convert percentage fields to decimals
      if (['currentNoShowRate', 'expectedNoShowReduction'].includes(name)) {
        parsedValue = parsedValue / 100;
      }
    }
    
    setInputs(prev => ({
      ...prev,
      [name]: parsedValue
    }));
  };
  
  // Calculate all ROI metrics
  const calculateROI = () => {
    // Calculate appointments saved
    const appointmentsSaved = Math.round(
      inputs.annualVisits * inputs.currentNoShowRate * inputs.expectedNoShowReduction
    );
    
    // Calculate direct revenue
    const directRevenue = appointmentsSaved * inputs.revenuePerVisit;
    
    // Calculate additional benefits
    
    // Provider productivity (value of time saved)
    const providerHourlyCost = 150;
    const avgApptLength = 0.5; // 30 minutes average appointment
    const providerProductivity = appointmentsSaved * avgApptLength * providerHourlyCost;
    
    // Front desk efficiency (reduced scheduling/rescheduling time)
    const staffHourlyCost = 25;
    const frontDeskTimePerNoShow = 0.33; // 20 minutes per no-show for follow-up
    const frontDeskEfficiency = appointmentsSaved * frontDeskTimePerNoShow * staffHourlyCost;
    
    // Reduced overtime (less schedule chaos means less overtime)
    const estimatedStaffFTE = inputs.annualVisits / 2500; // Rough estimate
    const otReductionHours = estimatedStaffFTE * 2 * inputs.expectedNoShowReduction;
    const reducedOvertime = otReductionHours * staffHourlyCost * 1.5; // OT at 1.5x
    
    // Improved collections (better scheduling means better collection opportunities)
    const collectionRateImprovement = 0.05; // 5%
    const improvedCollections = inputs.annualVisits * inputs.revenuePerVisit * collectionRateImprovement;
    
    // Payer mix optimization (better scheduling allows prioritization of higher-value appointments)
    const payerMixImprovement = 0.03; // 3%
    const payerMixOptimization = inputs.annualVisits * inputs.revenuePerVisit * payerMixImprovement;
    
    // Patient retention (better experience means less patient turnover)
    const patientRetentionValue = 100; // Value of retaining a patient
    const patientsRetained = inputs.annualVisits / 4 * inputs.expectedNoShowReduction * 0.2;
    const patientRetention = patientsRetained * patientRetentionValue;
    
    // Calculate total annual benefit
    const totalAnnualBenefit = directRevenue + providerProductivity + frontDeskEfficiency + 
                              reducedOvertime + improvedCollections + payerMixOptimization + 
                              patientRetention;
    
    // Calculate ROI
    const totalFirstYearCost = inputs.implementationCost + inputs.annualMaintenanceCost;
    const firstYearROI = (totalAnnualBenefit - totalFirstYearCost) / totalFirstYearCost;
    
    const totalThreeYearCost = inputs.implementationCost + (inputs.annualMaintenanceCost * 3);
    const threeYearROI = ((totalAnnualBenefit * 3) - totalThreeYearCost) / totalThreeYearCost;
    
    const totalFiveYearCost = inputs.implementationCost + (inputs.annualMaintenanceCost * 5);
    const fiveYearROI = ((totalAnnualBenefit * 5) - totalFiveYearCost) / totalFiveYearCost;
    
    // Calculate payback period in months
    const monthlyNetBenefit = (totalAnnualBenefit - inputs.annualMaintenanceCost) / 12;
    const paybackMonths = inputs.implementationCost / monthlyNetBenefit;
    
    // Update results
    setResults({
      appointmentsSaved,
      directRevenue,
      providerProductivity,
      frontDeskEfficiency,
      reducedOvertime,
      improvedCollections,
      payerMixOptimization,
      patientRetention,
      totalAnnualBenefit,
      firstYearROI,
      threeYearROI,
      fiveYearROI,
      paybackMonths
    });
  };
  
  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value);
  };
  
  // Format percentage
  const formatPercent = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      maximumFractionDigits: 1
    }).format(value);
  };
  
  return (
    <div className="p-4 max-w-6xl mx-auto">
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">VitalSchedule ROI Calculator</h1>
          <p className="mt-1 text-sm text-gray-500">Estimate the financial impact of reducing no-shows at your Community Health Center</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
          {/* Input Section */}
          <div className="md:col-span-1 space-y-6">
            {/* Health Center Parameters */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h2 className="text-lg font-medium text-gray-700 mb-4">Health Center Profile</h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Center Size
                </label>
                <select
                  name="centerSize"
                  value={inputs.centerSize}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  <option value="small">Small CHC (25,000 annual visits)</option>
                  <option value="medium">Medium CHC (50,000 annual visits)</option>
                  <option value="large">Large CHC (100,000 annual visits)</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Annual Visits
                </label>
                <input
                  type="number"
                  name="annualVisits"
                  value={inputs.annualVisits}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  disabled
                />
              </div>
            </div>
            
            {/* No-Show Parameters */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h2 className="text-lg font-medium text-gray-700 mb-4">No-Show Parameters</h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current No-Show Rate (%)
                </label>
                <input
                  type="number"
                  name="currentNoShowRate"
                  value={inputs.currentNoShowRate * 100}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  min="0"
                  max="100"
                  step="1"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Average Revenue Per Visit ($)
                </label>
                <input
                  type="number"
                  name="revenuePerVisit"
                  value={inputs.revenuePerVisit}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected No-Show Reduction (%)
                </label>
                <select
                  name="expectedNoShowReduction"
                  value={inputs.expectedNoShowReduction * 100}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  <option value="15">15% (Conservative)</option>
                  <option value="20">20%</option>
                  <option value="25">25%</option>
                  <option value="30">30% (Average)</option>
                  <option value="35">35%</option>
                  <option value="40">40% (Aggressive)</option>
                </select>
              </div>
            </div>
            
            {/* Implementation Parameters */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h2 className="text-lg font-medium text-gray-700 mb-4">Implementation Parameters</h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Implementation Cost ($)
                </label>
                <input
                  type="number"
                  name="implementationCost"
                  value={inputs.implementationCost}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  disabled
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Annual Maintenance Cost ($)
                </label>
                <input
                  type="number"
                  name="annualMaintenanceCost"
                  value={inputs.annualMaintenanceCost}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  disabled
                />
              </div>
            </div>
          </div>
          
          {/* Results Section */}
          <div className="md:col-span-2 space-y-6">
            {/* Summary Metrics */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-700">ROI Summary</h2>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 p-3 rounded-lg text-center">
                    <p className="text-sm text-gray-600">Annual Benefit</p>
                    <p className="text-xl font-bold text-blue-700">
                      {formatCurrency(results.totalAnnualBenefit)}
                    </p>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg text-center">
                    <p className="text-sm text-gray-600">Appointments Saved</p>
                    <p className="text-xl font-bold text-blue-700">
                      {results.appointmentsSaved.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg text-center">
                    <p className="text-sm text-gray-600">5-Year ROI</p>
                    <p className="text-xl font-bold text-green-700">
                      {formatPercent(results.fiveYearROI)}
                    </p>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg text-center">
                    <p className="text-sm text-gray-600">Payback Period</p>
                    <p className="text-xl font-bold text-green-700">
                      {Math.round(results.paybackMonths)} months
                    </p>
                  </div>
                </div>
                
                <div className="border-t border-gray-200 pt-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-xs text-gray-500">First Year ROI</p>
                      <p className="text-lg font-medium">
                        {formatPercent(results.firstYearROI)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Three Year ROI</p>
                      <p className="text-lg font-medium">
                        {formatPercent(results.threeYearROI)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Five Year ROI</p>
                      <p className="text-lg font-medium">
                        {formatPercent(results.fiveYearROI)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Detailed Benefits Breakdown */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-700">Benefits Breakdown</h2>
              </div>
              <div className="p-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Direct Revenue from Recovered Appointments</span>
                    <span className="text-sm font-medium">{formatCurrency(results.directRevenue)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Provider Productivity Improvement</span>
                    <span className="text-sm font-medium">{formatCurrency(results.providerProductivity)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Front Desk Efficiency Gains</span>
                    <span className="text-sm font-medium">{formatCurrency(results.frontDeskEfficiency)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Reduced Staff Overtime</span>
                    <span className="text-sm font-medium">{formatCurrency(results.reducedOvertime)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Improved Collection Rates</span>
                    <span className="text-sm font-medium">{formatCurrency(results.improvedCollections)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Better Payer Mix Management</span>
                    <span className="text-sm font-medium">{formatCurrency(results.payerMixOptimization)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 border-b">
                    <span className="text-sm">Patient Retention Value</span>
                    <span className="text-sm font-medium">{formatCurrency(results.patientRetention)}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50">
                    <span className="text-sm font-medium">Total Annual Benefit</span>
                    <span className="text-sm font-medium">{formatCurrency(results.totalAnnualBenefit)}</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* 5-Year Financial Projection */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-700">5-Year Financial Projection</h2>
              </div>
              <div className="p-4">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="text-left text-xs font-medium text-gray-500 pb-2">Year</th>
                      <th className="text-right text-xs font-medium text-gray-500 pb-2">Benefits</th>
                      <th className="text-right text-xs font-medium text-gray-500 pb-2">Costs</th>
                      <th className="text-right text-xs font-medium text-gray-500 pb-2">Net</th>
                      <th className="text-right text-xs font-medium text-gray-500 pb-2">Cumulative</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-t">
                      <td className="py-2 text-sm">Year 1</td>
                      <td className="py-2 text-right text-sm text-green-600">
                        {formatCurrency(results.totalAnnualBenefit)}
                      </td>
                      <td className="py-2 text-right text-sm text-red-600">
                        {formatCurrency(inputs.implementationCost + inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm">
                        {formatCurrency(results.totalAnnualBenefit - (inputs.implementationCost + inputs.annualMaintenanceCost))}
                      </td>
                      <td className="py-2 text-right text-sm font-medium">
                        {formatCurrency(results.totalAnnualBenefit - (inputs.implementationCost + inputs.annualMaintenanceCost))}
                      </td>
                    </tr>
                    <tr className="border-t">
                      <td className="py-2 text-sm">Year 2</td>
                      <td className="py-2 text-right text-sm text-green-600">
                        {formatCurrency(results.totalAnnualBenefit)}
                      </td>
                      <td className="py-2 text-right text-sm text-red-600">
                        {formatCurrency(inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm">
                        {formatCurrency(results.totalAnnualBenefit - inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm font-medium">
                        {formatCurrency(
                          (results.totalAnnualBenefit - (inputs.implementationCost + inputs.annualMaintenanceCost)) +
                          (results.totalAnnualBenefit - inputs.annualMaintenanceCost)
                        )}
                      </td>
                    </tr>
                    <tr className="border-t">
                      <td className="py-2 text-sm">Year 3</td>
                      <td className="py-2 text-right text-sm text-green-600">
                        {formatCurrency(results.totalAnnualBenefit)}
                      </td>
                      <td className="py-2 text-right text-sm text-red-600">
                        {formatCurrency(inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm">
                        {formatCurrency(results.totalAnnualBenefit - inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm font-medium">
                        {formatCurrency(
                          (results.totalAnnualBenefit - (inputs.implementationCost + inputs.annualMaintenanceCost)) +
                          (results.totalAnnualBenefit - inputs.annualMaintenanceCost) * 2
                        )}
                      </td>
                    </tr>
                    <tr className="border-t">
                      <td className="py-2 text-sm">Year 4</td>
                      <td className="py-2 text-right text-sm text-green-600">
                        {formatCurrency(results.totalAnnualBenefit)}
                      </td>
                      <td className="py-2 text-right text-sm text-red-600">
                        {formatCurrency(inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm">
                        {formatCurrency(results.totalAnnualBenefit - inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm font-medium">
                        {formatCurrency(
                          (results.totalAnnualBenefit - (inputs.implementationCost + inputs.annualMaintenanceCost)) +
                          (results.totalAnnualBenefit - inputs.annualMaintenanceCost) * 3
                        )}
                      </td>
                    </tr>
                    <tr className="border-t">
                      <td className="py-2 text-sm">Year 5</td>
                      <td className="py-2 text-right text-sm text-green-600">
                        {formatCurrency(results.totalAnnualBenefit)}
                      </td>
                      <td className="py-2 text-right text-sm text-red-600">
                        {formatCurrency(inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm">
                        {formatCurrency(results.totalAnnualBenefit - inputs.annualMaintenanceCost)}
                      </td>
                      <td className="py-2 text-right text-sm font-medium">
                        {formatCurrency(
                          (results.totalAnnualBenefit - (inputs.implementationCost + inputs.annualMaintenanceCost)) +
                          (results.totalAnnualBenefit - inputs.annualMaintenanceCost) * 4
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleROICalculator;
