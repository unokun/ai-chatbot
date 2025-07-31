from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Message Correction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CorrectionRequest(BaseModel):
    text: str
    user_id: Optional[str] = "anonymous"

class CorrectionVariant(BaseModel):
    text: str
    type: str
    reason: str

class CorrectionResponse(BaseModel):
    original_text: str
    variants: List[CorrectionVariant]

@app.get("/")
async def root():
    return {"message": "AI Message Correction API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/correct", response_model=CorrectionResponse)
async def correct_message(request: CorrectionRequest):
    try:
        from services.correction_service import CorrectionService
        
        correction_service = CorrectionService()
        variants = await correction_service.correct_text(request.text, request.user_id)
        
        return CorrectionResponse(
            original_text=request.text,
            variants=[CorrectionVariant(
                text=v.text,
                type=v.type,
                reason=v.reason
            ) for v in variants]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    from database.models import create_tables
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
