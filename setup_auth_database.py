"""
Setup Authentication Database Tables

Run this script once to create all necessary tables for user authentication.
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def create_user_tables():
    """Create tables for user authentication"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        print("Creating Users table...")
        # Users table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."Users" (
                "UserID" SERIAL PRIMARY KEY,
                "Username" VARCHAR(50) UNIQUE NOT NULL,
                "Email" VARCHAR(100) UNIQUE NOT NULL,
                "PasswordHash" VARCHAR(256) NOT NULL,
                "Salt" VARCHAR(64) NOT NULL,
                "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "LastLogin" TIMESTAMP,
                "IsActive" BOOLEAN DEFAULT TRUE
            )
        ''')
        
        print("Creating UserPreferences table...")
        # User preferences table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."UserPreferences" (
                "PreferenceID" SERIAL PRIMARY KEY,
                "UserID" INTEGER REFERENCES "{DB_SCHEMA}"."Users"("UserID"),
                "FavoriteTeam" VARCHAR(100),
                "Theme" VARCHAR(20) DEFAULT 'light',
                "EmailNotifications" BOOLEAN DEFAULT FALSE,
                "UpdatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("Creating UserSessions table...")
        # User sessions table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."UserSessions" (
                "SessionID" SERIAL PRIMARY KEY,
                "UserID" INTEGER REFERENCES "{DB_SCHEMA}"."Users"("UserID"),
                "SessionToken" VARCHAR(256) UNIQUE NOT NULL,
                "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "ExpiresAt" TIMESTAMP NOT NULL,
                "IPAddress" VARCHAR(45),
                "UserAgent" TEXT
            )
        ''')
        
        print("Creating UserPredictions table...")
        # Prediction history table (track user predictions)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."UserPredictions" (
                "PredictionID" SERIAL PRIMARY KEY,
                "UserID" INTEGER REFERENCES "{DB_SCHEMA}"."Users"("UserID"),
                "GameDate" DATE NOT NULL,
                "HomeTeam" VARCHAR(100) NOT NULL,
                "AwayTeam" VARCHAR(100) NOT NULL,
                "PredictedWinner" VARCHAR(100) NOT NULL,
                "Confidence" FLOAT,
                "ActualWinner" VARCHAR(100),
                "IsCorrect" BOOLEAN,
                "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("Creating indexes...")
        # Create indexes for better performance
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_users_username ON "{DB_SCHEMA}"."Users"("Username")')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_users_email ON "{DB_SCHEMA}"."Users"("Email")')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_sessions_token ON "{DB_SCHEMA}"."UserSessions"("SessionToken")')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_predictions_user ON "{DB_SCHEMA}"."UserPredictions"("UserID")')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\nAll authentication tables created successfully!")
        print("\nTables created:")
        print("  - Users")
        print("  - UserPreferences")
        print("  - UserSessions")
        print("  - UserPredictions")
        
        return True
        
    except Exception as e:
        print(f"Error creating user tables: {e}")
        conn.close()
        return False

if __name__ == "__main__":
    print("="*60)
    print("NBA Prediction Website - Authentication Setup")
    print("="*60)
    print()
    
    result = create_user_tables()
    
    if result:
        print("\n" + "="*60)
        print("Setup Complete!")
        print("="*60)
        print("\nYou can now:")
        print("1. Run your Streamlit app: streamlit run app.py")
        print("2. Navigate to the Login page")
        print("3. Create a new account")
    else:
        print("\n" + "="*60)
        print("Setup Failed!")
        print("="*60)
















