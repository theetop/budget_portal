import requests
import msal
import pandas as pd
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

load_dotenv()

class PowerBIService:
    def __init__(self):
        self.client_id = os.getenv("POWERBI_CLIENT_ID")
        self.client_secret = os.getenv("POWERBI_CLIENT_SECRET")
        self.tenant_id = os.getenv("POWERBI_TENANT_ID")
        self.workspace_id = os.getenv("POWERBI_WORKSPACE_ID")
        self.dataset_id = os.getenv("POWERBI_DATASET_ID")
        self.sales_china_id = os.getenv("SALES_CHINA_ID")

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://analysis.windows.net/powerbi/api/.default"]
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        result = self.app.acquire_token_for_client(scopes=self.scope)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            # Set expiry to be 5 minutes before actual expiry
            self.token_expiry = datetime.now() + timedelta(seconds=result["expires_in"] - 300)
            return self.access_token
        else:
            raise Exception(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_dataset_data(self, table_name: str = "BudgetData", 
                        filter_clause: str = None) -> pd.DataFrame:
        """Fetch data from PowerBI dataset"""
        headers = self.get_headers()
        
        # Build DAX query
        dax_query = f"EVALUATE '{table_name}'"
        if filter_clause:
            dax_query = f"EVALUATE FILTER('{table_name}', {filter_clause})"
        
        query_url = f"{self.base_url}/groups/{self.workspace_id}/datasets/{self.dataset_id}/executeQueries"
        
        payload = {
            "queries": [
                {
                    "query": dax_query
                }
            ],
            "serializerSettings": {
                "includeNulls": True
            }
        }
        
        try:
            response = requests.post(query_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("results") and len(result["results"]) > 0:
                tables = result["results"][0].get("tables", [])
                if tables:
                    rows = tables[0].get("rows", [])
                    if rows:
                        return pd.DataFrame(rows)
            
            return pd.DataFrame()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch data from PowerBI: {str(e)}")
    
    def push_data_to_dataset(self, data: List[Dict[str, Any]], 
                           table_name: str = "BudgetSubmissions") -> bool:
        """Push updated budget data to PowerBI dataset"""
        headers = self.get_headers()
        
        push_url = f"{self.base_url}/groups/{self.workspace_id}/datasets/{self.dataset_id}/tables/{table_name}/rows"
        
        try:
            # Clear existing data first (optional, depending on your needs)
            delete_url = f"{self.base_url}/groups/{self.workspace_id}/datasets/{self.dataset_id}/tables/{table_name}/rows"
            requests.delete(delete_url, headers=headers)
            
            # Push new data
            payload = {"rows": data}
            response = requests.post(push_url, headers=headers, json=payload)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to push data to PowerBI: {str(e)}")
            return False
    
    def refresh_dataset(self) -> bool:
        """Trigger dataset refresh"""
        headers = self.get_headers()
        refresh_url = f"{self.base_url}/groups/{self.workspace_id}/datasets/{self.dataset_id}/refreshes"
        
        try:
            payload = {"notifyOption": "NoNotification"}
            response = requests.post(refresh_url, headers=headers, json=payload)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to refresh dataset: {str(e)}")
            return False
    
    def get_user_data_with_rls(self, user_id: str, business_unit: str) -> pd.DataFrame:
        """Get data filtered by Row Level Security for specific user"""
        # This simulates RLS - in real implementation, RLS would be configured in PowerBI
        filter_clause = f"[BusinessUnit] = '{business_unit}' && [UserId] = '{user_id}'"
        return self.get_dataset_data(filter_clause=filter_clause)
    
    def validate_connection(self) -> bool:
        """Test PowerBI connection"""
        try:
            headers = self.get_headers()
            test_url = f"{self.base_url}/groups/{self.workspace_id}/datasets/{self.sales_china_id}"
            response = requests.get(test_url, headers=headers)
            print(test_url)
            return response.status_code == 200
        except:
            return False
