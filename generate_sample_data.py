"""
Sample Data Generator for Budget Portal
This script creates sample data for testing the application
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import sqlite3
import os

def generate_sample_data():
    """Generate sample budget data for testing"""
    
    # Sample data parameters
    business_units = ["Sales North", "Sales South", "Marketing", "Operations", "Finance"]
    users = {
        "Sales North": ["john.doe", "jane.smith", "mike.johnson"],
        "Sales South": ["sarah.wilson", "david.brown", "lisa.davis"],
        "Marketing": ["chris.taylor", "amanda.white", "robert.garcia"],
        "Operations": ["jennifer.martinez", "michael.anderson", "emily.thomas"],
        "Finance": ["daniel.jackson", "michelle.lee", "kevin.harris"]
    }
    
    product_categories = ["Laptops", "Desktops", "Servers", "Networking", "Software", "Services"]
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Africa"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    current_year = datetime.now().year
    
    data = []
    
    for bu, user_list in users.items():
        for user in user_list:
            for quarter in quarters:
                for category in product_categories:
                    for region in regions:
                        # Generate realistic financial data
                        historical_sales = random.uniform(100000, 500000)
                        target_sales = historical_sales * random.uniform(1.05, 1.25)  # 5-25% growth
                        market_share = random.uniform(0.05, 0.30)  # 5-30% market share
                        
                        # Some records have budget data, some don't (for testing)
                        if random.random() > 0.3:  # 70% have budget data
                            budget_amount = target_sales * random.uniform(0.8, 1.2)
                            forecast_sales = budget_amount * random.uniform(0.9, 1.1)
                            comments = random.choice([
                                "Conservative estimate based on market conditions",
                                "Aggressive growth strategy planned",
                                "Stable market, maintaining current levels",
                                "New product launch expected to boost sales",
                                "Economic uncertainty factored in",
                                ""
                            ])
                        else:
                            budget_amount = None
                            forecast_sales = None
                            comments = "Pending review"
                        
                        record = {
                            "business_unit": bu,
                            "user_id": user,
                            "product_category": category,
                            "region": region,
                            "quarter": quarter,
                            "year": current_year,
                            "historical_sales": round(historical_sales, 2),
                            "target_sales": round(target_sales, 2),
                            "market_share": round(market_share, 4),
                            "budget_amount": round(budget_amount, 2) if budget_amount else None,
                            "forecast_sales": round(forecast_sales, 2) if forecast_sales else None,
                            "comments": comments,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now(),
                            "submitted_at": None,
                            "is_submitted": False,
                            "version": 1
                        }
                        
                        data.append(record)
    
    return pd.DataFrame(data)

def create_sample_database():
    """Create SQLite database with sample data"""
    
    # Remove existing database
    db_path = "budget_data.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Generate sample data
    print("Generating sample data...")
    df = generate_sample_data()
    print(f"Generated {len(df)} sample records")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    
    # Create budget_data table
    create_table_sql = """
    CREATE TABLE budget_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_unit TEXT NOT NULL,
        user_id TEXT NOT NULL,
        product_category TEXT NOT NULL,
        region TEXT NOT NULL,
        quarter TEXT NOT NULL,
        year INTEGER NOT NULL,
        historical_sales REAL,
        target_sales REAL,
        market_share REAL,
        budget_amount REAL,
        forecast_sales REAL,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        submitted_at TIMESTAMP,
        is_submitted BOOLEAN DEFAULT FALSE,
        version INTEGER DEFAULT 1
    );
    """
    
    conn.execute(create_table_sql)
    
    # Create user_sessions table
    create_sessions_sql = """
    CREATE TABLE user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL UNIQUE,
        business_unit TEXT NOT NULL,
        session_token TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    
    conn.execute(create_sessions_sql)
    
    # Insert sample data
    df.to_sql('budget_data', conn, if_exists='append', index=False)
    
    # Create indexes
    conn.execute("CREATE INDEX idx_bu_user_quarter ON budget_data(business_unit, user_id, quarter, year);")
    conn.execute("CREATE INDEX idx_submission_status ON budget_data(is_submitted, submitted_at);")
    conn.execute("CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Sample database created: {db_path}")
    
    # Display summary
    print("\n📊 Sample Data Summary:")
    print(f"Total records: {len(df)}")
    print(f"Business units: {df['business_unit'].nunique()}")
    print(f"Users: {df['user_id'].nunique()}")
    print(f"Product categories: {df['product_category'].nunique()}")
    print(f"Regions: {df['region'].nunique()}")
    
    # Show records with and without budget data
    with_budget = df[df['budget_amount'].notna()]
    without_budget = df[df['budget_amount'].isna()]
    print(f"Records with budget data: {len(with_budget)} ({len(with_budget)/len(df)*100:.1f}%)")
    print(f"Records without budget data: {len(without_budget)} ({len(without_budget)/len(df)*100:.1f}%)")
    
    # Sample users by business unit
    print("\n👥 Sample Users by Business Unit:")
    user_summary = df.groupby('business_unit')['user_id'].unique()
    for bu, users in user_summary.items():
        print(f"  {bu}: {', '.join(users)}")

def create_powerbi_sample_data():
    """Create sample data in PowerBI format (CSV files)"""
    
    print("\n📋 Creating PowerBI sample data files...")
    
    df = generate_sample_data()
    
    # Create PowerBI source data (read-only columns)
    powerbi_source = df[['business_unit', 'user_id', 'product_category', 'region', 
                        'quarter', 'year', 'historical_sales', 'target_sales', 'market_share']].copy()
    
    powerbi_source.to_csv('powerbi_source_data.csv', index=False)
    print("✅ Created: powerbi_source_data.csv")
    
    # Create PowerBI submission data (editable columns that get updated)
    submitted_data = df[df['budget_amount'].notna()][
        ['business_unit', 'user_id', 'product_category', 'region', 'quarter', 'year',
         'budget_amount', 'forecast_sales', 'comments', 'submitted_at', 'version']
    ].copy()
    
    submitted_data.to_csv('powerbi_submission_data.csv', index=False)
    print("✅ Created: powerbi_submission_data.csv")
    
    print("\n💡 PowerBI Integration Notes:")
    print("1. Import 'powerbi_source_data.csv' as your main data source")
    print("2. Import 'powerbi_submission_data.csv' as your submission tracking table")
    print("3. Create relationships between tables on business_unit, user_id, product_category, region, quarter, year")
    print("4. Set up Row Level Security (RLS) to filter by business_unit and user_id")
    print("5. The application will update 'powerbi_submission_data.csv' on each submission")

if __name__ == "__main__":
    print("🏢 Budget Portal - Sample Data Generator")
    print("=" * 50)
    
    try:
        create_sample_database()
        create_powerbi_sample_data()
        
        print("\n🎉 Sample data generation completed successfully!")
        print("\n🚀 Next Steps:")
        print("1. Configure your PowerBI credentials in .env file")
        print("2. Set up PowerBI workspace and dataset")
        print("3. Run 'python start_app.py' or 'start_budget_portal.bat' to start the application")
        print("4. Login with any of the sample users (e.g., john.doe, jane.smith)")
        
    except Exception as e:
        print(f"❌ Error generating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
