# backend/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import BookingAgent
import os

app = FastAPI(title="TailorTalk Booking API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the booking agent
booking_agent = BookingAgent()

class MessageRequest(BaseModel):
    message: str
    session_id: str = "default"

class MessageResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    """Chat endpoint for the booking agent"""
    try:
        response = booking_agent.process_message(request.message)
        return MessageResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "TailorTalk API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)