"""
Export events to Google Calendar
One-click add to calendar functionality
"""
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import streamlit as st

def create_calendar_event(event_row: pd.Series) -> dict:
    """Create a Google Calendar event dictionary from a DataFrame row"""
    event = {
        'summary': event_row.get('scraped_event') or event_row.get('calendar_event', 'Untitled Event'),
        'description': event_row.get('description', ''),
        'location': event_row.get('location', ''),
    }
    
    # Add start time
    if pd.notna(event_row.get('start')):
        start_dt = pd.to_datetime(event_row['start'])
        event['start'] = {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'America/New_York'
        }
    else:
        return None
    
    # Add end time
    if pd.notna(event_row.get('end')):
        end_dt = pd.to_datetime(event_row['end'])
        event['end'] = {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'America/New_York'
        }
    else:
        # Default to 1 hour if no end time
        event['end'] = {
            'dateTime': (start_dt + pd.Timedelta(hours=1)).isoformat(),
            'timeZone': 'America/New_York'
        }
    
    return event

def add_events_to_calendar(creds: Credentials, events_df: pd.DataFrame, 
                          calendar_id: str = 'primary') -> dict:
    """Add multiple events to Google Calendar"""
    service = build('calendar', 'v3', credentials=creds)
    
    results = {
        'success': [],
        'failed': [],
        'total': len(events_df)
    }
    
    for idx, row in events_df.iterrows():
        try:
            event = create_calendar_event(row)
            if event:
                created_event = service.events().insert(
                    calendarId=calendar_id,
                    body=event
                ).execute()
                
                results['success'].append({
                    'event': event['summary'],
                    'id': created_event.get('id')
                })
            else:
                results['failed'].append({
                    'event': row.get('scraped_event') or row.get('calendar_event', 'Unknown'),
                    'reason': 'Invalid date/time'
                })
        except Exception as e:
            results['failed'].append({
                'event': row.get('scraped_event') or row.get('calendar_event', 'Unknown'),
                'reason': str(e)
            })
    
    return results

def generate_ical_file(events_df: pd.DataFrame) -> str:
    """Generate an iCal file for download"""
    ical_content = "BEGIN:VCALENDAR\n"
    ical_content += "VERSION:2.0\n"
    ical_content += "PRODID:-//Fit-Tartans//Fitness Scheduler//EN\n"
    ical_content += "CALSCALE:GREGORIAN\n"
    ical_content += "METHOD:PUBLISH\n"
    
    for _, row in events_df.iterrows():
        event_name = row.get('scraped_event') or row.get('calendar_event', 'Untitled Event')
        description = row.get('description', '')
        location = row.get('location', '')
        
        if pd.notna(row.get('start')):
            start_dt = pd.to_datetime(row['start'])
            end_dt = pd.to_datetime(row.get('end', start_dt + pd.Timedelta(hours=1)))
            
            # Format for iCal (UTC)
            start_str = start_dt.strftime('%Y%m%dT%H%M%SZ')
            end_str = end_dt.strftime('%Y%m%dT%H%M%SZ')
            
            ical_content += "BEGIN:VEVENT\n"
            ical_content += f"DTSTART:{start_str}\n"
            ical_content += f"DTEND:{end_str}\n"
            ical_content += f"SUMMARY:{event_name}\n"
            ical_content += f"DESCRIPTION:{description}\n"
            ical_content += f"LOCATION:{location}\n"
            ical_content += "END:VEVENT\n"
    
    ical_content += "END:VCALENDAR\n"
    return ical_content

