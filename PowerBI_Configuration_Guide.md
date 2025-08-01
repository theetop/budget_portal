# PowerBI Configuration Guide - Finding Your Keys

This guide will walk you through finding all the required keys for your `.env` file to connect the Budget Portal with PowerBI.

## 🎯 Required Keys Overview

You need to find these 5 key values for your `.env` file:

```env
POWERBI_CLIENT_ID=your_powerbi_client_id
POWERBI_CLIENT_SECRET=your_powerbi_client_secret
POWERBI_TENANT_ID=your_tenant_id
POWERBI_WORKSPACE_ID=your_workspace_id
POWERBI_DATASET_ID=your_dataset_id
```

---

## 🔐 Step 1: Get Azure AD Application Keys

### 1.1 Create Azure AD App Registration

1. **Go to Azure Portal**:
   - Navigate to [portal.azure.com](https://portal.azure.com)
   - Sign in with your organizational account

2. **Access App Registrations**:
   - Search for "App registrations" in the top search bar
   - Click on "App registrations"

3. **Create New Registration**:
   - Click "**+ New registration**"
   - Fill out the form:
     - **Name**: `Budget Portal PowerBI App`
     - **Supported account types**: `Accounts in this organizational directory only`
     - **Redirect URI**: Leave blank for now
   - Click "**Register**"

### 1.2 Get POWERBI_CLIENT_ID and POWERBI_TENANT_ID

After creating the app registration:

1. **Find Application (client) ID**:
   - On the app overview page, copy the **Application (client) ID**
   - This is your `POWERBI_CLIENT_ID`

2. **Find Directory (tenant) ID**:
   - On the same overview page, copy the **Directory (tenant) ID**
   - This is your `POWERBI_TENANT_ID`

### 1.3 Create POWERBI_CLIENT_SECRET

1. **Go to Certificates & secrets**:
   - In your app registration, click "**Certificates & secrets**" in the left menu

2. **Create New Client Secret**:
   - Click "**+ New client secret**"
   - Add description: `Budget Portal Secret`
   - Choose expiration: `24 months` (recommended)
   - Click "**Add**"

3. **Copy the Secret Value**:
   - ⚠️ **IMPORTANT**: Copy the **Value** immediately (not the Secret ID)
   - This is your `POWERBI_CLIENT_SECRET`
   - You cannot retrieve this value again after leaving the page!

### 1.4 Set API Permissions

1. **Go to API permissions**:
   - Click "**API permissions**" in the left menu

2. **Add PowerBI Permissions**:
   - Click "**+ Add a permission**"
   - Select "**Power BI Service**"
   - Choose "**Delegated permissions**"
   - Select these permissions:
     - `Dataset.ReadWrite.All`
     - `Workspace.Read.All`
     - `App.Read.All`
   - Click "**Add permissions**"

3. **Grant Admin Consent**:
   - Click "**Grant admin consent for [Your Organization]**"
   - Confirm by clicking "**Yes**"

---

## 🏢 Step 2: Get PowerBI Workspace ID

### 2.1 Access PowerBI Service

1. **Go to PowerBI Service**:
   - Navigate to [app.powerbi.com](https://app.powerbi.com)
   - Sign in with your PowerBI account

2. **Create or Select Workspace**:
   - If you don't have a workspace, create one:
     - Click "**Workspaces**" in the left menu
     - Click "**Create a workspace**"
     - Name it: `Budget Portal Workspace`
     - Click "**Save**"

### 2.2 Find Workspace ID

**Method 1: From URL**
1. Click on your workspace name
2. Look at the browser URL, it will be like:
   ```
   https://app.powerbi.com/groups/12345678-1234-1234-1234-123456789abc/
   ```
3. The GUID after `/groups/` is your `POWERBI_WORKSPACE_ID`

**Method 2: Using PowerBI REST API**
1. Open a new browser tab
2. Go to: `https://api.powerbi.com/v1.0/myorg/groups`
3. Find your workspace in the JSON response
4. Copy the `id` field value

### 2.3 Add Service Principal to Workspace

1. **Open Workspace Settings**:
   - In your workspace, click the "**Settings**" gear icon
   - Select "**Workspace settings**"

2. **Add Service Principal**:
   - Go to "**Access**" tab
   - Click "**+ Add**"
   - Enter your app's **Application (client) ID**
   - Set permission level to "**Admin**"
   - Click "**Add**"

---

## 📊 Step 3: Get PowerBI Dataset ID

### 3.1 Create Dataset (if needed)

If you don't have a dataset yet:

1. **Upload Sample Data**:
   - In your workspace, click "**+ New**"
   - Select "**Upload a file**"
   - Upload the `powerbi_source_data.csv` file from your project

2. **Or Create Dataset Manually**:
   - Click "**+ New**" → "**Dataset**"
   - Choose your data source
   - Follow the setup wizard

### 3.2 Find Dataset ID

**Method 1: From Dataset URL**
1. Click on your dataset name in the workspace
2. Look at the browser URL:
   ```
   https://app.powerbi.com/groups/[workspace-id]/datasets/87654321-4321-4321-4321-987654321abc/
   ```
3. The GUID after `/datasets/` is your `POWERBI_DATASET_ID`

**Method 2: Using PowerBI REST API**
1. Open browser and go to:
   ```
   https://api.powerbi.com/v1.0/myorg/groups/[YOUR_WORKSPACE_ID]/datasets
   ```
2. Replace `[YOUR_WORKSPACE_ID]` with your actual workspace ID
3. Find your dataset in the JSON response
4. Copy the `id` field value

**Method 3: Using PowerBI Desktop**
1. Open PowerBI Desktop
2. Connect to your PowerBI Service
3. Right-click on your dataset
4. Select "**Properties**"
5. Copy the Dataset ID

---

## 🔧 Step 4: Update Your .env File

Now update your `.env` file with all the collected values:

```env
# PowerBI Configuration
POWERBI_CLIENT_ID=12345678-1234-1234-1234-123456789abc
POWERBI_CLIENT_SECRET=abc123xyz789~secretvalue~here
POWERBI_TENANT_ID=87654321-4321-4321-4321-987654321abc
POWERBI_WORKSPACE_ID=11111111-2222-3333-4444-555555555555
POWERBI_DATASET_ID=99999999-8888-7777-6666-555555555555

# Database Configuration
DATABASE_URL=sqlite:///./budget_data.db

# Application Configuration
SECRET_KEY=your_secret_key_here
API_HOST=127.0.0.1
API_PORT=8000
```

---

## ✅ Step 5: Test Your Configuration

### 5.1 Run Connection Test

1. **Start the application**:
   ```bash
   python start_app.py
   ```

2. **Check API Health**:
   - Open browser to: `http://localhost:8000/api/health`
   - Look for: `"powerbi_connected": true`

3. **Check Streamlit App**:
   - Open: `http://localhost:8501`
   - Look for green "🟢 PowerBI Connected" in the sidebar

### 5.2 Test Data Flow

1. **Login to the app** with sample credentials:
   - User ID: `john.doe`
   - Business Unit: `Sales North`

2. **Edit some budget data** and click "**Submit to PowerBI**"

3. **Check PowerBI Service**:
   - Go back to your PowerBI workspace
   - Refresh your dataset
   - Verify new data appears

---

## 🚨 Common Issues and Solutions

### Issue 1: "Unauthorized" Error
**Problem**: App doesn't have proper permissions
**Solution**: 
- Verify API permissions are granted
- Ensure admin consent was given
- Check service principal is added to workspace

### Issue 2: "Invalid Client Secret"
**Problem**: Client secret expired or copied incorrectly
**Solution**:
- Generate new client secret
- Copy the **Value** (not Secret ID)
- Update .env file immediately

### Issue 3: "Workspace Not Found"
**Problem**: Wrong workspace ID or no access
**Solution**:
- Double-check workspace ID from URL
- Ensure service principal has Admin access to workspace
- Try using different workspace

### Issue 4: "Dataset Not Found"
**Problem**: Wrong dataset ID or dataset deleted
**Solution**:
- Verify dataset exists in the workspace
- Check dataset ID from URL or API
- Recreate dataset if necessary

### Issue 5: PowerBI Service Not Responding
**Problem**: Network or service issues
**Solution**:
- Check internet connection
- Verify PowerBI service status
- Try again in a few minutes

---

## 📋 Quick Checklist

Before testing, ensure you have:

- [ ] ✅ Created Azure AD app registration
- [ ] ✅ Copied Application (client) ID → `POWERBI_CLIENT_ID`
- [ ] ✅ Copied Directory (tenant) ID → `POWERBI_TENANT_ID`
- [ ] ✅ Generated and copied client secret → `POWERBI_CLIENT_SECRET`
- [ ] ✅ Added PowerBI API permissions
- [ ] ✅ Granted admin consent
- [ ] ✅ Found workspace ID → `POWERBI_WORKSPACE_ID`
- [ ] ✅ Added service principal to workspace as Admin
- [ ] ✅ Found dataset ID → `POWERBI_DATASET_ID`
- [ ] ✅ Updated .env file with all values
- [ ] ✅ Tested connection through health endpoint

---

## 📞 Need Help?

If you encounter issues:

1. **Check the application logs** for detailed error messages
2. **Verify all IDs** are copied correctly (no extra spaces/characters)
3. **Test individual components**:
   - Azure AD app permissions
   - PowerBI workspace access
   - Dataset existence
4. **Use PowerBI REST API documentation**: [docs.microsoft.com/en-us/rest/api/power-bi/](https://docs.microsoft.com/en-us/rest/api/power-bi/)

---

**🎉 Once all keys are configured correctly, your Budget Portal will seamlessly integrate with PowerBI for real-time data updates!**
