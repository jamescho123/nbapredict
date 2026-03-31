# User Authentication System - Complete Guide

## ✅ System Setup Complete!

Your NBA prediction website now has a full user authentication system with:
- User registration & login
- Secure password hashing
- Session management
- User profiles
- Prediction tracking

## 🗄️ Database Tables Created

```
✓ NBA.Users           - User accounts
✓ NBA.UserPreferences - User settings (favorite team, theme, etc.)
✓ NBA.UserSessions    - Active login sessions
✓ NBA.UserPredictions - Track user predictions & accuracy
```

## 🚀 How to Use

### 1. Start Your Streamlit App

```bash
streamlit run app.py
```

### 2. New Pages Available

- **Login Page** - `/Login` - User login and registration
- **Profile Page** - `/Profile` - User profile, stats, and prediction history

### 3. Create Your First Account

1. Navigate to the Login page
2. Click the "Register" tab
3. Fill in:
   - Username (min 3 characters)
   - Email
   - Password (min 8 chars, must include uppercase, lowercase, number)
   - Confirm password
4. Click "Register"
5. Login with your new account!

## 🔐 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Passwords are hashed with SHA-256 and unique salt per user

### Session Management
- Secure session tokens (64 bytes, URL-safe)
- Sessions expire after 7 days
- Automatic session validation

### Database Security
- Passwords never stored in plain text
- Unique salt per user
- Session tokens are random and unique

## 📊 User Features

### Profile Page Features
1. **Account Information**
   - View username, email, user ID
   - Set favorite team
   - Choose theme (light/dark)
   - Email notification preferences

2. **Statistics Dashboard**
   - Total predictions made
   - Correct predictions
   - Accuracy percentage
   - Average confidence
   - Performance rating

3. **Prediction History**
   - View all past predictions
   - See actual results
   - Track accuracy over time

## 💻 How to Add Auth to Existing Pages

### Example: Protect Hybrid Prediction Page

```python
# At the top of pages/Hybrid_Predict.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_system import check_authentication, save_user_prediction

# Check if user is logged in
if not check_authentication():
    st.warning("Please login to make predictions")
    st.info("Visit the Login page to create an account or sign in")
    st.stop()

# User is authenticated - show their username
st.success(f"Welcome, {st.session_state.user_data['username']}!")

# ... rest of your prediction code ...

# When user makes a prediction, save it:
if prediction_made:
    save_user_prediction(
        user_id=st.session_state.user_data['user_id'],
        game_date=game_date,
        home_team=home_team,
        away_team=away_team,
        predicted_winner=predicted_winner,
        confidence=confidence
    )
```

### Example: Optional Auth (Feature Available to All, Enhanced for Logged-in Users)

```python
from auth_system import check_authentication

# Check authentication (optional)
is_authenticated = check_authentication()

if is_authenticated:
    st.success(f"Welcome back, {st.session_state.user_data['username']}!")
    st.info("Your predictions will be saved to your profile")
else:
    st.info("Login to save your predictions and track accuracy")

# ... rest of your code works for everyone ...
```

## 📝 Available Functions

### Authentication Functions

```python
from auth_system import (
    # Core auth
    login_user,          # Login with username/email + password
    register_user,       # Create new account
    logout_user,         # Logout
    check_authentication # Check if user is logged in
    
    # Session management
    verify_session,      # Verify session token is valid
    
    # User data
    get_user_preferences,   # Get user preferences
    update_user_preferences, # Update preferences
    
    # Predictions
    save_user_prediction,      # Save prediction to history
    get_user_prediction_history, # Get user's predictions
    get_user_stats              # Get accuracy stats
)
```

### Usage Examples

#### Check if User is Logged In

```python
from auth_system import check_authentication

if check_authentication():
    # User is logged in
    username = st.session_state.user_data['username']
    user_id = st.session_state.user_data['user_id']
    st.write(f"Hello, {username}!")
else:
    # User is not logged in
    st.warning("Please login")
```

#### Save User Prediction

```python
from auth_system import save_user_prediction

# After making a prediction
if check_authentication():
    save_user_prediction(
        user_id=st.session_state.user_data['user_id'],
        game_date='2025-11-05',
        home_team='Boston Celtics',
        away_team='New York Knicks',
        predicted_winner='Boston Celtics',
        confidence=75.5
    )
```

#### Get User Stats

```python
from auth_system import get_user_stats

if check_authentication():
    stats = get_user_stats(st.session_state.user_data['user_id'])
    
    st.metric("Your Accuracy", f"{stats['accuracy']:.1f}%")
    st.metric("Total Predictions", stats['total_predictions'])
```

## 🎯 Integration Examples

### Add Login Reminder to Sidebar

```python
# In your main app or any page
import streamlit as st
from auth_system import check_authentication

# Sidebar
with st.sidebar:
    if check_authentication():
        st.success(f"Logged in as: {st.session_state.user_data['username']}")
        
        # Link to profile
        if st.button("My Profile"):
            st.switch_page("pages/Profile.py")
    else:
        st.warning("Not logged in")
        if st.button("Login"):
            st.switch_page("pages/Login_Supabase.py")
```

### Protect Admin Features

```python
from auth_system import check_authentication

# Admin-only feature
if check_authentication():
    user_id = st.session_state.user_data['user_id']
    
    # Check if admin (you can add an IsAdmin column to Users table)
    if user_id == 1:  # First user is admin
        st.header("Admin Panel")
        # ... admin features ...
    else:
        st.warning("Admin access required")
else:
    st.warning("Please login")
```

## 🔧 Database Schema

### Users Table
```sql
"UserID" SERIAL PRIMARY KEY
"Username" VARCHAR(50) UNIQUE NOT NULL
"Email" VARCHAR(100) UNIQUE NOT NULL
"PasswordHash" VARCHAR(256) NOT NULL
"Salt" VARCHAR(64) NOT NULL
"CreatedAt" TIMESTAMP
"LastLogin" TIMESTAMP
"IsActive" BOOLEAN
```

### UserPreferences Table
```sql
"PreferenceID" SERIAL PRIMARY KEY
"UserID" INTEGER REFERENCES Users
"FavoriteTeam" VARCHAR(100)
"Theme" VARCHAR(20)
"EmailNotifications" BOOLEAN
"UpdatedAt" TIMESTAMP
```

### UserSessions Table
```sql
"SessionID" SERIAL PRIMARY KEY
"UserID" INTEGER REFERENCES Users
"SessionToken" VARCHAR(256) UNIQUE
"CreatedAt" TIMESTAMP
"ExpiresAt" TIMESTAMP
"IPAddress" VARCHAR(45)
"UserAgent" TEXT
```

### UserPredictions Table
```sql
"PredictionID" SERIAL PRIMARY KEY
"UserID" INTEGER REFERENCES Users
"GameDate" DATE
"HomeTeam" VARCHAR(100)
"AwayTeam" VARCHAR(100)
"PredictedWinner" VARCHAR(100)
"Confidence" FLOAT
"ActualWinner" VARCHAR(100)
"IsCorrect" BOOLEAN
"CreatedAt" TIMESTAMP
```

## 🔄 Session Flow

1. **User registers/logs in** → Session token created
2. **Session stored in** `st.session_state` and database
3. **On each page load** → `check_authentication()` verifies session
4. **Session expires** → User must login again
5. **User logs out** → Session deleted from database

## ⚙️ Configuration

### Change Session Duration

Edit `auth_system.py`, line ~260:
```python
# Default: 7 days
expires_at = datetime.now() + timedelta(days=7)

# Change to 30 days:
expires_at = datetime.now() + timedelta(days=30)

# Change to 12 hours:
expires_at = datetime.now() + timedelta(hours=12)
```

### Customize Password Requirements

Edit `auth_system.py`, function `validate_password()`:
```python
def validate_password(password):
    # Customize requirements here
    if len(password) < 12:  # Change minimum length
        return False, "Password must be at least 12 characters"
    
    # Add special character requirement
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Password must contain special character"
    
    # ... etc
```

## 🐛 Troubleshooting

### "Please login to access this feature"
- User is not logged in or session expired
- Navigate to Login page and sign in

### "Invalid username or password"
- Check credentials are correct
- Usernames and emails are case-sensitive

### "Username already exists"
- Choose a different username
- Or login if you already have an account

### Session keeps expiring
- Check session duration in `auth_system.py`
- Clear browser cookies and login again

## 📱 Mobile Support

The authentication system works on mobile devices:
- Responsive login/register forms
- Touch-friendly buttons
- Mobile-optimized profile page

## 🎨 Customization

### Change Theme Colors

Edit the pages to match your brand:
```python
st.set_page_config(
    page_title="Login - Your Brand",
    page_icon="🎯",  # Your icon
    layout="wide"
)
```

### Add Social Login (Future Enhancement)

You can extend the system to support:
- Google OAuth
- GitHub login
- Twitter/X authentication

## 📊 Analytics

Track user engagement:
```python
from auth_system import get_user_stats

# Get all users' stats
conn = connect_to_database()
cursor = conn.cursor()

cursor.execute('''
    SELECT 
        COUNT(*) as total_users,
        COUNT(CASE WHEN "LastLogin" > NOW() - INTERVAL '7 days' THEN 1 END) as active_users
    FROM "NBA"."Users"
''')

total, active = cursor.fetchone()
st.metric("Total Users", total)
st.metric("Active (7 days)", active)
```

## ✅ Next Steps

1. **Test the system** - Create an account and test login
2. **Add auth to pages** - Protect prediction features
3. **Customize appearance** - Match your website theme
4. **Add features** - User avatars, password reset, etc.

## 🎯 Summary

You now have a **complete, secure user authentication system** for your NBA prediction website!

**Features:**
- ✅ User registration & login
- ✅ Secure password hashing
- ✅ Session management
- ✅ User profiles
- ✅ Prediction tracking
- ✅ Statistics dashboard
- ✅ Easy integration with existing pages

**Ready to use!** 🚀












