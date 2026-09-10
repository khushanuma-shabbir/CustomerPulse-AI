"""
FastAPI Application for CustomerPulse AI
Provides REST API for ticket priority prediction and analysis
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from app.supabase_client import supabase
from app.priority_engine import PriorityEngine
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="CustomerPulse AI API",
    description="AI-powered customer support ticket prioritization system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Priority Engine
try:
    priority_engine = PriorityEngine()
    print("✓ Priority Engine initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load priority engine: {e}")
    print("  Train the model first by running: python train_model.py")
    priority_engine = None


# Pydantic models for request/response
class TicketPredictionRequest(BaseModel):
    customer_tier: str
    product: str
    product_category: str
    product_criticality: str
    issue_type: str
    channel: str
    current_severity: str
    sla_target_hours: float
    sla_remaining_hours: float
    sla_breached: int
    reopen_count: int
    customer_contact_count: int
    production_impact: str
    business_impact: str
    affected_users_estimate: int
    security_related: int
    customer_sentiment: str
    urgency_keywords: str
    waiting_time_hours: float
    status: str
    assigned_team: str
    previous_escalation: int
    ticket_id: Optional[str] = None


class PredictionResponse(BaseModel):
    predicted_priority: str
    confidence: Optional[float]
    reasons: List[str]
    ticket_id: str


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "CustomerPulse AI API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /tickets": "Get all tickets",
            "GET /tickets/{ticket_id}": "Get specific ticket",
            "POST /predict": "Predict ticket priority",
            "GET /stats": "Get ticket statistics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": priority_engine is not None,
        "database_connected": True
    }


@app.get("/tickets")
async def get_tickets(
    limit: int = 100,
    offset: int = 0,
    priority: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get tickets from database
    
    Args:
        limit: Maximum number of tickets to return
        offset: Number of tickets to skip
        priority: Filter by priority (Critical, High, Medium, Low)
        status: Filter by status
    """
    try:
        query = supabase.table("tickets").select("*")
        
        # Apply filters
        if priority:
            query = query.eq("ground_truth_priority", priority)
        if status:
            query = query.eq("status", status)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "tickets": response.data,
            "count": len(response.data),
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get a specific ticket by ID"""
    try:
        response = supabase.table("tickets").select("*").eq("ticket_id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        
        ticket = response.data[0]
        
        # Add AI prediction if model is available
        if priority_engine:
            try:
                prediction = priority_engine.predict_priority(ticket)
                ticket['ai_prediction'] = prediction
            except Exception as e:
                ticket['ai_prediction'] = {'error': str(e)}
        
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ticket: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict_priority(request: TicketPredictionRequest):
    """
    Predict priority for a new or existing ticket
    
    Args:
        request: Ticket data
        
    Returns:
        Prediction with priority, confidence, and explanation
    """
    if not priority_engine:
        raise HTTPException(
            status_code=503,
            detail="Priority prediction model not available. Please train the model first."
        )
    
    try:
        # Convert request to dictionary
        ticket_data = request.dict()
        
        # Make prediction
        prediction = priority_engine.predict_priority(ticket_data)
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """Get ticket statistics and analytics"""
    try:
        # Get all tickets
        response = supabase.table("tickets").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if df.empty:
            return {"error": "No tickets found"}
        
        # Calculate statistics
        stats = {
            "total_tickets": len(df),
            "priority_distribution": df["ground_truth_priority"].value_counts().to_dict(),
            "status_distribution": df["status"].value_counts().to_dict() if "status" in df.columns else {},
            "sla_breached_count": int(df[df["sla_breached"] == "Yes"].shape[0]) if "sla_breached" in df.columns else 0,
            "critical_tickets": int(df[df["ground_truth_priority"] == "Critical"].shape[0]),
            "high_tickets": int(df[df["ground_truth_priority"] == "High"].shape[0]),
            "medium_tickets": int(df[df["ground_truth_priority"] == "Medium"].shape[0]),
            "low_tickets": int(df[df["ground_truth_priority"] == "Low"].shape[0]),
            "avg_sla_remaining": float(df["sla_remaining_hours"].mean()) if "sla_remaining_hours" in df.columns else 0,
            "avg_affected_users": float(df["affected_users_estimate"].mean()) if "affected_users_estimate" in df.columns else 0,
            "security_related_count": int(df[df["security_related"] == "Yes"].shape[0]) if "security_related" in df.columns else 0,
        }
        
        # Customer tier breakdown
        if "customer_tier" in df.columns:
            stats["customer_tier_distribution"] = df["customer_tier"].value_counts().to_dict()
        
        # Production impact breakdown
        if "production_impact" in df.columns:
            stats["production_impact_distribution"] = df["production_impact"].value_counts().to_dict()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


@app.get("/predict-batch/{ticket_ids}")
async def predict_batch(ticket_ids: str):
    """
    Predict priorities for multiple tickets
    
    Args:
        ticket_ids: Comma-separated ticket IDs
    """
    if not priority_engine:
        raise HTTPException(
            status_code=503,
            detail="Priority prediction model not available"
        )
    
    try:
        # Parse ticket IDs
        ids = [tid.strip() for tid in ticket_ids.split(",")]
        
        # Fetch tickets
        response = supabase.table("tickets").select("*").in_("ticket_id", ids).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No tickets found")
        
        # Make predictions
        predictions = priority_engine.batch_predict(response.data)
        
        return {
            "predictions": predictions,
            "count": len(predictions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


if __name__ == "__main__":
    print("="*60)
    print("Starting CustomerPulse AI API Server")
    print("="*60)
    print("\nAPI Documentation available at:")
    print("  • http://localhost:8000/docs (Swagger UI)")
    print("  • http://localhost:8000/redoc (ReDoc)")
    print("\n" + "="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
