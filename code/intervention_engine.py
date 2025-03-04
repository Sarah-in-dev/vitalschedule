import pandas as pd
import numpy as np

class InterventionEngine:
    def __init__(self):
        # Define intervention types and their effectiveness
        self.interventions = {
            'standard_reminder': {
                'effectiveness': 0.1,  # Reduces no-show probability by 10%
                'cost': 0.5,  # Cost in dollars
                'description': 'Standard automated reminder'
            },
            'personalized_sms': {
                'effectiveness': 0.15,
                'cost': 1.0,
                'description': 'Personalized SMS reminder'
            },
            'phone_call': {
                'effectiveness': 0.3,
                'cost': 5.0,
                'description': 'Personal phone call'
            },
            'transportation_assistance': {
                'effectiveness': 0.4,
                'cost': 15.0,
                'description': 'Offer transportation assistance'
            },
            'incentive_offer': {
                'effectiveness': 0.25,
                'cost': 10.0,
                'description': 'Offer small incentive for attendance'
            },
            'flexible_scheduling': {
                'effectiveness': 0.2,
                'cost': 2.0,
                'description': 'Offer flexible time window'
            }
        }
    
    def match_interventions(self, risk_score, risk_factors):
        """
        Match appropriate interventions based on risk score and factors
        
        Parameters:
        -----------
        risk_score : float
            Probability of no-show
        risk_factors : dict
            Dictionary of risk factors and their values
            
        Returns:
        --------
        list
            List of recommended interventions with effectiveness
        """
        recommended = []
        
        # Always include standard reminder
        recommended.append({
            'type': 'standard_reminder',
            'description': self.interventions['standard_reminder']['description'],
            'effectiveness': self.interventions['standard_reminder']['effectiveness'],
            'cost': self.interventions['standard_reminder']['cost']
        })
        
        # For medium risk (30-70%)
        if risk_score >= 0.3 and risk_score < 0.7:
            recommended.append({
                'type': 'personalized_sms',
                'description': self.interventions['personalized_sms']['description'],
                'effectiveness': self.interventions['personalized_sms']['effectiveness'],
                'cost': self.interventions['personalized_sms']['cost']
            })
            
            # Add phone call for higher end of medium risk
            if risk_score >= 0.5:
                recommended.append({
                    'type': 'phone_call',
                    'description': self.interventions['phone_call']['description'],
                    'effectiveness': self.interventions['phone_call']['effectiveness'],
                    'cost': self.interventions['phone_call']['cost']
                })
        
        # For high risk (70%+)
        if risk_score >= 0.7:
            # Include phone call if not already added
            if not any(r['type'] == 'phone_call' for r in recommended):
                recommended.append({
                    'type': 'phone_call',
                    'description': self.interventions['phone_call']['description'],
                    'effectiveness': self.interventions['phone_call']['effectiveness'],
                    'cost': self.interventions['phone_call']['cost']
                })
            
            # Check for transportation issues
            if 'transport_score' in risk_factors and risk_factors['transport_score'] < 5:
                recommended.append({
                    'type': 'transportation_assistance',
                    'description': self.interventions['transportation_assistance']['description'],
                    'effectiveness': self.interventions['transportation_assistance']['effectiveness'],
                    'cost': self.interventions['transportation_assistance']['cost']
                })
            
            # For very high risk, consider incentives
            if risk_score >= 0.85:
                recommended.append({
                    'type': 'incentive_offer',
                    'description': self.interventions['incentive_offer']['description'],
                    'effectiveness': self.interventions['incentive_offer']['effectiveness'],
                    'cost': self.interventions['incentive_offer']['cost']
                })
        
        # Sort by effectiveness
        recommended.sort(key=lambda x: x['effectiveness'], reverse=True)
        
        return recommended
    
    def calculate_roi(self, risk_score, intervention, avg_appointment_value=150):
        """
        Calculate expected ROI for an intervention
        
        Parameters:
        -----------
        risk_score : float
            Probability of no-show
        intervention : dict
            Intervention details
        avg_appointment_value : float
            Average value of an appointment in dollars
            
        Returns:
        --------
        float
            Expected ROI ratio
        """
        # Calculate probability of attendance with intervention
        baseline_attendance_prob = 1 - risk_score
        intervention_effectiveness = intervention['effectiveness']
        new_attendance_prob = baseline_attendance_prob + (risk_score * intervention_effectiveness)
        
        # Calculate value
        baseline_value = baseline_attendance_prob * avg_appointment_value
        new_value = new_attendance_prob * avg_appointment_value
        value_increase = new_value - baseline_value
        
        # Calculate ROI
        cost = intervention['cost']
        roi = (value_increase - cost) / cost if cost > 0 else float('inf')
        
        return roi
    
    def optimize_interventions(self, risk_score, risk_factors, budget=None, avg_appointment_value=150):
        """
        Optimize interventions based on ROI and budget constraints
        
        Parameters:
        -----------
        risk_score : float
            Probability of no-show
        risk_factors : dict
            Dictionary of risk factors and their values
        budget : float
            Maximum budget for interventions
        avg_appointment_value : float
            Average value of an appointment in dollars
            
        Returns:
        --------
        list
            Optimized list of interventions
        """
        all_interventions = self.match_interventions(risk_score, risk_factors)
        
        # Calculate ROI for each intervention
        for intervention in all_interventions:
            intervention['roi'] = self.calculate_roi(risk_score, intervention, avg_appointment_value)
        
        # Sort by ROI
        all_interventions.sort(key=lambda x: x['roi'], reverse=True)
        
        # If no budget constraint, return all positive ROI interventions
        if budget is None:
            return [i for i in all_interventions if i['roi'] > 0]
        
        # Otherwise, select interventions within budget
        optimized = []
        remaining_budget = budget
        
        for intervention in all_interventions:
            if intervention['cost'] <= remaining_budget and intervention['roi'] > 0:
                optimized.append(intervention)
                remaining_budget -= intervention['cost']
            
            if remaining_budget <= 0:
                break
        
        return optimized
