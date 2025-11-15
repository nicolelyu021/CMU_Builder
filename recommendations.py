"""
AI-Powered Smart Recommendations
Suggests optimal fitness classes based on user preferences and schedule
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class FitnessRecommender:
    def __init__(self):
        self.preferences = {
            'preferred_times': ['morning', 'afternoon', 'evening'],  # All by default
            'preferred_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'class_types': [],  # Empty = all types
            'max_classes_per_week': 5,
            'min_gap_hours': 1  # Minimum hours between classes
        }
    
    def set_preferences(self, preferred_times=None, preferred_days=None, 
                       class_types=None, max_classes_per_week=None, min_gap_hours=None):
        """Update user preferences"""
        if preferred_times:
            self.preferences['preferred_times'] = preferred_times
        if preferred_days:
            self.preferences['preferred_days'] = preferred_days
        if class_types:
            self.preferences['class_types'] = class_types
        if max_classes_per_week:
            self.preferences['max_classes_per_week'] = max_classes_per_week
        if min_gap_hours:
            self.preferences['min_gap_hours'] = min_gap_hours
    
    def get_time_of_day(self, hour: int) -> str:
        """Categorize hour into time of day"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def calculate_fitness_score(self, event_row: pd.Series, calendar_df: pd.DataFrame) -> float:
        """Calculate a fitness score for recommending this class"""
        score = 0.0
        
        # Parse event time
        if 'start' in event_row and pd.notna(event_row['start']):
            start_dt = pd.to_datetime(event_row['start'])
            hour = start_dt.hour
            day = start_dt.strftime('%A')
            time_of_day = self.get_time_of_day(hour)
        else:
            return 0.0
        
        # Check time preference (40 points)
        if time_of_day in self.preferences['preferred_times']:
            score += 40
        
        # Check day preference (30 points)
        if day in self.preferences['preferred_days']:
            score += 30
        
        # Check for conflicts (penalty)
        if not calendar_df.empty and 'start' in calendar_df.columns:
            event_start = start_dt
            event_end = pd.to_datetime(event_row.get('end', event_start + timedelta(hours=1)))
            
            # Check for conflicts
            conflicts = 0
            for _, cal_event in calendar_df.iterrows():
                if pd.notna(cal_event.get('start')) and pd.notna(cal_event.get('end')):
                    cal_start = pd.to_datetime(cal_event['start'])
                    cal_end = pd.to_datetime(cal_event['end'])
                    
                    # Check overlap
                    if (event_start < cal_end) and (event_end > cal_start):
                        conflicts += 1
                        # Heavy penalty for conflicts
                        score -= 50
            
            # Bonus for no conflicts
            if conflicts == 0:
                score += 20
        
        # Check class type preference (20 points)
        event_name = str(event_row.get('scraped_event', '')).lower()
        if self.preferences['class_types']:
            for preferred_type in self.preferences['class_types']:
                if preferred_type.lower() in event_name:
                    score += 20
                    break
        else:
            # No preference = bonus
            score += 10
        
        # Bonus for morning classes (health benefit)
        if time_of_day == 'morning':
            score += 10
        
        # Bonus for weekday classes (consistency)
        if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            score += 5
        
        return max(0, score)  # Ensure non-negative
    
    def recommend_classes(self, fitness_df: pd.DataFrame, calendar_df: pd.DataFrame, 
                         top_n: int = 10) -> pd.DataFrame:
        """Get top N recommended fitness classes"""
        if fitness_df.empty:
            return pd.DataFrame()
        
        # Calculate scores for all fitness classes
        scores = []
        for _, row in fitness_df.iterrows():
            score = self.calculate_fitness_score(row, calendar_df)
            scores.append(score)
        
        fitness_df = fitness_df.copy()
        fitness_df['recommendation_score'] = scores
        
        # Filter out classes with zero or negative scores
        fitness_df = fitness_df[fitness_df['recommendation_score'] > 0]
        
        # Sort by score and return top N
        fitness_df = fitness_df.sort_values('recommendation_score', ascending=False)
        
        return fitness_df.head(top_n)
    
    def suggest_optimal_schedule(self, fitness_df: pd.DataFrame, calendar_df: pd.DataFrame,
                                 weeks: int = 2) -> pd.DataFrame:
        """Suggest an optimal weekly schedule"""
        if fitness_df.empty:
            return pd.DataFrame()
        
        # Get recommendations
        recommendations = self.recommend_classes(fitness_df, calendar_df, top_n=50)
        
        if recommendations.empty:
            return pd.DataFrame()
        
        # Group by week and day
        optimal_schedule = []
        selected_classes = set()
        
        # Get date range
        if 'start' in recommendations.columns:
            recommendations['start_dt'] = pd.to_datetime(recommendations['start'])
            recommendations['week'] = recommendations['start_dt'].dt.isocalendar().week
            recommendations['day'] = recommendations['start_dt'].dt.day_name()
            
            # Select best classes per day, respecting max_classes_per_week
            for week in recommendations['week'].unique():
                week_df = recommendations[recommendations['week'] == week]
                week_classes = []
                
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                    day_df = week_df[week_df['day'] == day].sort_values('recommendation_score', ascending=False)
                    
                    for _, class_row in day_df.iterrows():
                        class_id = f"{class_row.get('scraped_event', '')}_{class_row.get('start', '')}"
                        
                        if class_id not in selected_classes:
                            # Check gap requirement
                            if self._check_gap_requirement(class_row, week_classes):
                                week_classes.append(class_row)
                                selected_classes.add(class_id)
                                
                                if len(week_classes) >= self.preferences['max_classes_per_week']:
                                    break
                    
                    if len(week_classes) >= self.preferences['max_classes_per_week']:
                        break
                
                optimal_schedule.extend(week_classes)
        
        if optimal_schedule:
            return pd.DataFrame(optimal_schedule)
        else:
            return pd.DataFrame()
    
    def _check_gap_requirement(self, new_class: pd.Series, existing_classes: List) -> bool:
        """Check if new class meets minimum gap requirement"""
        if not existing_classes:
            return True
        
        new_start = pd.to_datetime(new_class.get('start'))
        min_gap = timedelta(hours=self.preferences['min_gap_hours'])
        
        for existing in existing_classes:
            existing_start = pd.to_datetime(existing.get('start'))
            existing_end = pd.to_datetime(existing.get('end', existing_start + timedelta(hours=1)))
            
            # Check if too close
            if abs((new_start - existing_end).total_seconds()) < min_gap.total_seconds():
                return False
        
        return True
    
    def get_schedule_insights(self, combined_df: pd.DataFrame) -> Dict[str, any]:
        """Generate insights about the schedule"""
        insights = {
            'total_events': len(combined_df),
            'busiest_day': None,
            'busiest_hour': None,
            'most_common_class': None,
            'schedule_balance': 'balanced',
            'recommendations': []
        }
        
        if combined_df.empty:
            return insights
        
        if 'start' in combined_df.columns:
            combined_df['start_dt'] = pd.to_datetime(combined_df['start'])
            combined_df['day'] = combined_df['start_dt'].dt.day_name()
            combined_df['hour'] = combined_df['start_dt'].dt.hour
            
            # Busiest day
            if 'day' in combined_df.columns:
                busiest_day = combined_df['day'].value_counts().index[0]
                insights['busiest_day'] = busiest_day
            
            # Busiest hour
            if 'hour' in combined_df.columns:
                busiest_hour = combined_df['hour'].value_counts().index[0]
                insights['busiest_hour'] = int(busiest_hour)
            
            # Most common class type
            fitness_events = combined_df[combined_df['scraped_event'].notna()]
            if not fitness_events.empty:
                most_common = fitness_events['scraped_event'].value_counts().index[0]
                insights['most_common_class'] = most_common
            
            # Schedule balance
            day_counts = combined_df['day'].value_counts()
            if day_counts.max() - day_counts.min() > 3:
                insights['schedule_balance'] = 'unbalanced'
                insights['recommendations'].append(
                    f"Your schedule is heavier on {day_counts.idxmax()}s. "
                    f"Consider spreading activities more evenly."
                )
            
            # Time distribution
            morning_count = len(combined_df[combined_df['hour'].between(6, 11)])
            afternoon_count = len(combined_df[combined_df['hour'].between(12, 16)])
            evening_count = len(combined_df[combined_df['hour'].between(17, 21)])
            
            if morning_count == 0:
                insights['recommendations'].append(
                    "You have no morning activities. Morning workouts can boost energy for the day!"
                )
            if evening_count > morning_count + afternoon_count:
                insights['recommendations'].append(
                    "Most of your activities are in the evening. Consider adding some morning sessions."
                )
        
        return insights

