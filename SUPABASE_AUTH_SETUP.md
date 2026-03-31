# Supabase Authentication Setup Guide

## Overview

This guide will help you set up Supabase authentication for your NBA Predict application.

## Prerequisites

1. Supabase project: `mxnpfsiyaqqwdcokukij`
2. Python environment with required packages

## Step 1: Install Dependencies

```bash
pip install supabase>=2.0.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Step 2: Get Supabase Anon Key

1. Go to your Supabase Dashboard:
   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api

2. Copy the **anon/public** key (NOT the service_role key)
   - The anon key is safe to use in client-side code
   - The service_role key has admin access and should NEVER be exposed

3. Set it as an environment variable:

**Windows PowerShell:**
```powershell
$env:SUPABASE_ANON_KEY="your_anon_key_here"
```

**Windows CMD:**
```cmd
set SUPABASE_ANON_KEY=your_anon_key_here
```

**Linux/Mac:**
```bash
export SUPABASE_ANON_KEY="your_anon_key_here"
```

**Or create a `.env` file:**
```
SUPABASE_URL=https://mxnpfsiyaqqwdcokukij.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

## Step 3: Configure Supabase Auth Settings

1. Go to Authentication settings:
   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/auth/providers

2. Enable Email provider (should be enabled by default)

3. Configure email templates (optional):
   - Go to: Authentication → Email Templates
   - Customize welcome email, password reset email, etc.

4. Set up email redirect URLs (if needed):
   - Go to: Authentication → URL Configuration
   - Add your app URL to allowed redirect URLs

## Step 4: Use Supabase Auth in Your App

### Option A: Use the New Supabase Login Page

Update your `Home.py` or main app to include the Supabase login page:

```python
from pages import Login_Supabase

# Add to navigation
if page == "Login":
    Login_Supabase.app()
```

### Option B: Update Existing Login Page

Replace imports in `pages/Login.py`:

```python
# Old:
from auth_system import login_user, register_user

# New:
from nba_supabase_auth import login_user, register_user
```

## Step 5: Test Authentication

1. Start your Streamlit app:
```bash
streamlit run Home.py
```

2. Navigate to the Login page

3. Register a new account:
   - Enter email and password
   - Check your email for verification link
   - Verify your email
   - Login with your credentials

## Features

### What Supabase Auth Provides

✅ **Secure Authentication**
- Industry-standard password hashing (bcrypt)
- JWT-based sessions
- Automatic token refresh

✅ **Email Verification**
- Automatic email verification
- Password reset emails
- Welcome emails

✅ **User Management**
- User profiles with metadata
- Session management
- Account recovery

✅ **Security Features**
- Rate limiting
- Password strength requirements
- Secure token storage

## Migration from Custom Auth

If you have existing users in your custom `NBA.Users` table, you have two options:

### Option 1: Keep Both Systems
- Use Supabase Auth for new users
- Keep custom auth for existing users
- Migrate users gradually

### Option 2: Migrate All Users
1. Export users from `NBA.Users` table
2. Create accounts in Supabase Auth (requires admin access)
3. Update your app to use only Supabase Auth

## Troubleshooting

### "Supabase anon key not configured"
- Make sure you've set the `SUPABASE_ANON_KEY` environment variable
- Restart your Streamlit app after setting the variable

### "Invalid login credentials"
- Check that email is verified (if email verification is enabled)
- Verify password is correct
- Check Supabase dashboard for user status

### "Email already registered"
- User exists in Supabase Auth
- Use password reset if you forgot your password
- Or login with existing credentials

### Email Not Sending
- Check Supabase project settings
- Verify email provider is configured
- Check spam folder
- For development, Supabase provides test emails

## Environment Variables Summary

```bash
# Required
SUPABASE_ANON_KEY=your_anon_key_here

# Optional (defaults provided)
SUPABASE_URL=https://mxnpfsiyaqqwdcokukij.supabase.co
```

## Security Notes

⚠️ **Important:**
- Never commit your `SUPABASE_ANON_KEY` to git
- Use environment variables or `.env` file (add to `.gitignore`)
- The anon key is safe for client-side use
- Never use the service_role key in your app

## Next Steps

1. ✅ Install supabase package
2. ✅ Get anon key from dashboard
3. ✅ Set environment variable
4. ✅ Test registration and login
5. ✅ Integrate with your app pages

## Resources

- Supabase Dashboard: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij
- Supabase Auth Docs: https://supabase.com/docs/guides/auth
- API Settings: https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api

