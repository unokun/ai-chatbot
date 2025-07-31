from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    preferred_model: Optional[str] = None
    correction_style: Optional[str] = "default"

class ModelSelectionRequest(BaseModel):
    user_id: str
    model_name: str

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
        variants = await correction_service.correct_text(
            request.text, 
            request.user_id,
            request.preferred_model,
            request.correction_style
        )
        
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

@app.get("/api/models")
async def get_available_models():
    """Get available AI models"""
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        models = correction_service.get_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/model")
async def set_user_model(request: ModelSelectionRequest):
    """Set user's preferred AI model"""
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        success = await correction_service.set_user_preferred_model(
            request.user_id, 
            request.model_name
        )
        
        if success:
            return {"message": "Model preference updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid model name")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/settings")
async def get_user_settings(user_id: str):
    """Get user settings including preferred model"""
    try:
        from database.models import UserSettings, get_db
        db = next(get_db())
        
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if user_settings:
            return {
                "user_id": user_settings.user_id,
                "preferred_ai_model": user_settings.preferred_ai_model,
                "default_correction_style": user_settings.default_correction_style
            }
        else:
            # Return default settings
            return {
                "user_id": user_id,
                "preferred_ai_model": "openai-gpt4o",
                "default_correction_style": "polite"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/user/{user_id}/history")
async def get_correction_history(user_id: str, limit: int = 50, offset: int = 0):
    """Get user's correction history with pagination"""
    try:
        from database.models import CorrectionHistory, get_db
        db = next(get_db())
        
        history_query = db.query(CorrectionHistory).filter(
            CorrectionHistory.user_id == user_id
        ).order_by(CorrectionHistory.created_at.desc())
        
        total_count = history_query.count()
        history_items = history_query.offset(offset).limit(limit).all()
        
        return {
            "total_count": total_count,
            "items": [
                {
                    "id": item.id,
                    "original_text": item.original_text,
                    "corrected_text": item.corrected_text,
                    "correction_type": item.correction_type,
                    "ai_model_used": item.ai_model_used,
                    "created_at": item.created_at
                }
                for item in history_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/admin/health")
async def get_service_health():
    """Get health status of all AI services"""
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        health_status = correction_service.get_service_health()
        return {"services": health_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/reset-circuit-breaker/{service_name}")
async def reset_circuit_breaker(service_name: str):
    """Reset circuit breaker for a specific service"""
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        success = correction_service.reset_service_circuit_breaker(service_name)
        
        if success:
            return {"message": f"Circuit breaker reset for {service_name}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to reset circuit breaker")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/cache-stats")
async def get_cache_stats():
    """Get cache performance statistics"""  
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        cache_stats = await correction_service.get_cache_stats()
        return {"cache": cache_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/clear-cache")
async def clear_cache():
    """Clear correction cache"""
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        success = await correction_service.clear_cache()
        
        if success:
            return {"message": "Cache cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/correct/batch")
async def correct_messages_batch(requests: List[CorrectionRequest]):
    """Batch correction endpoint for multiple messages"""
    try:
        from services.correction_service import CorrectionService
        correction_service = CorrectionService()
        
        batch_requests = [
            {
                'text': req.text,
                'user_id': req.user_id,
                'preferred_model': req.preferred_model,
                'correction_style': req.correction_style,
                'use_cache': True
            }
            for req in requests
        ]
        
        batch_results = await correction_service.correct_text_batch(batch_requests)
        
        return [
            CorrectionResponse(
                original_text=req.text,
                variants=[CorrectionVariant(
                    text=v.text,
                    type=v.type,
                    reason=v.reason
                ) for v in variants]
            )
            for req, variants in zip(requests, batch_results)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    from database.models import create_tables
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
