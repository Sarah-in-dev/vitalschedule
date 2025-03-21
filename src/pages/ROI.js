import React, { useState } from 'react';

const ROI = () => {
  const [activeCalculator, setActiveCalculator] = useState('noshow');

  // Common components and functions for both calculators
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value);
  };
  
  const formatPercent = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      maximumFractionDigits: 1
    }).format(value);
  };

  // No-Show Calculator Component
  const NoShowCalculator = () => {
    const [inputs, setInputs] = useState({
      centerSize: 'medium',
      annualVisits: 50000,
      currentNoShowRate: 25,
      revenuePerVisit: 150,
      expectedReduction: 30,
      implementationCost: 450000,
      annualMaintenanceCost: 95000
    });
    
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

    // Update implementation costs based on annual visits
    React.useEffect(() => {
      // Only update costs if visits change and the user hasn't manually adjusted costs
      const suggestedImplementationCost = Math.max(250000, inputs.annualVisits * 7);
      const suggestedMaintenanceCost = Math.max(60000, inputs.annualVisits * 1.8);
      
      setInputs(prev => ({
        ...prev,
        implementationCost: suggestedImplementationCost,
        annualMaintenanceCost: suggestedMaintenanceCost
      }));
    }, []);
    
    // Calculate ROI on input change
    React.useEffect(() => {
      calculateROI();
    }, [inputs]);
    
    // Handle input changes
    const handleInputChange = (e) => {
      const { name, value, type } = e.target;
      let parsedValue = value;
      
      if (type === 'number') {
        parsedValue = parseFloat(value) || 0;
      }
      
      setInputs(prev => ({
        ...prev,
        [name]: parsedValue
      }));
    };
    
    // Calculate ROI metrics
    const calculateROI = () => {
      // Calculate appointments saved
      const appointmentsSaved = Math.round(
        inputs.annualVisits * (inputs.currentNoShowRate / 100) * (inputs.expectedReduction / 100)
      );
      
      // Calculate direct revenue
      const directRevenue = appointmentsSaved * inputs.revenuePerVisit;
      
      // Calculate additional benefits
      const providerHourlyCost = 150;
      const avgApptLength = 0.5; // 30 minutes average appointment
      const providerProductivity = appointmentsSaved * avgApptLength * providerHourlyCost;
      
      const staffHourlyCost = 25;
      const frontDeskTimePerNoShow = 0.33; // 20 minutes per no-show for follow-up
      const frontDeskEfficiency = appointmentsSaved * frontDeskTimePerNoShow * staffHourlyCost;
      
      const estimatedStaffFTE = inputs.annualVisits / 2500; // Rough estimate
      const otReductionHours = estimatedStaffFTE * 2 * (inputs.expectedReduction / 100);
      const reducedOvertime = otReductionHours * staffHourlyCost * 1.5; // OT at 1.5x
      
      const collectionRateImprovement = 0.05; // 5%
      const improvedCollections = inputs.annualVisits * inputs.revenuePerVisit * collectionRateImprovement;
      
      const payerMixImprovement = 0.03; // 3%
      const payerMixOptimization = inputs.annualVisits * inputs.revenuePerVisit * payerMixImprovement;
      
      const patientRetentionValue = 100; // Value of retaining a patient
      const patientsRetained = inputs.annualVisits / 4 * (inputs.expectedReduction / 100) * 0.2;
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

    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-medium mb-4">No-Show Reduction ROI Calculator</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Annual Visits
              </label>
              <input
                type="number"
                name="annualVisits"
                value={inputs.annualVisits}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="1000"
                step="1000"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current No-Show Rate (%)
              </label>
              <input
                type="number"
                name="currentNoShowRate"
                value={inputs.currentNoShowRate}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                max="100"
                step="1"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Revenue Per Visit ($)
              </label>
              <input
                type="number"
                name="revenuePerVisit"
                value={inputs.revenuePerVisit}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                step="10"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expected No-Show Reduction (%)
              </label>
              <input
                type="number"
                name="expectedReduction"
                value={inputs.expectedReduction}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                max="100"
                step="5"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Implementation Cost ($)
              </label>
              <input
                type="number"
                name="implementationCost"
                value={inputs.implementationCost}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                step="10000"
              />
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.max(250000, inputs.annualVisits * 7))} based on your volume</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Annual Maintenance Cost ($)
              </label>
              <input
                type="number"
                name="annualMaintenanceCost"
                value={inputs.annualMaintenanceCost}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                step="5000"
              />
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.max(60000, inputs.annualVisits * 1.8))} based on your volume</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">ROI Summary</h3>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-white p-3 rounded-lg border border-blue-100">
                  <p className="text-sm text-gray-600">Appointments Saved</p>
                  <p className="text-xl font-bold text-blue-700">{results.appointmentsSaved.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">annually</p>
                </div>
                
                <div className="bg-white p-3 rounded-lg border border-blue-100">
                  <p className="text-sm text-gray-600">Direct Revenue</p>
                  <p className="text-xl font-bold text-blue-700">{formatCurrency(results.directRevenue)}</p>
                  <p className="text-xs text-gray-500">annually</p>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-blue-100">
                  <span>Total Annual Benefit:</span>
                  <span className="font-bold">{formatCurrency(results.totalAnnualBenefit)}</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-blue-100">
                  <span>5-Year ROI:</span>
                  <span className="font-bold text-green-600">{formatPercent(results.fiveYearROI)}</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-blue-100">
                  <span>Payback Period:</span>
                  <span className="font-bold">{Math.round(results.paybackMonths)} months</span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Benefits Breakdown</h3>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Direct Revenue:</span>
                  <span>{formatCurrency(results.directRevenue)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Provider Productivity:</span>
                  <span>{formatCurrency(results.providerProductivity)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Front Desk Efficiency:</span>
                  <span>{formatCurrency(results.frontDeskEfficiency)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Reduced Overtime:</span>
                  <span>{formatCurrency(results.reducedOvertime)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Improved Collections:</span>
                  <span>{formatCurrency(results.improvedCollections)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Payer Mix Optimization:</span>
                  <span>{formatCurrency(results.payerMixOptimization)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Patient Retention Value:</span>
                  <span>{formatCurrency(results.patientRetention)}</span>
                </div>
                
                <div className="flex justify-between text-sm font-medium pt-2 border-t">
                  <span>Total Annual Benefit:</span>
                  <span>{formatCurrency(results.totalAnnualBenefit)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Readmission Calculator Component
  const ReadmissionCalculator = () => {
    const [inputs, setInputs] = useState({
      hospitalSize: 'medium',
      annualDischarges: 15000,
      readmissionRate: 15,
      costPerReadmission: 12000,
      expectedReduction: 20,
      implementationCost: 480000,
      annualMaintenanceCost: 110000
    });
    
    const [results, setResults] = useState({
      readmissionsAvoided: 0,
      directSavings: 0,
      bedDaysFreed: 0,
      bedDaysValue: 0,
      staffProductivity: 0,
      qualityImprovementValue: 0,
      totalAnnualBenefit: 0,
      firstYearROI: 0,
      threeYearROI: 0,
      fiveYearROI: 0,
      paybackMonths: 0
    });

    // Update implementation costs based on annual discharges
    React.useEffect(() => {
      // Only update costs when component mounts
      const suggestedImplementationCost = Math.max(300000, inputs.annualDischarges * 28);
      const suggestedMaintenanceCost = Math.max(80000, inputs.annualDischarges * 7);
      
      setInputs(prev => ({
        ...prev,
        implementationCost: suggestedImplementationCost,
        annualMaintenanceCost: suggestedMaintenanceCost
      }));
    }, []);
    
    // Calculate ROI on input change
    React.useEffect(() => {
      calculateROI();
    }, [inputs]);
    
    // Handle input changes
    const handleInputChange = (e) => {
      const { name, value, type } = e.target;
      let parsedValue = value;
      
      if (type === 'number') {
        parsedValue = parseFloat(value) || 0;
      }
      
      setInputs(prev => ({
        ...prev,
        [name]: parsedValue
      }));
    };
    
    // Calculate ROI metrics
    const calculateROI = () => {
      // Calculate readmissions avoided
      const readmissionsAvoided = Math.round(
        inputs.annualDischarges * (inputs.readmissionRate / 100) * (inputs.expectedReduction / 100)
      );
      
      // Calculate direct cost savings
      const directSavings = readmissionsAvoided * inputs.costPerReadmission;
      
      // Calculate additional benefits
      const avgLOS = 4.5; // Average length of stay
      const bedDaysFreed = readmissionsAvoided * avgLOS;
      
      // Value of freed bed days (average revenue per bed day)
      const revPerBedDay = 1800;
      const bedDaysValue = bedDaysFreed * revPerBedDay;
      
      // Staff productivity (time saved not managing readmissions)
      const staffHoursPerReadmission = 8; // nursing, case management, etc.
      const staffHourlyRate = 60; // blended rate
      const staffProductivity = readmissionsAvoided * staffHoursPerReadmission * staffHourlyRate;
      
      // Quality improvement value (penalties avoided, better ratings)
      const qualityImprovementValue = directSavings * 0.15;
      
      // Calculate total annual benefit
      const totalAnnualBenefit = directSavings + bedDaysValue + staffProductivity + qualityImprovementValue;
      
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
        readmissionsAvoided,
        directSavings,
        bedDaysFreed,
        bedDaysValue,
        staffProductivity,
        qualityImprovementValue,
        totalAnnualBenefit,
        firstYearROI,
        threeYearROI,
        fiveYearROI,
        paybackMonths
      });
    };

    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-medium mb-4">Readmission Reduction ROI Calculator</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Annual Discharges
              </label>
              <input
                type="number"
                name="annualDischarges"
                value={inputs.annualDischarges}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="1000"
                step="1000"
              />
              <p className="text-xs text-gray-500 mt-1">
                Typical ranges: Small (5,000-10,000), Medium (10,000-20,000), Large (20,000+)
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Readmission Rate (%)
              </label>
              <input
                type="number"
                name="readmissionRate"
                value={inputs.readmissionRate}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                max="100"
                step="0.5"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Average Cost Per Readmission ($)
              </label>
              <input
                type="number"
                name="costPerReadmission"
                value={inputs.costPerReadmission}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                step="500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Industry average: $10,000-$15,000 depending on case mix
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expected Readmission Reduction (%)
              </label>
              <input
                type="number"
                name="expectedReduction"
                value={inputs.expectedReduction}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                max="100"
                step="5"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Implementation Cost ($)
              </label>
              <input
                type="number"
                name="implementationCost"
                value={inputs.implementationCost}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                step="10000"
              />
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.max(300000, inputs.annualDischarges * 28))} based on your volume</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Annual Maintenance Cost ($)
              </label>
              <input
                type="number"
                name="annualMaintenanceCost"
                value={inputs.annualMaintenanceCost}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
                min="0"
                step="5000"
              />
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.max(80000, inputs.annualDischarges * 7))} based on your volume</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">ROI Summary</h3>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-white p-3 rounded-lg border border-green-100">
                  <p className="text-sm text-gray-600">Readmissions Avoided</p>
                  <p className="text-xl font-bold text-green-700">{results.readmissionsAvoided.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">annually</p>
                </div>
                
                <div className="bg-white p-3 rounded-lg border border-green-100">
                  <p className="text-sm text-gray-600">Direct Cost Savings</p>
                  <p className="text-xl font-bold text-green-700">{formatCurrency(results.directSavings)}</p>
                  <p className="text-xs text-gray-500">annually</p>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-green-100">
                  <span>Total Annual Benefit:</span>
                  <span className="font-bold">{formatCurrency(results.totalAnnualBenefit)}</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-green-100">
                  <span>5-Year ROI:</span>
                  <span className="font-bold text-green-600">{formatPercent(results.fiveYearROI)}</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-green-100">
                  <span>Payback Period:</span>
                  <span className="font-bold">{Math.round(results.paybackMonths)} months</span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">Benefits Breakdown</h3>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Direct Cost Savings:</span>
                  <span>{formatCurrency(results.directSavings)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Bed Days Freed Up:</span>
                  <span>{results.bedDaysFreed.toLocaleString()} days</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Value of Freed Bed Days:</span>
                  <span>{formatCurrency(results.bedDaysValue)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Staff Productivity:</span>
                  <span>{formatCurrency(results.staffProductivity)}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Quality Improvement Value:</span>
                  <span>{formatCurrency(results.qualityImprovementValue)}</span>
                </div>
                
                <div className="flex justify-between text-sm font-medium pt-2 border-t">
                  <span>Total Annual Benefit:</span>
                  <span>{formatCurrency(results.totalAnnualBenefit)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-3xl font-bold my-6">VitalSchedule ROI Calculator</h1>
      <p className="mb-6 text-gray-600">
        Estimate the financial impact of our AI-powered healthcare solutions. Choose a module below to see its specific ROI calculation.
      </p>
      
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setActiveCalculator('noshow')}
          className={`px-4 py-2 rounded-md ${
            activeCalculator === 'noshow'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
          }`}
        >
          No-Show Reduction
        </button>
        <button
          onClick={() => setActiveCalculator('readmission')}
          className={`px-4 py-2 rounded-md ${
            activeCalculator === 'readmission'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
          }`}
        >
          Readmission Reduction
        </button>
      </div>
      
      {activeCalculator === 'noshow' ? (
        <NoShowCalculator />
      ) : activeCalculator === 'readmission' ? (
        <ReadmissionCalculator />
      ) : null}
      
      <div className="mt-8 bg-gray-50 p-4 rounded-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-2">About Our ROI Calculations</h2>
        <p className="text-gray-700 mb-4">
          These calculators provide estimates based on industry benchmarks and our implementation experience. Actual results may vary based on your specific environment, patient population, and implementation details.
        </p>
        <p className="text-gray-700">
          For a detailed, customized ROI analysis tailored to your specific organization, please contact our team for a consultation.
        </p>
      </div>
    </div>
  );
};

export default ROI;
