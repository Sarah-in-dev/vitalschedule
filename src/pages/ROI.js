import React, { useState } from 'react';

const ROI = () => {
  const [activeCalculator, setActiveCalculator] = useState('noshow');
  const [showFullBenefits, setShowFullBenefits] = useState(true);

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

  // Calculate implementation costs using a non-linear scale to show economies of scale
  const calculateImplementationCost = (volume, basePrice, volumeFactor, maxDiscount) => {
    // Calculate discount percentage based on volume (capped at maxDiscount)
    // Using a logarithmic curve for smoother scaling
    const discount = Math.min(maxDiscount, Math.log10(volume / 1000) * 0.1);
    
    // Base price + (volume factor with discount)
    return Math.max(basePrice, basePrice + (volume * volumeFactor * (1 - discount)));
  };

  // No-Show Calculator Component
  const NoShowCalculator = () => {
    const [inputs, setInputs] = useState({
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
      // Direct revenue only calculations
      directRevenueROI: {
        firstYearROI: 0,
        threeYearROI: 0,
        fiveYearROI: 0,
        paybackMonths: 0
      },
      // Full benefits calculations
      fullBenefitsROI: {
        firstYearROI: 0,
        threeYearROI: 0,
        fiveYearROI: 0,
        paybackMonths: 0
      }
    });

    // Update implementation costs based on annual visits with non-linear scaling
    React.useEffect(() => {
      // Only update costs when component mounts
      // For visits: Base price = 200,000, volume factor = 5, max discount = 40%
      const suggestedImplementationCost = calculateImplementationCost(
        inputs.annualVisits, 200000, 5, 0.4
      );
      
      // For maintenance: Base price = 50,000, volume factor = 0.9, max discount = 35%
      const suggestedMaintenanceCost = calculateImplementationCost(
        inputs.annualVisits, 50000, 0.9, 0.35
      );
      
      setInputs(prev => ({
        ...prev,
        implementationCost: Math.round(suggestedImplementationCost),
        annualMaintenanceCost: Math.round(suggestedMaintenanceCost)
      }));
    }, []);
    
    // Calculate ROI whenever inputs change
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
    
    // Calculate all ROI metrics
    const calculateROI = () => {
      // Calculate appointments saved
      const appointmentsSaved = Math.round(
        inputs.annualVisits * (inputs.currentNoShowRate / 100) * (inputs.expectedReduction / 100)
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
      const otReductionHours = estimatedStaffFTE * 2 * (inputs.expectedReduction / 100);
      const reducedOvertime = otReductionHours * staffHourlyCost * 1.5; // OT at 1.5x
      
      // Improved collections (better scheduling means better collection opportunities)
      const collectionRateImprovement = 0.05; // 5%
      const improvedCollections = inputs.annualVisits * inputs.revenuePerVisit * collectionRateImprovement;
      
      // Payer mix optimization (better scheduling allows prioritization of higher-value appointments)
      const payerMixImprovement = 0.03; // 3%
      const payerMixOptimization = inputs.annualVisits * inputs.revenuePerVisit * payerMixImprovement;
      
      // Patient retention (better experience means less patient turnover)
      const patientRetentionValue = 100; // Value of retaining a patient
      const patientsRetained = inputs.annualVisits / 4 * (inputs.expectedReduction / 100) * 0.2;
      const patientRetention = patientsRetained * patientRetentionValue;
      
      // Calculate total annual benefit (all benefits)
      const totalAnnualBenefit = directRevenue + providerProductivity + frontDeskEfficiency + 
                            reducedOvertime + improvedCollections + payerMixOptimization + 
                            patientRetention;
      
      // Calculate implementation and maintenance costs
      const totalFirstYearCost = inputs.implementationCost + inputs.annualMaintenanceCost;
      
      // Calculate ROI based on direct revenue only
      const directRevenueROI = {
        firstYearROI: (directRevenue - totalFirstYearCost) / totalFirstYearCost,
        threeYearROI: ((directRevenue * 3) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 3))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 3)),
        fiveYearROI: ((directRevenue * 5) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 5))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 5)),
        paybackMonths: (directRevenue > inputs.annualMaintenanceCost) ? 
          (inputs.implementationCost / ((directRevenue - inputs.annualMaintenanceCost) / 12)) : 
          Number.POSITIVE_INFINITY
      };
      
      // Calculate ROI based on full benefits
      const fullBenefitsROI = {
        firstYearROI: (totalAnnualBenefit - totalFirstYearCost) / totalFirstYearCost,
        threeYearROI: ((totalAnnualBenefit * 3) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 3))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 3)),
        fiveYearROI: ((totalAnnualBenefit * 5) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 5))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 5)),
        paybackMonths: (totalAnnualBenefit > inputs.annualMaintenanceCost) ? 
          (inputs.implementationCost / ((totalAnnualBenefit - inputs.annualMaintenanceCost) / 12)) : 
          Number.POSITIVE_INFINITY
      };
      
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
        directRevenueROI,
        fullBenefitsROI
      });
    };
    
    // Calculate suggested implementation costs
    const suggestedImplementationCost = calculateImplementationCost(
      inputs.annualVisits, 200000, 5, 0.4
    );
    
    const suggestedMaintenanceCost = calculateImplementationCost(
      inputs.annualVisits, 50000, 0.9, 0.35
    );

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
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.round(suggestedImplementationCost))} based on your volume (economies of scale applied)</p>
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
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.round(suggestedMaintenanceCost))} based on your volume (economies of scale applied)</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="flex justify-between mb-2">
              <div className="text-sm font-medium text-gray-700">ROI Calculation View:</div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowFullBenefits(false)}
                  className={`px-3 py-1 text-xs rounded ${
                    !showFullBenefits
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  Direct Revenue Only
                </button>
                <button
                  onClick={() => setShowFullBenefits(true)}
                  className={`px-3 py-1 text-xs rounded ${
                    showFullBenefits
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  Full Benefits
                </button>
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">ROI Summary {!showFullBenefits && "(Direct Revenue Only)"}</h3>
              
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
                  <span className="font-bold">{formatCurrency(showFullBenefits ? results.totalAnnualBenefit : results.directRevenue)}</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-blue-100">
                  <span>5-Year ROI:</span>
                  <span className="font-bold text-green-600">{
                    formatPercent(showFullBenefits ? 
                      results.fullBenefitsROI.fiveYearROI : 
                      results.directRevenueROI.fiveYearROI)
                  }</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-blue-100">
                  <span>Payback Period:</span>
                  <span className="font-bold">
                    {
                      showFullBenefits ? 
                        (isFinite(results.fullBenefitsROI.paybackMonths) ? 
                          Math.round(results.fullBenefitsROI.paybackMonths) + " months" : 
                          "N/A") : 
                        (isFinite(results.directRevenueROI.paybackMonths) ? 
                          Math.round(results.directRevenueROI.paybackMonths) + " months" : 
                          "N/A")
                    }
                  </span>
                </div>
              </div>
            </div>
            
            {showFullBenefits && (
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
            )}
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">ROI Comparison</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="text-left text-xs font-medium text-gray-500 px-2">Metric</th>
                      <th className="text-center text-xs font-medium text-gray-500 px-2">Direct Revenue Only</th>
                      <th className="text-center text-xs font-medium text-gray-500 px-2">Full Benefits</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">Annual Benefit</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatCurrency(results.directRevenue)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatCurrency(results.totalAnnualBenefit)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">1-Year ROI</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.directRevenueROI.firstYearROI)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.fullBenefitsROI.firstYearROI)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">3-Year ROI</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.directRevenueROI.threeYearROI)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.fullBenefitsROI.threeYearROI)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">5-Year ROI</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.directRevenueROI.fiveYearROI)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.fullBenefitsROI.fiveYearROI)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">Payback Period</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">
                        {isFinite(results.directRevenueROI.paybackMonths) ? 
                          Math.round(results.directRevenueROI.paybackMonths) + " months" : 
                          "N/A"}
                      </td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">
                        {isFinite(results.fullBenefitsROI.paybackMonths) ? 
                          Math.round(results.fullBenefitsROI.paybackMonths) + " months" : 
                          "N/A"}
                      </td>
                    </tr>
                  </tbody>
                </table>
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
      // Direct savings only calculations
      directSavingsROI: {
        firstYearROI: 0,
        threeYearROI: 0,
        fiveYearROI: 0,
        paybackMonths: 0
      },
      // Full benefits calculations
      fullBenefitsROI: {
        firstYearROI: 0,
        threeYearROI: 0,
        fiveYearROI: 0,
        paybackMonths: 0
      }
    });

    // Update implementation costs based on annual discharges with non-linear scaling
    React.useEffect(() => {
      // Only update costs when component mounts
      // For implementation: Base price = 250,000, volume factor = 15, max discount = 45%
      const suggestedImplementationCost = calculateImplementationCost(
        inputs.annualDischarges, 250000, 15, 0.45
      );
      
      // For maintenance: Base price = 70,000, volume factor = 2.5, max discount = 40%
      const suggestedMaintenanceCost = calculateImplementationCost(
        inputs.annualDischarges, 70000, 2.5, 0.4
      );
      
      setInputs(prev => ({
        ...prev,
        implementationCost: Math.round(suggestedImplementationCost),
        annualMaintenanceCost: Math.round(suggestedMaintenanceCost)
      }));
    }, []);
    
    // Calculate ROI whenever inputs change
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
      
      // Calculate ROI based on direct savings only
      const totalFirstYearCost = inputs.implementationCost + inputs.annualMaintenanceCost;
      
      const directSavingsROI = {
        firstYearROI: (directSavings - totalFirstYearCost) / totalFirstYearCost,
        threeYearROI: ((directSavings * 3) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 3))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 3)),
        fiveYearROI: ((directSavings * 5) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 5))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 5)),
        paybackMonths: (directSavings > inputs.annualMaintenanceCost) ? 
          (inputs.implementationCost / ((directSavings - inputs.annualMaintenanceCost) / 12)) : 
          Number.POSITIVE_INFINITY
      };
      
      // Calculate ROI based on full benefits
      const fullBenefitsROI = {
        firstYearROI: (totalAnnualBenefit - totalFirstYearCost) / totalFirstYearCost,
        threeYearROI: ((totalAnnualBenefit * 3) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 3))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 3)),
        fiveYearROI: ((totalAnnualBenefit * 5) - (inputs.implementationCost + (inputs.annualMaintenanceCost * 5))) / (inputs.implementationCost + (inputs.annualMaintenanceCost * 5)),
        paybackMonths: (totalAnnualBenefit > inputs.annualMaintenanceCost) ? 
          (inputs.implementationCost / ((totalAnnualBenefit - inputs.annualMaintenanceCost) / 12)) : 
          Number.POSITIVE_INFINITY
      };
      
      // Update results
      setResults({
        readmissionsAvoided,
        directSavings,
        bedDaysFreed,
        bedDaysValue,
        staffProductivity,
        qualityImprovementValue,
        totalAnnualBenefit,
        directSavingsROI,
        fullBenefitsROI
      });
    };
    
    // Calculate suggested implementation costs
    const suggestedImplementationCost = calculateImplementationCost(
      inputs.annualDischarges, 250000, 15, 0.45
    );
    
    const suggestedMaintenanceCost = calculateImplementationCost(
      inputs.annualDischarges, 70000, 2.5, 0.4
    );

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
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.round(suggestedImplementationCost))} based on your volume (economies of scale applied)</p>
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
              <p className="text-xs text-gray-500 mt-1">Suggested: {formatCurrency(Math.round(suggestedMaintenanceCost))} based on your volume (economies of scale applied)</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="flex justify-between mb-2">
              <div className="text-sm font-medium text-gray-700">ROI Calculation View:</div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowFullBenefits(false)}
                  className={`px-3 py-1 text-xs rounded ${
                    !showFullBenefits
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  Direct Savings Only
                </button>
                <button
                  onClick={() => setShowFullBenefits(true)}
                  className={`px-3 py-1 text-xs rounded ${
                    showFullBenefits
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  Full Benefits
                </button>
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">ROI Summary {!showFullBenefits && "(Direct Savings Only)"}</h3>
              
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
                  <span className="font-bold">{formatCurrency(showFullBenefits ? results.totalAnnualBenefit : results.directSavings)}</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-green-100">
                  <span>5-Year ROI:</span>
                  <span className="font-bold text-green-600">{
                    formatPercent(showFullBenefits ? 
                      results.fullBenefitsROI.fiveYearROI : 
                      results.directSavingsROI.fiveYearROI)
                  }</span>
                </div>
                
                <div className="flex justify-between text-sm p-2 bg-white rounded border border-green-100">
                  <span>Payback Period:</span>
                  <span className="font-bold">
                    {
                      showFullBenefits ? 
                        (isFinite(results.fullBenefitsROI.paybackMonths) ? 
                          Math.round(results.fullBenefitsROI.paybackMonths) + " months" : 
                          "N/A") : 
                        (isFinite(results.directSavingsROI.paybackMonths) ? 
                          Math.round(results.directSavingsROI.paybackMonths) + " months" : 
                          "N/A")
                    }
                  </span>
                </div>
              </div>
            </div>
            
            {showFullBenefits && (
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
            )}
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium mb-3">ROI Comparison</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="text-left text-xs font-medium text-gray-500 px-2">Metric</th>
                      <th className="text-center text-xs font-medium text-gray-500 px-2">Direct Savings Only</th>
                      <th className="text-center text-xs font-medium text-gray-500 px-2">Full Benefits</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">Annual Benefit</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatCurrency(results.directSavings)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatCurrency(results.totalAnnualBenefit)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">1-Year ROI</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.directSavingsROI.firstYearROI)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.fullBenefitsROI.firstYearROI)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">3-Year ROI</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.directSavingsROI.threeYearROI)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.fullBenefitsROI.threeYearROI)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">5-Year ROI</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.directSavingsROI.fiveYearROI)}</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">{formatPercent(results.fullBenefitsROI.fiveYearROI)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-sm font-medium text-gray-900 px-2">Payback Period</td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">
                        {isFinite(results.directSavingsROI.paybackMonths) ? 
                          Math.round(results.directSavingsROI.paybackMonths) + " months" : 
                          "N/A"}
                      </td>
                      <td className="py-2 text-center text-sm text-gray-700 px-2">
                        {isFinite(results.fullBenefitsROI.paybackMonths) ? 
                          Math.round(results.fullBenefitsROI.paybackMonths) + " months" : 
                          "N/A"}
                      </td>
                    </tr>
                  </tbody>
                </table>
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
          These calculators provide estimates based on industry benchmarks and our implementation experience. You can toggle between "Direct Revenue Only" for a conservative estimate based solely on direct financial impact, or "Full Benefits" to include operational efficiencies and other indirect benefits.
        </p>
        <p className="text-gray-700 mb-4">
          Our pricing model includes economies of scale, with larger facilities benefiting from proportionally lower costs per visit or discharge.
        </p>
        <p className="text-gray-700">
          For a detailed, customized ROI analysis tailored to your specific organization, please contact our team for a consultation.
        </p>
      </div>
    </div>
  );
};

export default ROI;
