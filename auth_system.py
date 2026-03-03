"""
User Authentication System for NBA Prediction Website

Features:
- User registration
- Login/logout
- Password hashing (secure)
- Session management
- User preferences
"""

import psycopg2
import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
import re

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
        st.error(f"Database connection failed: {e}")
        return None

def create_user_tables():
    """Create tables for user authentication"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
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
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating user tables: {e}")
        conn.close()
        return False

def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Combine password and salt
    pwd_salt = f"{password}{salt}".encode('utf-8')
    
    # Hash using SHA-256
    pwd_hash = hashlib.sha256(pwd_salt).hexdigest()
    
    return pwd_hash, salt

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def register_user(username, email, password):
    """Register a new user"""
    conn = connect_to_database()
    if not conn:
        return False, "Database connection failed"
    
    # Validate inputs
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    cursor = conn.cursor()
    
    try:
        # Check if username exists
        cursor.execute(
            f'SELECT "UserID" FROM "{DB_SCHEMA}"."Users" WHERE "Username" = %s',
            (username,)
        )
        if cursor.fetchone():
            return False, "Username already exists"
        
        # Check if email exists
        cursor.execute(
            f'SELECT "UserID" FROM "{DB_SCHEMA}"."Users" WHERE "Email" = %s',
            (email,)
        )
        if cursor.fetchone():
            return False, "Email already registered"
        
        # Hash password
        pwd_hash, salt = hash_password(password)
        
        # Insert new user
        cursor.execute(f'''
            INSERT INTO "{DB_SCHEMA}"."Users" 
            ("Username", "Email", "PasswordHash", "Salt")
            VALUES (%s, %s, %s, %s)
            RETURNING "UserID"
        ''', (username, email, pwd_hash, salt))
        
        user_id = cursor.fetchone()[0]
        
        # Create default preferences
        cursor.execute(f'''
            INSERT INTO "{DB_SCHEMA}"."UserPreferences" 
            ("UserID")
            VALUES (%s)
        ''', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "Registration successful!"
        
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}"

def login_user(username, password):
    """Authenticate user login"""
    conn = connect_to_database()
    if not conn:
        return False, None, "Database connection failed"
    
    cursor = conn.cursor()
    
    try:
        # Get user data
        cursor.execute(f'''
            SELECT "UserID", "Username", "Email", "PasswordHash", "Salt", "IsActive"
            FROM "{DB_SCHEMA}"."Users"
            WHERE "Username" = %s OR "Email" = %s
        ''', (username, username))
        
        user = cursor.fetchone()
        
        if not user:
            return False, None, "Invalid username or password"
        
        user_id, username, email, stored_hash, salt, is_active = user
        
        if not is_active:
            return False, None, "Account is disabled"
        
        # Verify password
        pwd_hash, _ = hash_password(password, salt)
        
        if pwd_hash != stored_hash:
            return False, None, "Invalid username or password"
        
        # Update last login
        cursor.execute(f'''
            UPDATE "{DB_SCHEMA}"."Users"
            SET "LastLogin" = CURRENT_TIMESTAMP
            WHERE "UserID" = %s
        ''', (user_id,))
        
        # Create session token
        session_token = secrets.token_urlsafe(64)
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute(f'''
            INSERT INTO "{DB_SCHEMA}"."UserSessions"
            ("UserID", "SessionToken", "ExpiresAt")
            VALUES (%s, %s, %s)
            RETURNING "SessionID"
        ''', (user_id, session_token, expires_at))
        
        session_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        user_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'session_token': session_token,
            'session_id': session_id
        }
        
        return True, user_data, "Login successful!"
        
    except Exception as e:
        conn.close()
        return False, None, f"Login failed: {str(e)}"

def logout_user(session_token):
    """Logout user by invalidating session"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            DELETE FROM "{DB_SCHEMA}"."UserSessions"
            WHERE "SessionToken" = %s
        ''', (session_token,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        conn.close()
        return False

def verify_session(session_token):
    """Verify if session token is valid"""
    conn = connect_to_database()
    if not conn:
        return False, None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            SELECT u."UserID", u."Username", u."Email", s."ExpiresAt"
            FROM "{DB_SCHEMA}"."Users" u
            JOIN "{DB_SCHEMA}"."UserSessions" s ON u."UserID" = s."UserID"
            WHERE s."SessionToken" = %s AND s."ExpiresAt" > CURRENT_TIMESTAMP
        ''', (session_token,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            user_data = {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'session_token': session_token
            }
            return True, user_data
        
        return False, None
        
    except Exception as e:
        conn.close()
        return False, None

def get_user_preferences(user_id):
    """Get user preferences"""
    conn = connect_to_database()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            SELECT "FavoriteTeam", "Theme", "EmailNotifications"
            FROM "{DB_SCHEMA}"."UserPreferences"
            WHERE "UserID" = %s
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return {
                'favorite_team': result[0],
                'theme': result[1],
                'email_notifications': result[2]
            }
        
        return None
        
    except Exception as e:
        conn.close()
        return None

def update_user_preferences(user_id, favorite_team=None, theme=None, email_notifications=None):
    """Update user preferences"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if favorite_team is not None:
            updates.append('"FavoriteTeam" = %s')
            params.append(favorite_team)
        
        if theme is not None:
            updates.append('"Theme" = %s')
            params.append(theme)
        
        if email_notifications is not None:
            updates.append('"EmailNotifications" = %s')
            params.append(email_notifications)
        
        if not updates:
            return True
        
        params.append(user_id)
        
        query = f'''
            UPDATE "{DB_SCHEMA}"."UserPreferences"
            SET {", ".join(updates)}, "UpdatedAt" = CURRENT_TIMESTAMP
            WHERE "UserID" = %s
        '''
        
        cursor.execute(query, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        conn.close()
        return False

def save_user_prediction(user_id, game_date, home_team, away_team, 
                         predicted_winner, confidence):
    """Save user's prediction"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            INSERT INTO "{DB_SCHEMA}"."UserPredictions"
            ("UserID", "GameDate", "HomeTeam", "AwayTeam", "PredictedWinner", "Confidence")
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, game_date, home_team, away_team, predicted_winner, confidence))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        conn.close()
        return False

def get_user_prediction_history(user_id, limit=20):
    """Get user's prediction history"""
    conn = connect_to_database()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            SELECT "GameDate", "HomeTeam", "AwayTeam", "PredictedWinner", 
                   "Confidence", "ActualWinner", "IsCorrect", "CreatedAt"
            FROM "{DB_SCHEMA}"."UserPredictions"
            WHERE "UserID" = %s
            ORDER BY "CreatedAt" DESC
            LIMIT %s
        ''', (user_id, limit))
        
        predictions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [{
            'game_date': p[0],
            'home_team': p[1],
            'away_team': p[2],
            'predicted_winner': p[3],
            'confidence': p[4],
            'actual_winner': p[5],
            'is_correct': p[6],
            'created_at': p[7]
        } for p in predictions]
        
    except Exception as e:
        conn.close()
        return []

def get_user_stats(user_id):
    """Get user prediction statistics"""
    conn = connect_to_database()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            SELECT 
                COUNT(*) as total_predictions,
                SUM(CASE WHEN "IsCorrect" = TRUE THEN 1 ELSE 0 END) as correct_predictions,
                AVG("Confidence") as avg_confidence
            FROM "{DB_SCHEMA}"."UserPredictions"
            WHERE "UserID" = %s AND "IsCorrect" IS NOT NULL
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result[0] > 0:
            total = result[0]
            correct = result[1] or 0
            accuracy = (correct / total * 100) if total > 0 else 0
            
            return {
                'total_predictions': total,
                'correct_predictions': correct,
                'accuracy': accuracy,
                'avg_confidence': result[2] or 0
            }
        
        return {
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy': 0,
            'avg_confidence': 0
        }
        
    except Exception as e:
        conn.close()
        return None

# Initialize session state for authentication
def init_auth_session():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

def check_authentication():
    """Check if user is authenticated"""
    init_auth_session()
    
    if st.session_state.authenticated and st.session_state.session_token:
        # Verify session is still valid
        is_valid, user_data = verify_session(st.session_state.session_token)
        
        if is_valid:
            st.session_state.user_data = user_data
            return True
        else:
            # Session expired
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.session_state.session_token = None
            return False
    
    return False

def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            st.warning("Please login to access this feature")
            return None
        return func(*args, **kwargs)
    return wrapper
















