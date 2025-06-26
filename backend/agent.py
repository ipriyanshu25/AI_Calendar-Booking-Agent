import os
import openai
from datetime import datetime, timedelta
from typing import Dict, List
from pydantic import PrivateAttr
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import BaseTool
from calendar_service import GoogleCalendarService

# --- custom lightweight wrapper over OpenAI ChatCompletion ---
class ChatOpenAI:
    def __init__(self, *, model_name: str, temperature: float, openai_api_key: str):
        openai.api_key = openai_api_key
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, messages):
        api_messages = []
        for m in messages:
            role = "user" if isinstance(m, HumanMessage) else "assistant"
            api_messages.append({"role": role, "content": m.content})
        resp = openai.ChatCompletion.create(
            model=self.model_name,
            messages=api_messages,
            temperature=self.temperature,
        )
        return AIMessage(content=resp.choices[0].message["content"])


class CalendarTool(BaseTool):
    name: str = "calendar_tool"
    description: str = "Tool for checking calendar availability and booking appointments"
    _calendar_service: GoogleCalendarService = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._calendar_service = GoogleCalendarService()

    def _run(self, action: str, **kwargs) -> str:
        if action == "check_availability":
            date = kwargs.get('date')
            return self._check_availability(date)
        elif action == "book_appointment":
            return self._book_appointment(**kwargs)
        else:
            return "Invalid action"

    def _check_availability(self, date_str: str) -> str:
        try:
            date = self._parse_date(date_str)
            if not date:
                return "Could not parse the date. Please provide a clearer date."

            free_slots = self._calendar_service.find_free_slots(date)
            if not free_slots:
                return f"No available slots found for {date.strftime('%B %d, %Y')}"

            slots_text = f"Available slots for {date.strftime('%B %d, %Y')}:\n"
            for i, slot in enumerate(free_slots[:5], 1):
                slots_text += f"{i}. {slot['start']} - {slot['end']}\n"
            return slots_text
        except Exception as e:
            return f"Error checking availability: {str(e)}"

    def _book_appointment(self, title: str, date_str: str, time_str: str) -> str:
        try:
            date = self._parse_date(date_str)
            start_time = self._parse_time(date, time_str)
            end_time = start_time + timedelta(hours=1)

            success = self._calendar_service.book_appointment(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description="Booked via TailorTalk Agent"
            )
            if success:
                return f"✅ Successfully booked '{title}' for {start_time.strftime('%B %d, %Y at %I:%M %p')}"
            else:
                return "❌ Failed to book the appointment. Please try again."
        except Exception as e:
            return f"Error booking appointment: {str(e)}"

    def _parse_date(self, date_str: str) -> datetime:
        today = datetime.now()
        date_str = date_str.lower()
        if "today" in date_str:
            return today
        elif "tomorrow" in date_str:
            return today + timedelta(days=1)
        elif "next week" in date_str:
            return today + timedelta(days=7)
        elif "friday" in date_str:
            days_ahead = 4 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        return today + timedelta(days=1)

    def _parse_time(self, date: datetime, time_str: str) -> datetime:
        time_str = time_str.lower()
        if "afternoon" in time_str:
            hour = 14
        elif "morning" in time_str:
            hour = 10
        elif "3" in time_str and "pm" in time_str:
            hour = 15
        else:
            hour = 14
        return datetime.combine(date.date(), datetime.min.time().replace(hour=hour))


class ConversationState:
    def __init__(self):
        self.messages: List[Dict] = []
        self.user_intent: str = ""
        self.appointment_details: Dict = {}
        self.stage: str = "greeting"


class BookingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.calendar_tool = CalendarTool()
        self.conversation_state = ConversationState()

    def process_message(self, user_message: str) -> str:
        self.conversation_state.messages.append({"role": "user", "content": user_message})
        intent = self._analyze_intent(user_message)
        if intent == "greeting":
            response = "Hello! I'm your personal booking assistant. I can help you schedule appointments on your calendar. What would you like to book?"
        elif intent == "check_availability":
            date_info = self._extract_date_info(user_message)
            availability = self.calendar_tool._run("check_availability", date=date_info)
            response = f"{availability}\n\nWhich time slot would you prefer?"
        elif intent == "book_appointment":
            details = self._extract_booking_details(user_message)
            if self._validate_booking_details(details):
                response = self.calendar_tool._run(
                    "book_appointment",
                    title=details.get('title', 'Meeting'), date_str=details['date'], time_str=details['time']
                )
            else:
                response = "I need more information. Please specify the date and time for your appointment."
        else:
            response = self._generate_contextual_response(user_message)
        self.conversation_state.messages.append({"role": "assistant", "content": response})
        return response

    def _analyze_intent(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["hi","hello","hey"]): return "greeting"
        if any(w in msg for w in ["available","free","check","when"]): return "check_availability"
        if any(w in msg for w in ["book","schedule","confirm","reserve"]): return "book_appointment"
        return "conversation"

    def _extract_date_info(self, message: str) -> str:
        return message

    def _extract_booking_details(self, message: str) -> Dict:
        details: Dict = {}
        m = message.lower()
        if "tomorrow" in m: details['date'] = "tomorrow"
        elif "friday" in m: details['date'] = "friday"
        elif "next week" in m: details['date'] = "next week"
        if "3 pm" in m or "3pm" in m: details['time'] = "3 pm"
        elif "afternoon" in m: details['time'] = "afternoon"
        elif "morning" in m: details['time'] = "morning"
        details['title'] = "Meeting"
        return details

    def _validate_booking_details(self, details: Dict) -> bool:
        return 'date' in details and 'time' in details

    def _generate_contextual_response(self, user_message: str) -> str:
        system_prompt = (
            "You are a helpful calendar booking assistant. Your job is to:\n"
            "1. Help users book appointments on their calendar\n"
            "2. Ask clarifying questions when needed\n"
            "3. Be friendly and professional\n"
            "4. Guide the conversation towards booking a specific time slot\n"
            "Keep responses concise and focused on booking appointments."
        )
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_state.messages[-3:]
        try:
            resp = self.llm.invoke([
                HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) for m in messages
            ])
            return resp.content
        except Exception:
            return "I'm here to help you book appointments. What date and time would you like to schedule?"
