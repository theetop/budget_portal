# Budget Portal - Excel-like Interface with PowerBI Integration

A comprehensive web application that provides an Excel-like interface for BU leaders to submit budget and sales data with Row Level Security (RLS), direct PowerBI integration, and support for simultaneous multi-user updates.

## 🚀 Deployment

### Frontend Deployment (Streamlit Cloud)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file path: `streamlit_app.py`
   - Configure secrets in Streamlit Cloud dashboard

3. **Configure Streamlit Secrets**:
   In Streamlit Cloud dashboard, add these secrets:
   ```toml
   [general]
   ENVIRONMENT = "production"
   API_BASE_URL = "https://your-backend-app.onrender.com"

   [database]
   DATABASE_URL = "your-production-database-url"

   [powerbi]
   POWERBI_CLIENT_ID = "your-powerbi-client-id"
   POWERBI_CLIENT_SECRET = "your-powerbi-client-secret"
   POWERBI_TENANT_ID = "your-powerbi-tenant-id"
   POWERBI_WORKSPACE_ID = "your-powerbi-workspace-id"
   POWERBI_DATASET_ID = "your-powerbi-dataset-id"

   [security]
   SECRET_KEY = "your-production-secret-key"
   SESSION_TIMEOUT_HOURS = "8"
   ```

### Backend Deployment (Render)

1. **Create Render Account**: Go to [render.com](https://render.com)

2. **Deploy Backend**:
   - Connect your GitHub repository
   - Create a new "Web Service"
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `uvicorn APIServer:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment Variables** in Render dashboard:
   ```
   ENVIRONMENT=production
   DATABASE_URL=your-database-url
   POWERBI_CLIENT_ID=your-client-id
   POWERBI_CLIENT_SECRET=your-client-secret
   POWERBI_TENANT_ID=your-tenant-id
   POWERBI_WORKSPACE_ID=your-workspace-id
   POWERBI_DATASET_ID=your-dataset-id
   SECRET_KEY=your-secret-key
   ```

4. **Update Frontend Configuration**:
   - Copy your Render backend URL
   - Update the `API_BASE_URL` in Streamlit secrets
   - Redeploy the Streamlit app

### Database Options

**Option 1: PostgreSQL (Recommended for Production)**
```bash
# Add to requirements.txt
psycopg2-binary>=2.9.7

# Update DATABASE_URL
DATABASE_URL=postgresql://username:password@host:port/database
```

**Option 2: SQLite (Simple, but limited)**
```bash
# Keep current setup - works for small deployments
DATABASE_URL=sqlite:///./budget_data.db
```

### Post-Deployment Checklist

- [ ] Backend API is accessible at your Render URL
- [ ] Frontend can connect to the backend
- [ ] Database connection is working
- [ ] PowerBI integration is configured
- [ ] Environment variables are set correctly
- [ ] Health check endpoint returns "healthy" status
- [ ] User authentication works
- [ ] Data loading and saving functions properly

## 🛠️ Development vs Production

### Environment Configuration
The application automatically detects the environment based on the `ENVIRONMENT` variable:

- **Development**: Uses local database, allows all CORS origins
- **Production**: Uses production database, restricts CORS origins

### CORS Configuration
- **Development**: Allows all origins (`["*"]`)
- **Production**: Restricts to trusted domains (Streamlit Cloud, your domain)

### Security Considerations
- Change default secret keys in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement proper logging and monitoring

## 🎯 Key Features

### Excel-like Interface
- **Editable Grid**: Excel-like table interface using Streamlit AgGrid
- **Visual Indicators**: Clearly marked editable vs read-only columns
- **Real-time Updates**: Live data editing with immediate visual feedback
- **Multi-cell Selection**: Copy/paste and bulk operations support

### Concurrent User Support
- **Thread-safe Operations**: Multiple users can edit simultaneously without data corruption
- **Row-level Locking**: Prevents conflicts during database updates
- **Session Management**: User authentication with session tokens
- **Real-time Synchronization**: Changes are immediately visible to all users

### PowerBI Integration
- **Direct Data Connection**: Fetches source data from PowerBI semantic model
- **Automated Updates**: Submitted data automatically updates PowerBI datasets
- **Dataset Refresh**: Triggers PowerBI dataset refresh after submissions
- **Row Level Security**: Respects PowerBI RLS configurations

### Security & Access Control
- **User Authentication**: Simple login system with business unit assignment
- **Row Level Security**: Users only see data relevant to their business unit
- **Session Management**: Secure session tokens with expiration
- **Audit Trail**: Complete tracking of data changes and submissions

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI       │    │    PowerBI      │
│   Frontend      │◄──►│    Backend       │◄──►│    Service      │
│                 │    │                  │    │                 │
│ - Excel-like UI │    │ - Thread Safety  │    │ - Data Source   │
│ - User Auth     │    │ - Concurrent     │    │ - Dataset       │
│ - Data Editing  │    │   Updates        │    │ - Refresh       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    SQLite       │
                       │   Database      │
                       │                 │
                       │ - Temp Storage  │
                       │ - User Sessions │
                       │ - Change Log    │
                       └─────────────────┘
```

## 📁 Project Structure

```
budget_portal/
├── streamlit_app.py           # Main Streamlit frontend application
├── api_server.py              # FastAPI backend server
├── database.py                # Database models and configuration
├── powerbi_service.py         # PowerBI REST API integration
├── start_app.py               # Application startup script
├── generate_sample_data.py    # Sample data generator for testing
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
├── start_budget_portal.bat    # Windows startup script
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- PowerBI Pro or Premium license
- Azure AD application registration (for PowerBI API)

### 2. Installation

**Option A: Using Windows Batch File (Recommended for Windows)**
```bash
# Double-click or run in command prompt
start_budget_portal.bat
```

**Option B: Manual Setup**
```bash
# Clone or download the project
cd budget_portal

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Generate sample data (optional)
python generate_sample_data.py

# Start the application
python start_app.py
```

### 3. Configuration

Edit the `.env` file with your PowerBI credentials:

```env
# PowerBI Configuration
POWERBI_CLIENT_ID=your_powerbi_client_id
POWERBI_CLIENT_SECRET=your_powerbi_client_secret
POWERBI_TENANT_ID=your_tenant_id
POWERBI_WORKSPACE_ID=your_workspace_id
POWERBI_DATASET_ID=your_dataset_id

# Database Configuration
DATABASE_URL=sqlite:///./budget_data.db

# Application Configuration
SECRET_KEY=your_secret_key_here
API_HOST=127.0.0.1
API_PORT=8000
```

### 4. PowerBI Setup

1. **Create Azure AD Application**:
   - Go to Azure Portal → App Registrations
   - Create new registration
   - Add PowerBI Service permissions
   - Generate client secret

2. **Configure PowerBI Workspace**:
   - Create a workspace in PowerBI Service
   - Add your service principal as admin
   - Create dataset with required tables

3. **Set Up Row Level Security**:
   - Configure RLS rules in PowerBI
   - Filter by BusinessUnit and UserId columns

## 🎮 Usage

### For BU Leaders

1. **Login**:
   - Navigate to `http://localhost:8501`
   - Enter your User ID and select Business Unit
   - Click "Login"

2. **Edit Budget Data**:
   - Yellow highlighted columns are editable (Budget Amount, Forecast Sales, Comments)
   - Gray columns are read-only (historical data from PowerBI)
   - Click any editable cell to modify values
   - Use Tab/Enter to navigate between cells

3. **Save Changes**:
   - Click "Save Changes" to store modifications locally
   - Changes are immediately available to other users

4. **Submit to PowerBI**:
   - Click "Submit to PowerBI" to finalize data
   - This triggers PowerBI dataset refresh
   - Submitted data becomes read-only

### For Administrators

1. **Monitor System Health**:
   - API health endpoint: `http://localhost:8000/api/health`
   - Check PowerBI connection status
   - Monitor user sessions

2. **Data Management**:
   - Use `generate_sample_data.py` to create test data
   - Monitor database through SQL tools
   - Track submission status via API endpoints

## 🔧 API Endpoints

### Authentication
- `POST /api/login` - User authentication
- `GET /api/submission-status/{user_id}` - Get user submission status

### Data Operations
- `GET /api/data/{user_id}` - Fetch user data with RLS
- `POST /api/update` - Update budget data (thread-safe)
- `POST /api/submit` - Submit data to PowerBI

### System
- `GET /api/health` - Health check and PowerBI status

## 🛡️ Security Features

### Concurrent Access Protection
- **Database Transactions**: All updates wrapped in transactions
- **Thread Locking**: `threading.RLock()` prevents race conditions
- **Version Control**: Record versioning prevents overwrite conflicts
- **Session Validation**: Token-based session management

### Row Level Security
- **Business Unit Filtering**: Users only see their BU data
- **User ID Filtering**: Additional user-level restrictions
- **PowerBI RLS**: Leverages PowerBI's native RLS capabilities
- **API-level Filtering**: Backend enforces access controls

## 📊 Sample Data

The application includes a sample data generator with:
- **5 Business Units**: Sales North/South, Marketing, Operations, Finance
- **15 Sample Users**: 3 users per business unit
- **6 Product Categories**: Laptops, Desktops, Servers, etc.
- **5 Regions**: North America, Europe, Asia Pacific, etc.
- **4 Quarters**: Q1, Q2, Q3, Q4

Run `python generate_sample_data.py` to create test data.

## 🔧 Troubleshooting

### Common Issues

**1. "Cannot connect to API server"**
- Ensure FastAPI server is running on port 8000
- Check if port is blocked by firewall
- Verify API_HOST and API_PORT in .env

**2. "PowerBI Disconnected"**
- Verify PowerBI credentials in .env file
- Check Azure AD app permissions
- Ensure service principal has workspace access

**3. "No data available"**
- Run sample data generator first
- Check database connection
- Verify user has data for their business unit

**4. "Save changes failed"**
- Check database write permissions
- Verify record IDs are valid
- Look for concurrent access conflicts

### Performance Optimization

1. **Database Indexes**: Ensure proper indexing on filtered columns
2. **Connection Pooling**: Configure SQLAlchemy connection pool
3. **Caching**: Implement Redis for session caching
4. **Batch Operations**: Group updates for better performance

## 🔄 Development

### Adding New Features

1. **New Columns**: Update `BudgetData` model in `database.py`
2. **New Endpoints**: Add routes in `api_server.py`
3. **UI Changes**: Modify `streamlit_app.py`
4. **PowerBI Integration**: Extend `powerbi_service.py`

### Testing

```bash
# Run with sample data
python generate_sample_data.py
python start_app.py

# Test API endpoints
curl http://localhost:8000/api/health

# Test concurrent access
# Open multiple browser tabs and edit simultaneously
```

## 📈 Monitoring

### Application Metrics
- User session count
- Submission success rate
- PowerBI sync status
- Database performance

### Logging
- API request logs
- Error tracking
- Performance metrics
- User activity audit

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review API documentation at `http://localhost:8000/docs`
3. Check application logs
4. Create GitHub issue with detailed description

---
