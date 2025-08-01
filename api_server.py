from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
import threading
from datetime import datetime, timedelta
import uuid
import json
from pydantic import BaseModel

from database import get_db, BudgetData, UserSession, create_tables
from powerbi_service import PowerBIService

app = FastAPI(title="Budget Portal API", version="1.0.0")

# CORS middleware for Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread lock for concurrent operations
data_lock = threading.RLock()
powerbi_service = PowerBIService()

@app.on_event("startup")
async def startup_event():
    create_tables()

class LoginRequest(BaseModel):
    user_id: str
    business_unit: str

class BudgetUpdateRequest:
    def __init__(self, user_id: str, business_unit: str, updates: List[Dict]):
        self.user_id = user_id
        self.business_unit = business_unit
        self.updates = updates

@app.post("/api/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and create session"""
    try:
        user_id = request.user_id
        business_unit = request.business_unit
        
        # Generate session token
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=8)
        
        # Check if user session exists
        existing_session = db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).first()
        
        if existing_session:
            existing_session.session_token = session_token
            existing_session.expires_at = expires_at
            existing_session.is_active = True
        else:
            new_session = UserSession(
                user_id=user_id,
                business_unit=business_unit,
                session_token=session_token,
                expires_at=expires_at
            )
            db.add(new_session)
        
        db.commit()
        
        return {
            "success": True,
            "session_token": session_token,
            "user_id": user_id,
            "business_unit": business_unit
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/data/{user_id}/{business_unit}")
async def get_user_data(user_id: str, business_unit: str, db: Session = Depends(get_db)):
    """Get data for specific user with RLS"""
    try:
        # First try to get data from local database
        local_data = db.query(BudgetData).filter(
            and_(
                BudgetData.user_id == user_id,
                BudgetData.business_unit == business_unit
            )
        ).all()
        
        # If no local data, fetch from PowerBI
        if not local_data:
            powerbi_data = powerbi_service.get_user_data_with_rls(user_id, business_unit)
            
            if not powerbi_data.empty:
                # Convert PowerBI data to local format and store
                for _, row in powerbi_data.iterrows():
                    budget_entry = BudgetData(
                        business_unit=business_unit,
                        user_id=user_id,
                        product_category=row.get('ProductCategory', ''),
                        region=row.get('Region', ''),
                        quarter=row.get('Quarter', ''),
                        year=row.get('Year', datetime.now().year),
                        historical_sales=row.get('HistoricalSales'),
                        target_sales=row.get('TargetSales'),
                        market_share=row.get('MarketShare'),
                        budget_amount=row.get('BudgetAmount'),
                        forecast_sales=row.get('ForecastSales'),
                        comments=row.get('Comments', '')
                    )
                    db.add(budget_entry)
                
                db.commit()
                local_data = db.query(BudgetData).filter(
                    and_(
                        BudgetData.user_id == user_id,
                        BudgetData.business_unit == business_unit
                    )
                ).all()
        
        # Convert to dict format
        result = []
        for item in local_data:
            result.append({
                "id": item.id,
                "business_unit": item.business_unit,
                "product_category": item.product_category,
                "region": item.region,
                "quarter": item.quarter,
                "year": item.year,
                "historical_sales": item.historical_sales,
                "target_sales": item.target_sales,
                "market_share": item.market_share,
                "budget_amount": item.budget_amount,
                "forecast_sales": item.forecast_sales,
                "comments": item.comments,
                "is_submitted": item.is_submitted,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            })
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

@app.post("/api/update")
async def update_budget_data(
    user_id: str,
    business_unit: str,
    updates: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Update budget data with thread safety"""
    with data_lock:
        try:
            updated_records = []
            
            for update in updates:
                record_id = update.get("id")
                if not record_id:
                    continue
                
                # Get existing record
                record = db.query(BudgetData).filter(
                    and_(
                        BudgetData.id == record_id,
                        BudgetData.user_id == user_id,
                        BudgetData.business_unit == business_unit
                    )
                ).first()
                
                if record:
                    # Update editable fields only
                    if "budget_amount" in update:
                        record.budget_amount = update["budget_amount"]
                    if "forecast_sales" in update:
                        record.forecast_sales = update["forecast_sales"]
                    if "comments" in update:
                        record.comments = update["comments"]
                    
                    record.updated_at = datetime.utcnow()
                    record.version += 1
                    
                    updated_records.append(record.id)
            
            db.commit()
            
            return {
                "success": True,
                "updated_records": updated_records,
                "message": f"Updated {len(updated_records)} records"
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.post("/api/submit")
async def submit_budget_data(
    user_id: str,
    business_unit: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit budget data and trigger PowerBI refresh"""
    with data_lock:
        try:
            # Mark all user's records as submitted
            records = db.query(BudgetData).filter(
                and_(
                    BudgetData.user_id == user_id,
                    BudgetData.business_unit == business_unit,
                    BudgetData.is_submitted == False
                )
            ).all()
            
            if not records:
                raise HTTPException(status_code=400, detail="No records to submit")
            
            submission_time = datetime.utcnow()
            submitted_data = []
            
            for record in records:
                record.is_submitted = True
                record.submitted_at = submission_time
                
                # Prepare data for PowerBI
                submitted_data.append({
                    "UserId": record.user_id,
                    "BusinessUnit": record.business_unit,
                    "ProductCategory": record.product_category,
                    "Region": record.region,
                    "Quarter": record.quarter,
                    "Year": record.year,
                    "BudgetAmount": record.budget_amount,
                    "ForecastSales": record.forecast_sales,
                    "Comments": record.comments,
                    "SubmittedAt": submission_time.isoformat(),
                    "Version": record.version
                })
            
            db.commit()
            
            # Background task to update PowerBI
            background_tasks.add_task(
                update_powerbi_async,
                submitted_data
            )
            
            return {
                "success": True,
                "submitted_records": len(records),
                "submission_time": submission_time.isoformat(),
                "message": "Data submitted successfully. PowerBI will be updated shortly."
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

async def update_powerbi_async(data: List[Dict[str, Any]]):
    """Background task to update PowerBI"""
    try:
        success = powerbi_service.push_data_to_dataset(data)
        if success:
            # Trigger dataset refresh
            powerbi_service.refresh_dataset()
            print(f"PowerBI updated successfully with {len(data)} records")
        else:
            print("Failed to update PowerBI")
    except Exception as e:
        print(f"PowerBI update error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    powerbi_status = powerbi_service.validate_connection()
    return {
        "status": "healthy",
        "powerbi_connected": powerbi_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/submission-status/{user_id}/{business_unit}")
async def get_submission_status(user_id: str, business_unit: str, db: Session = Depends(get_db)):
    """Get submission status for user"""
    try:
        total_records = db.query(BudgetData).filter(
            and_(
                BudgetData.user_id == user_id,
                BudgetData.business_unit == business_unit
            )
        ).count()
        
        submitted_records = db.query(BudgetData).filter(
            and_(
                BudgetData.user_id == user_id,
                BudgetData.business_unit == business_unit,
                BudgetData.is_submitted == True
            )
        ).count()
        
        latest_submission = db.query(BudgetData).filter(
            and_(
                BudgetData.user_id == user_id,
                BudgetData.business_unit == business_unit,
                BudgetData.is_submitted == True
            )
        ).order_by(BudgetData.submitted_at.desc()).first()
        
        return {
            "total_records": total_records,
            "submitted_records": submitted_records,
            "pending_records": total_records - submitted_records,
            "latest_submission": latest_submission.submitted_at.isoformat() if latest_submission else None,
            "completion_percentage": (submitted_records / total_records * 100) if total_records > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
