from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
import threading
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel

from powerbi_service import PowerBIService

from DatabaseManager import get_db, China2025B, UserSession, create_tables

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

class BudgetUpdateRequest(BaseModel):
    user_id: str
    business_unit: str
    updates: List[Dict]

@app.get("/data")
async def get_data(db: Session = Depends(get_db)):
    """Get all data from china_2025B table"""
    try:
        data = db.query(China2025B).all()
        result = [
            {
                "id": item.id,
                "user_id": item.user_id,
                "business_unit": item.business_unit,
                "Sales_Region": item.Sales_Region,
                "Customer_Note": item.Customer_Note,
                "Customer_Group": item.Customer_Group,
                "BizType": item.BizType,
                "Vendor_Category": item.Vendor_Category,
                "Vendor_Grouping": item.Vendor_Grouping,
                "ProductNature": item.ProductNature,
                "Y2019A": item.Y2019A,
                "Y2020A": item.Y2020A,
                "Y2021A": item.Y2021A,
                "Y2022A": item.Y2022A,
                "Y2023A": item.Y2023A,
                "Y2024B": item.Y2024B,
                "Y2024Q3F": item.Y2024Q3F,
                "Y2024A08": item.Y2024A08,
                "Y2024R08": item.Y2024R08,
                "avg1924": item.avg1924,
                "Y2025B": item.Y2025B,
                "Y2026P": item.Y2026P,
                "Y2027P": item.Y2027P,
                "Y2028P": item.Y2028P,
                "Y2029P": item.Y2029P,
                "Sales_Remark": item.Sales_Remark
            } for item in data
        ]
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

@app.post("/api/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and create session"""
    try:
        user = db.query(UserSession).filter(UserSession.user_id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        # Validate business unit if needed
        if not request.business_unit:
            raise HTTPException(status_code=400, detail="Business unit required")
        
        # Generate session token
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=8)
        
        # Check if user session exists
        existing_session = db.query(UserSession).filter(
            UserSession.user_id == request.user_id,
        ).first()
        
        if existing_session:
            existing_session.session_token = session_token
            existing_session.expires_at = expires_at
            existing_session.is_active = True
        else:
            new_session = UserSession(
                user_id=request.user_id,
                business_unit=request.business_unit,
                session_token=session_token,
                expires_at=expires_at
            )
            db.add(new_session)
        
        db.commit()
        
        return {
            "success": True,
            "session_token": session_token,
            "user_id": request.user_id,
            "business_unit": request.business_unit,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/data/{user_id}/{business_unit}")
async def get_user_data(user_id: str, business_unit: str, db: Session = Depends(get_db)):
    """Get data for specific user with RLS"""
    try:
        # First try to get data from local database
        local_data = db.query(China2025B).filter(
            and_(
                China2025B.user_id == user_id,
                China2025B.business_unit == business_unit
            )
        ).all()
        
        # If no local data, fetch from PowerBI
        if not local_data:
            raise HTTPException(status_code=404, detail="No data found for user and business unit")
            '''
            powerbi_data = powerbi_service.get_user_data_with_rls(user_id, business_unit)

            if not powerbi_data.empty:
                # Convert PowerBI data to local format and store
                for _, row in powerbi_data.iterrows():
                    budget_entry = China2025B(
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
                local_data = db.query(China2025B).filter(
                    and_(
                        China2025B.user_id == user_id,
                        China2025B.business_unit == business_unit
                    )
                ).all()
            '''
        
        result = [
            {
                "id": item.id,
                "user_id": item.user_id,
                "business_unit": item.business_unit,
                "Sales_Region": item.Sales_Region,
                "Customer_Note": item.Customer_Note,
                "Customer_Group": item.Customer_Group,
                "BizType": item.BizType,
                "Vendor_Category": item.Vendor_Category,
                "Vendor_Grouping": item.Vendor_Grouping,
                "ProductNature": item.ProductNature,
                "Y2019A": item.Y2019A,
                "Y2020A": item.Y2020A,
                "Y2021A": item.Y2021A,
                "Y2022A": item.Y2022A,
                "Y2023A": item.Y2023A,
                "Y2024B": item.Y2024B,
                "Y2024Q3F": item.Y2024Q3F,
                "Y2024A08": item.Y2024A08,
                "Y2024R08": item.Y2024R08,
                "avg1924": item.avg1924,
                "Y2025B": item.Y2025B,
                "Y2026P": item.Y2026P,
                "Y2027P": item.Y2027P,
                "Y2028P": item.Y2028P,
                "Y2029P": item.Y2029P,
                "Sales_Remark": item.Sales_Remark
            } for item in local_data
        ]
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

@app.post("/api/update")
async def update_budget_data(
    request: BudgetUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update budget data with thread safety"""
    with data_lock:
        try:
            updated_records = []
            
            for update in request.updates:
                record_id = update.get("id")
                if not record_id:
                    continue
                
                # Get existing record
                record = db.query(China2025B).filter(
                    and_(
                        China2025B.id == record_id,
                        China2025B.user_id == request.user_id,
                        China2025B.business_unit == request.business_unit
                    )
                ).first()
                
                if record:
                    # Update editable fields only
                    if "Y2025B" in update:
                        record.Y2025B = update["Y2025B"]
                    if "Y2026P" in update:
                        record.Y2026P = update["Y2026P"]
                    if "Y2027P" in update:
                        record.Y2027P = update["Y2027P"]
                    if "Y2028P" in update:
                        record.Y2028P = update["Y2028P"]
                    if "Y2029P" in update:
                        record.Y2029P = update["Y2029P"]
                    if "Sales_Remark" in update:
                        record.Sales_Remark = update["Sales_Remark"]
                    
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
            records = db.query(China2025B).filter(
                and_(
                    China2025B.user_id == user_id,
                    China2025B.business_unit == business_unit,
                )
            ).all()
            
            if not records:
                raise HTTPException(status_code=400, detail="No records to submit")
            
            submitted_data = [
                {
                    "user_id": record.user_id,
                    "business_unit": record.business_unit,
                    "Y2025B": record.Y2025B,
                    "Y2026P": record.Y2026P,
                    "Y2027P": record.Y2027P,
                    "Y2028P": record.Y2028P,
                    "Y2029P": record.Y2029P,
                    "Sales_Remark": record.Sales_Remark
                } for record in records
            ]
            
            db.commit()
            
            # Background task to update PowerBI
            background_tasks.add_task(
                update_powerbi_async,
                submitted_data
            )
            
            return {
                "success": True,
                "submitted_records": len(records),
                "message": "Data submitted successfully. PowerBI will be updated shortly."
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

async def update_powerbi_async(data: List[Dict[str, Any]]):
    """Background task to update PowerBI
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
    """
    
    try:
        df = pd.DataFrame(data)
        df.to_csv('temp1_Powerbi_submission_data.csv', index=False)
        print(f"PowerBI submission CSV updated with {len(data)} records")
    except Exception as e:
        print(f"PowerBI CSV update error: {str(e)}")

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
async def get_submission_status(
    user_id: str, 
    business_unit: str, 
    db: Session = Depends(get_db)
):
    """Get submission status for user"""
    try:
        total_records = db.query(China2025B).filter(
            and_(
                China2025B.user_id == user_id,
                China2025B.business_unit == business_unit
            )
        ).count()
        
        return {
            "total_records": total_records,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
