"""
Visualization utilities for Fit-Tartans
Creates beautiful charts and calendar views
"""
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

def create_timeline_chart(df, height=600):
    """Create an interactive timeline/Gantt chart of events"""
    if df.empty or 'start' not in df.columns:
        return None
    
    # Prepare data for timeline
    timeline_df = df.copy()
    timeline_df['start_dt'] = pd.to_datetime(timeline_df['start'])
    timeline_df['end_dt'] = pd.to_datetime(timeline_df['end'])
    
    # Calculate duration in hours
    timeline_df['duration_hours'] = (timeline_df['end_dt'] - timeline_df['start_dt']).dt.total_seconds() / 3600
    timeline_df['duration_hours'] = timeline_df['duration_hours'].fillna(1)  # Default 1 hour
    
    # Create event name
    timeline_df['event_name'] = timeline_df.apply(
        lambda row: row.get('calendar_event', '') or row.get('scraped_event', 'Untitled Event'),
        axis=1
    )
    
    # Create color based on source
    timeline_df['source'] = timeline_df.apply(
        lambda row: 'Calendar' if pd.notna(row.get('calendar_event')) else 'Fitness Class',
        axis=1
    )
    
    # Sort by start time
    timeline_df = timeline_df.sort_values('start_dt')
    
    # Create the chart
    chart = alt.Chart(timeline_df).mark_bar(
        cornerRadius=4,
        strokeWidth=1,
        stroke='white'
    ).encode(
        x=alt.X('start_dt:T', title='Time', axis=alt.Axis(format='%m/%d %H:%M')),
        x2='end_dt:T',
        y=alt.Y('event_name:N', 
                title='Event',
                sort=alt.EncodingSortField(field='start_dt', order='ascending'),
                axis=alt.Axis(labelLimit=200)),
        color=alt.Color('source:N',
                       scale=alt.Scale(domain=['Calendar', 'Fitness Class'],
                                      range=['#4285F4', '#EA4335']),
                       legend=alt.Legend(title='Event Type')),
        tooltip=[
            alt.Tooltip('event_name:N', title='Event'),
            alt.Tooltip('start_dt:T', title='Start', format='%Y-%m-%d %H:%M'),
            alt.Tooltip('end_dt:T', title='End', format='%Y-%m-%d %H:%M'),
            alt.Tooltip('location:N', title='Location'),
            alt.Tooltip('source:N', title='Source')
        ]
    ).properties(
        width=800,
        height=height,
        title='Your Fitness Schedule Timeline'
    ).interactive()
    
    return chart

def create_schedule_heatmap(df):
    """Create a heatmap showing schedule density by day of week and hour"""
    if df.empty or 'start' not in df.columns:
        return None
    
    heatmap_df = df.copy()
    heatmap_df['start_dt'] = pd.to_datetime(heatmap_df['start'])
    heatmap_df['day_of_week'] = heatmap_df['start_dt'].dt.day_name()
    heatmap_df['hour'] = heatmap_df['start_dt'].dt.hour
    
    # Count events per day/hour
    heatmap_data = heatmap_df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    
    # Order days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data['day_of_week'] = pd.Categorical(heatmap_data['day_of_week'], categories=day_order, ordered=True)
    
    chart = alt.Chart(heatmap_data).mark_rect(
        stroke='white',
        strokeWidth=2
    ).encode(
        x=alt.X('hour:O', title='Hour of Day', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('day_of_week:O', title='Day of Week', sort=day_order),
        color=alt.Color('count:Q',
                       scale=alt.Scale(scheme='blues'),
                       legend=alt.Legend(title='Number of Events')),
        tooltip=[
            alt.Tooltip('day_of_week:N', title='Day'),
            alt.Tooltip('hour:O', title='Hour'),
            alt.Tooltip('count:Q', title='Events')
        ]
    ).properties(
        width=700,
        height=300,
        title='Schedule Density Heatmap'
    )
    
    return chart

def create_class_type_chart(df):
    """Create a bar chart showing distribution of class types"""
    if df.empty:
        return None
    
    # Extract class types from event names
    class_df = df.copy()
    class_df['event_name'] = class_df.apply(
        lambda row: row.get('scraped_event', '') or row.get('calendar_event', ''),
        axis=1
    )
    
    # Common fitness class keywords
    fitness_keywords = {
        'Yoga': ['yoga', 'vinyasa', 'yin', 'ashtanga'],
        'Pilates': ['pilates', 'reformer'],
        'Cardio': ['hiit', 'cardio', 'kickboxing', 'boxing', 'cycling', 'spin'],
        'Strength': ['strength', 'weights', 'kettlebell', 'abs', 'glutes'],
        'Dance': ['dance', 'hip hop', 'jazz', 'zumba'],
        'Mindfulness': ['meditation', 'sound bath', 'mindfulness'],
        'Barre': ['barre'],
        'Other': []
    }
    
    def categorize_class(name):
        name_lower = str(name).lower()
        for category, keywords in fitness_keywords.items():
            if category == 'Other':
                continue
            if any(keyword in name_lower for keyword in keywords):
                return category
        return 'Other'
    
    class_df['category'] = class_df['event_name'].apply(categorize_class)
    category_counts = class_df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    chart = alt.Chart(category_counts).mark_bar(
        cornerRadius=5
    ).encode(
        x=alt.X('Count:Q', title='Number of Classes'),
        y=alt.Y('Category:N', title='Class Type', sort='-x'),
        color=alt.Color('Category:N', scale=alt.Scale(scheme='category20')),
        tooltip=['Category:N', 'Count:Q']
    ).properties(
        width=600,
        height=300,
        title='Fitness Classes by Type'
    )
    
    return chart

def create_time_distribution_chart(df):
    """Create a chart showing event distribution throughout the day"""
    if df.empty or 'start' not in df.columns:
        return None
    
    time_df = df.copy()
    time_df['start_dt'] = pd.to_datetime(time_df['start'])
    time_df['hour'] = time_df['start_dt'].dt.hour
    
    hour_counts = time_df['hour'].value_counts().sort_index().reset_index()
    hour_counts.columns = ['Hour', 'Count']
    
    chart = alt.Chart(hour_counts).mark_area(
        line=True,
        point=True,
        color='#EA4335',
        fill='#EA4335',
        fillOpacity=0.3
    ).encode(
        x=alt.X('Hour:Q', title='Hour of Day', scale=alt.Scale(domain=[0, 23])),
        y=alt.Y('Count:Q', title='Number of Events'),
        tooltip=['Hour:Q', 'Count:Q']
    ).properties(
        width=700,
        height=250,
        title='Event Distribution Throughout the Day'
    )
    
    return chart

def create_stats_cards(df):
    """Create metric cards for dashboard"""
    if df.empty:
        return {
            'total_events': 0,
            'fitness_classes': 0,
            'calendar_events': 0,
            'free_slots': 0,
            'avg_per_day': 0
        }
    
    stats = {}
    stats['total_events'] = len(df)
    
    # Count by source
    calendar_count = df['calendar_event'].notna().sum()
    fitness_count = df['scraped_event'].notna().sum()
    
    stats['calendar_events'] = calendar_count
    stats['fitness_classes'] = fitness_count
    
    # Calculate free time slots (simplified - assumes 8am-10pm active hours)
    if 'start' in df.columns:
        df['start_dt'] = pd.to_datetime(df['start'])
        df['end_dt'] = pd.to_datetime(df['end'])
        
        # Get date range
        min_date = df['start_dt'].min().date()
        max_date = df['start_dt'].max().date()
        days = (max_date - min_date).days + 1
        
        # Assume 14 hours of active time per day (8am-10pm)
        total_hours = days * 14
        booked_hours = (df['end_dt'] - df['start_dt']).dt.total_seconds().sum() / 3600
        free_hours = total_hours - booked_hours
        
        stats['free_slots'] = max(0, int(free_hours))
        stats['avg_per_day'] = round(stats['total_events'] / days, 1) if days > 0 else 0
    else:
        stats['free_slots'] = 0
        stats['avg_per_day'] = 0
    
    return stats

