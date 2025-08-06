import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
from io import BytesIO
import time
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from st_aggrid.shared import JsCode
from config import config

# Page configuration
st.set_page_config(
    page_title="Budget Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration - Use environment-aware URL
API_BASE_URL = config.get_api_base_url()

# Custom CSS for Excel-like styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .editable-cell {
        background-color: #fef3c7;
        cursor: pointer;
    }
    
    .readonly-cell {
        background-color: #f3f4f6 !important;
        color: #6b7280 !important;
    }
    
    .status-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #10b981;
    }
    
    .submit-button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .submit-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'business_unit' not in st.session_state:
        st.session_state.business_unit = ""
    if 'session_token' not in st.session_state:
        st.session_state.session_token = ""
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame()
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()


def api_call(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
    """Make API calls with error handling and timeout"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        timeout = 30
        
        # Debug information (only show in development)
        # if not config.is_production():
            # st.info(f"Making {method} request to: {url}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if method == "GET":
            response = requests.get(url, params=data, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        else:
            response = requests.request(method, url, json=data, headers=headers, timeout=timeout)
        
        # Debug response status
        # if not config.is_production():
            # st.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_detail = response.json().get('detail', response.text)
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            
            st.error(error_msg)
            return {"success": False, "error": error_msg}
            
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out after {timeout} seconds. The server might be slow or unavailable."
        st.error(error_msg)
        return {"success": False, "error": "Request timeout"}
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Cannot connect to API server at {API_BASE_URL}. Please check if the server is running and accessible."
        st.error(error_msg)
        if not config.is_production():
            st.error(f"Connection error details: {str(e)}")
        return {"success": False, "error": "Connection failed"}
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        st.error(error_msg)
        return {"success": False, "error": str(e)}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        st.error(error_msg)
        return {"success": False, "error": str(e)}

def login_form():
    """Display login form"""
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Budget Portal</h1>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("Authentication")
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", placeholder="Enter your user ID")
        
        with col2:
            business_units = ['CHINA-01', 'CHINA-02', 'CHINA-03A', 'CHINA-03B', 'CHINA-04', 
                            'CHINA-05', 'CHINA-06', 'CHINA-07', 'CHINA-08', 'CHINA-09', 
                            'CHINA-10', 'CHINA-11', 'CHINA-12', 'CHINA-13', 'CHINA-14', 
                            'CHINA-15', 'CHINA-16', 'CHINA-17', 'CHINA-18', 'CHINA-19', 
                            'CHINA-20', 'CHINA-21', 'CHINA-22', 'CHINA-23', 'CHINA-24', 
                            'CHINA-25', 'CHINA-26', 'CHINA-NEW', 'CHINA-ROC']
            business_unit = st.selectbox("Business Unit", business_units)
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted and user_id:
            with st.spinner("Authenticating..."):
                result = api_call("/api/login", "POST", {
                    "user_id": user_id,
                    "business_unit": business_unit
                })
                
                if result.get("success"):
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_id
                    st.session_state.business_unit = business_unit
                    st.session_state.session_token = result.get("session_token")
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Authentication failed. Please try again.")

def load_user_data() -> pd.DataFrame:
    """Load user's budget data"""
    # URL encode business unit to handle spaces
    import urllib.parse
    print(st.session_state.business_unit)
    business_unit_encoded = urllib.parse.quote(st.session_state.business_unit)
    
    result = api_call(f"/api/data/{st.session_state.user_id}/{business_unit_encoded}", "GET")
    
    if result.get("success"):
        data = result.get("data", [])
        if data:
            df = pd.DataFrame(data)
            print(df)
            return df
    
    return pd.DataFrame()

def create_excel_grid(df: pd.DataFrame):
    """Create Excel-like grid with AgGrid"""
    if df.empty:
        st.warning("No data available for your business unit.")
        return {}
    
    # Add Index column to df
    df['Index'] = [i for i in range(len(df))]
    
    # Reorder columns to put 'Index' first
    cols = ['Index'] + [col for col in df.columns if col != 'Index']
    df = df[cols]
    
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Define column configurations
    editable_columns = ['Y2025B', 'Y2026P', 'Y2027P', 'Y2028P', 'Y2029P', 'Sales_Remark']
    readonly_columns = ['Index', 'Sales_Region', 'Customer_Note', 'Customer_Group', 'BizType',
            'Vendor_Category', 'Vendor_Grouping', 'ProductNature', 'Y2019A', 'Y2020A',
            'Y2021A', 'Y2022A', 'Y2023A', 'Y2024B', 'Y2024Q3F', 'Y2024A08', 'Y2024R08',
            'avg1924']
    pinned_columns = ['Index', 'Sales_Region', 'Customer_Note', 'Customer_Group', 'BizType']
    hidden_columns = ['id', 'user_id', 'business_unit']

    # Set column properties
    for col in df.columns:
        if col in hidden_columns:
            gb.configure_column(
                col,
                hide=True
            )
        elif col in pinned_columns:
            gb.configure_column(
                col, 
                editable=False,
                pinned='left',  # Pin to the left
                cellStyle=JsCode("""
                function(params) {
                    return {
                        'background-color': '#f3f4f6',
                        'color': '#6b7280',
                        'font-weight': 'bold'  // Optional: emphasize pinned columns
                    };
                }
                """)
            )
        elif col in editable_columns:
            gb.configure_column(
                col, 
                editable=True,
                cellStyle=JsCode("""
                function(params) {
                    return {
                        'background-color': '#fef3c7',
                        'font-weight': 'bold'
                    };
                }
                """)
            )
        elif col in readonly_columns:
            gb.configure_column(
                col,
                width=120,
                editable=False,
                cellStyle=JsCode("""
                function(params) {
                    return {
                        'background-color': '#f3f4f6',
                        'color': '#6b7280'
                    };
                }
                """)
            )
        else:
            continue  # Skip any columns not in editable or readonly lists
    
    # Grid options
    gb.configure_default_column(resizable=True, sortable=True, filter=True)
    gb.configure_grid_options(
        enableRowSelection=True,
        rowSelection="multiple",
        suppressRowClickSelection=False,
        enableRangeSelection=True,
        enableCellTextSelection=True,
        ensureDomOrder=True
    )
    
    grid_options = gb.build()
    
    # Display the grid
    st.subheader("Budget Data")

    
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        height=500,
        width='100%',
        theme='streamlit', 
        allow_unsafe_jscode=True
    )
    
    return grid_response

def save_changes(updated_data: pd.DataFrame):
    """Save changes to the database"""
    if updated_data.empty:
        return
    
    # Prepare updates
    updates = []
    for _, row in updated_data.iterrows():
        id_val = row.get("id")
        y2025b_val = row.get("Y2025B")
        y2026p_val = row.get("Y2026P")
        y2027p_val = row.get("Y2027P")
        y2028p_val = row.get("Y2028P")
        y2029p_val = row.get("Y2029P")
        sales_remark_val = row.get("Sales_Remark")
        update_dict = {
            "id": id_val,
            "Y2025B": 0 if pd.isna(y2025b_val) else y2025b_val,
            "Y2026P": 0 if pd.isna(y2026p_val) else y2026p_val,
            "Y2027P": 0 if pd.isna(y2027p_val) else y2027p_val,
            "Y2028P": 0 if pd.isna(y2028p_val) else y2028p_val,
            "Y2029P": 0 if pd.isna(y2029p_val) else y2029p_val,
            "Sales_Remark": "" if pd.isna(sales_remark_val) else sales_remark_val
        }
        updates.append(update_dict)
    
    with st.spinner("Saving changes..."):
        result = api_call("/api/update", "POST", {
            "user_id": st.session_state.user_id,
            "business_unit": st.session_state.business_unit,
            "updates": updates
        })
        
        if result.get("success"):
            st.success(f"✅ {result.get('message', 'Changes saved successfully!')}")
            return True
        else:
            st.error("❌ Failed to save changes")
            return False

def submit_data():
    """Submit budget data to PowerBI"""
    with st.spinner("Submitting data to PowerBI..."):
        result = api_call("/api/submit", "POST", {
            "user_id": st.session_state.user_id,
            "business_unit": st.session_state.business_unit
        })
        
        if result.get("success"):
            st.success("🎉 " + result.get("message", "Data submitted successfully!"))
            st.balloons()
            return True
        else:
            st.error("❌ Submission failed: " + result.get("error", "Unknown error"))
            return False

def display_dashboard():
    """Main dashboard interface"""
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 Budget Portal Dashboard</h1>
        <p>Welcome, {st.session_state.user_id} | {st.session_state.business_unit}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Controls")
        
        if st.button("Refresh Data", use_container_width=True):
            st.session_state.data = load_user_data()
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        st.markdown(f"**Last Refresh:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # Submission status
        st.subheader("Status")
        import urllib.parse
        business_unit_encoded = urllib.parse.quote(st.session_state.business_unit)
        status_result = api_call(f"/api/submission-status/{st.session_state.user_id}/{business_unit_encoded}", "GET")
        
        if status_result.get("success"):
            status = status_result
            completion = status.get("completion_percentage", 0)
            
            st.metric("Total Records", status.get("total_records", 0))
            st.metric("Submitted", status.get("submitted_records", 0))
            st.metric("Pending", status.get("pending_records", 0))
            
            # Progress bar
            st.progress(completion / 100)
            st.write(f"**Completion: {completion:.1f}%**")
            
            if status.get("latest_submission"):
                st.write(f"**Last Submission:** {status['latest_submission'][:16]}")
        
        # Health check
        health_result = api_call("/api/health", "GET")
        if health_result.get("status") == "healthy":
            st.success("🟢 API Server Connected")
        else:
            st.error("🔴 API Server Disconnected")
            if not config.is_production():
                st.info(f"API URL: {API_BASE_URL}")
        
        # PowerBI status (if available)
        if health_result.get("powerbi_connected"):
            st.success("🟢 PowerBI Connected")
        elif "powerbi_connected" in health_result:
            st.error("🔴 PowerBI Disconnected")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_id = ""
            st.session_state.business_unit = ""
            st.session_state.session_token = ""
            st.session_state.data = pd.DataFrame()
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Load data if not already loaded
    if st.session_state.data.empty:
        with st.spinner("Loading your budget data..."):
            st.session_state.data = load_user_data()
    
    # Main content area
    if not st.session_state.data.empty:
        grid_response = create_excel_grid(st.session_state.data)
        
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                if 'data' in grid_response and not grid_response['data'].empty:
                    if save_changes(grid_response['data']):
                        time.sleep(1)
                        st.rerun()
        
        with col2:
            if st.button("Submit to PowerBI", use_container_width=True, type="secondary"):
                if submit_data():
                    time.sleep(2)
                    st.rerun()
        
        with col3:
            if st.button("Export Data", use_container_width=True):
                export_data(st.session_state.data)
        
        # Data change detection
        if 'data' in grid_response:
            current_data = grid_response['data']
            if not current_data.equals(st.session_state.data):
                st.info("🔄 **Data has been modified.** Remember to save your changes!")
    
    else:
        st.info("📝 No budget data found. Data will be loaded from PowerBI when available.")

def export_data(df: pd.DataFrame):
    """Export data to Excel"""
    if not df.empty:
        # Convert to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        st.download_button(
            label="📥 Download Excel File",
            data=output,
            file_name=f"budget_data_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def main():
    """Main application function"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_form()
    else:
        display_dashboard()

if __name__ == "__main__":
    main()
