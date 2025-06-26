# backend/calendar_service.py

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080, host='localhost')
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_busy_times(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get busy time slots from calendar"""
        try:
            freebusy_request = {
                'timeMin': start_time.isoformat(),
                'timeMax': end_time.isoformat(),
                'items': [{'id': self.calendar_id}]
            }
            
            freebusy_result = self.service.freebusy().query(body=freebusy_request).execute()
            busy_times = freebusy_result['calendars'][self.calendar_id]['busy']
            
            return busy_times
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def find_free_slots(self, date: datetime, duration_minutes: int = 60, 
                       start_hour: int = 9, end_hour: int = 17) -> List[Dict]:
        """Find free time slots on a given date"""
        # Set timezone
        tz = pytz.timezone('UTC')
        
        # Create start and end times for the day
        day_start = tz.localize(datetime.combine(date.date(), 
                                               datetime.min.time().replace(hour=start_hour)))
        day_end = tz.localize(datetime.combine(date.date(), 
                                             datetime.min.time().replace(hour=end_hour)))
        
        # Get busy times
        busy_times = self.get_busy_times(day_start, day_end)
        
        # Generate potential slots
        potential_slots = []
        current_time = day_start
        
        while current_time + timedelta(minutes=duration_minutes) <= day_end:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with busy times
            is_free = True
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                if (current_time < busy_end and slot_end > busy_start):
                    is_free = False
                    break
            
            if is_free:
                potential_slots.append({
                    'start': current_time.strftime('%I:%M %p'),
                    'end': slot_end.strftime('%I:%M %p'),
                    'start_datetime': current_time,
                    'end_datetime': slot_end
                })
            
            current_time += timedelta(minutes=30)  # 30-minute intervals
        
        return potential_slots
    
    def book_appointment(self, title: str, start_time: datetime, 
                        end_time: datetime, description: str = "") -> bool:
        """Book an appointment on the calendar"""
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            print(f'Event created: {event.get("htmlLink")}')
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False