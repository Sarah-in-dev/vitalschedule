import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class ROICalculator:
    def __init__(self):
        # Default parameters
        self.avg_appointment_value = 150
        self.cost_per_no_show = 50  # Administrative cost of a no-show
        self.provider_idle_cost = 100  # Cost of provider idle time per hour
        self.baseline_no_show_rate = 0.25  # 25% no-show rate
        
    def set_parameters(self, **kwargs):
        """
        Update ROI calculation parameters
        
        Parameters:
        -----------
        kwargs : dict
            Parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        return self
    
    def calculate_baseline_costs(self, num_appointments):
        """
        Calculate baseline costs with current no-show rate
        
        Parameters:
        -----------
        num_appointments : int
            Number of appointments per year
            
        Returns:
        --------
        dict
            Baseline cost breakdown
        """
        expected_no_shows = num_appointments * self.baseline_no_show_rate
        expected_attended = num_appointments - expected_no_shows
        
        revenue = expected_attended * self.avg_appointment_value
        no_show_costs = expected_no_shows * self.cost_per_no_show
        idle_costs = expected_no_shows * self.provider_idle_cost
        
        return {
            'total_appointments': num_appointments,
            'expected_no_shows': expected_no_shows,
            'expected_attended': expected_attended,
            'revenue': revenue,
            'no_show_costs': no_show_costs,
            'idle_costs': idle_costs,
            'net_value': revenue - no_show_costs - idle_costs
        }
    
    def calculate_improved_scenario(self, num_appointments, no_show_reduction, implementation_cost, annual_cost):
        """
        Calculate costs and benefits with reduced no-show rate
        
        Parameters:
        -----------
        num_appointments : int
            Number of appointments per year
        no_show_reduction : float
            Percentage reduction in no-shows (0-1)
        implementation_cost : float
            One-time implementation cost
        annual_cost : float
            Annual maintenance cost
            
        Returns:
        --------
        dict
            Improved scenario breakdown
        """
        baseline = self.calculate_baseline_costs(num_appointments)
        
        new_no_show_rate = self.baseline_no_show_rate * (1 - no_show_reduction)
        expected_no_shows = num_appointments * new_no_show_rate
        expected_attended = num_appointments - expected_no_shows
        
        revenue = expected_attended * self.avg_appointment_value
        no_show_costs = expected_no_shows * self.cost_per_no_show
        idle_costs = expected_no_shows * self.provider_idle_cost
        
        additional_appointments = baseline['expected_no_shows'] - expected_no_shows
        additional_revenue = additional_appointments * self.avg_appointment_value
        reduced_costs = (baseline['no_show_costs'] - no_show_costs) + (baseline['idle_costs'] - idle_costs)
        
        return {
            'total_appointments': num_appointments,
            'new_no_show_rate': new_no_show_rate,
            'expected_no_shows': expected_no_shows,
            'expected_attended': expected_attended,
            'revenue': revenue,
            'no_show_costs': no_show_costs,
            'idle_costs': idle_costs,
            'additional_appointments': additional_appointments,
            'additional_revenue': additional_revenue,
            'reduced_costs': reduced_costs,
            'implementation_cost': implementation_cost,
            'annual_cost': annual_cost,
            'net_value': revenue - no_show_costs - idle_costs - annual_cost
        }
    
    def calculate_roi(self, num_appointments, no_show_reduction, implementation_cost, annual_cost, years=5):
        """
        Calculate ROI over multiple years
        
        Parameters:
        -----------
        num_appointments : int
            Number of appointments per year
        no_show_reduction : float
            Percentage reduction in no-shows (0-1)
        implementation_cost : float
            One-time implementation cost
        annual_cost : float
            Annual maintenance cost
        years : int
            Number of years for calculation
            
        Returns:
        --------
        dict
            ROI analysis
        """
        baseline = self.calculate_baseline_costs(num_appointments)
        improved = self.calculate_improved_scenario(num_appointments, no_show_reduction, implementation_cost, annual_cost)
        
        annual_benefit = improved['net_value'] - baseline['net_value']
        
        yearly_cashflow = [-implementation_cost]
        for _ in range(years):
            yearly_cashflow.append(annual_benefit)
        
        cumulative_cashflow = []
        cumulative = 0
        for cf in yearly_cashflow:
            cumulative += cf
            cumulative_cashflow.append(cumulative)
        
        # Calculate NPV with 7% discount rate
        npv = -implementation_cost
        discount_rate = 0.07
        for i in range(years):
            npv += annual_benefit / ((1 + discount_rate) ** (i + 1))
        
        # Calculate payback period
        if annual_benefit <= 0:
            payback_period = float('inf')
        else:
            payback_period = implementation_cost / annual_benefit
        
        # Calculate ROI
        total_investment = implementation_cost + annual_cost * years
        total_benefit = annual_benefit * years
        roi = (total_benefit - total_investment) / total_investment * 100
        
        return {
            'annual_benefit': annual_benefit,
            'yearly_cashflow': yearly_cashflow,
            'cumulative_cashflow': cumulative_cashflow,
            'npv': npv,
            'payback_period': payback_period,
            'roi': roi,
            'total_investment': total_investment,
            'total_benefit': total_benefit
        }
    
    def plot_roi(self, roi_data):
        """
        Create ROI visualization
        
        Parameters:
        -----------
        roi_data : dict
            ROI calculation results
            
        Returns:
        --------
        matplotlib.figure.Figure
            ROI chart
        """
        years = len(roi_data['yearly_cashflow'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot yearly and cumulative cash flow
        x = range(years)
        bar_width = 0.35
        
        ax.bar(x, roi_data['yearly_cashflow'], bar_width, label='Yearly Cash Flow')
        ax.plot(x, roi_data['cumulative_cashflow'], 'r-o', label='Cumulative Cash Flow')
        
        # Add zero line
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        
        # Add labels and title
        ax.set_xlabel('Year')
        ax.set_ylabel('Cash Flow ($)')
        ax.set_title('ROI Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(['Implementation'] + [f'Year {i+1}' for i in range(years-1)])
        
        # Add payback period annotation
        if roi_data['payback_period'] < float('inf'):
            payback_year = min(years-1, int(roi_data['payback_period']))
            ax.annotate(f'Payback: {roi_data["payback_period"]:.2f} years',
                         xy=(payback_year, roi_data['cumulative_cashflow'][payback_year]),
                         xytext=(payback_year-0.5, roi_data['cumulative_cashflow'][payback_year]+100000),
                         arrowprops=dict(arrowstyle='->'))
        
        # Add ROI annotation
        ax.annotate(f'5-Year ROI: {roi_data["roi"]:.1f}%',
                     xy=(years-1, roi_data['cumulative_cashflow'][-1]),
                     xytext=(years-2, roi_data['cumulative_cashflow'][-1]),
                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.3))
        
        ax.legend()
        plt.tight_layout()
        
        return fig
