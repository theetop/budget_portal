import os
import random
import sqlite3
import pandas as pd

def retrieve_data():
    try:
        df = pd.read_excel("2025B_Rev.xlsx", sheet_name="CHINA", header=2, usecols=['Sales Region', 'Customer Note', 'Customer Group', 'BizType',
            'Vendor Category', 'Vendor Grouping', 'ProductNature'])
        
        df.columns = [col.strip().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        Customer_Note = df['Customer_Note']
        users = {
            Customer_Note.unique()[i]: f'john_doe{i}' 
            for i in range(len(Customer_Note.unique()))
        }

        df['user_id'] = df['Customer_Note'].map(users)
        df['business_unit'] = df['Customer_Note']

        hist_sales_col = [
            'Y2019A', 'Y2020A', 'Y2021A', 'Y2022A', 'Y2023A', 'Y2024B', 'Y2024Q3F', 
            'Y2024A08', 'Y2024R08', 'avg1924', 'Y2025B', 'Y2026P', 'Y2027P', 
            'Y2028P', 'Y2029P'
        ]
        
        for col in hist_sales_col:
            df[col] = [random.uniform(100000, 500000) for _ in range(len(df))]

        df['Sales_Remark'] = ''
        df['Sales_Remark'] = df['Sales_Remark'].astype(str)
        print(df.columns)
        return df
        
    except FileNotFoundError:
        print("Error: 2025B_Rev.xlsx file not found")
    except KeyError as e:
        print(f"Error: Column not found - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        
def create_database():
    db_path = "China_2025B.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    print("Generating data...")
    df = retrieve_data()
    if df is not None:
        conn = sqlite3.connect(db_path)
        
        # Create China_2025B table
        create_table_sql = """
        CREATE TABLE China_2025B (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            business_unit TEXT NOT NULL,
            Sales_Region VARCHAR(100),
            Customer_Note VARCHAR(255),
            Customer_Group VARCHAR(100),
            BizType VARCHAR(50),
            Vendor_Category VARCHAR(100),
            Vendor_Grouping VARCHAR(100),
            ProductNature VARCHAR(100),
            Y2019A DECIMAL(15,2),
            Y2020A DECIMAL(15,2),
            Y2021A DECIMAL(15,2),
            Y2022A DECIMAL(15,2),
            Y2023A DECIMAL(15,2),
            Y2024B DECIMAL(15,2),
            Y2024Q3F DECIMAL(15,2),
            Y2024A08 DECIMAL(15,2),
            Y2024R08 DECIMAL(15,2),
            avg1924 DECIMAL(15,2),
            Y2025B DECIMAL(15,2),
            Y2026P DECIMAL(15,2),
            Y2027P DECIMAL(15,2),
            Y2028P DECIMAL(15,2),
            Y2029P DECIMAL(15,2),
            Sales_Remark TEXT DEFAULT ''
        );
        """
        
        conn.execute(create_table_sql)
        
        # Create user_sessions table
        create_sessions_sql = """
        CREATE TABLE user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            business_unit TEXT NOT NULL
        );
        """
        
        conn.execute(create_sessions_sql)
        df.to_sql('China_2025B', conn, if_exists='append', index=False)
        
        user_sessions = df[['user_id', 'business_unit']].drop_duplicates()
        user_sessions.to_sql('user_sessions', conn, if_exists='append', index=False)

        # Create indexes
        conn.execute("CREATE INDEX idx_user_id ON China_2025B(user_id);")
        conn.execute("CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Sample database created: {db_path}")
        
        # Display summary
        print("\n📊 Sample Data Summary:")
        print(f"Total records: {len(df)}")
        print(f"Business units: {df['business_unit'].nunique()}")
        print(f"Users: {df['user_id'].nunique()}")

def create_powerbi_sample_data():
    """Create sample data in PowerBI format (CSV files)"""
    
    print("\n📋 Creating PowerBI sample data files...")
    
    df = retrieve_data()
    
    if df is not None:
    
        # Create PowerBI source data (read-only columns)
        powerbi_source = df[['Sales_Region', 'Customer_Note', 'Customer_Group', 'BizType',
            'Vendor_Category', 'Vendor_Grouping', 'ProductNature', 'user_id',
            'business_unit', 'Y2019A', 'Y2020A', 'Y2021A', 'Y2022A', 'Y2023A', 'Y2024B',
            'Y2024Q3F', 'Y2024A08', 'Y2024R08', 'avg1924']].copy()

        powerbi_source.to_csv('China_2025B_powerbi_source_data.csv', index=False)
        
        # Create PowerBI submission data (editable columns that get updated)
        submitted_data = df[['user_id', 'business_unit', 'Y2025B', 'Y2026P', 'Y2027P', 'Y2028P', 'Y2029P', 'Sales_Remark']].copy()
        submitted_data.to_csv('China_2025B_powerbi_submission_data.csv', index=False)
        

if __name__ == "__main__":
    try:
        create_database()
        create_powerbi_sample_data()
        
    except Exception as e:
        print(f"❌ Error generating sample data: {str(e)}")
        import traceback
        traceback.print_exc()