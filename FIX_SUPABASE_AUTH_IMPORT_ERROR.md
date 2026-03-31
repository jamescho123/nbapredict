# Fix: ModuleNotFoundError: No module named 'supabase_auth.errors'

## Problem
You're getting this error because Python has cached the old module name `supabase_auth` and is trying to import from it.

## Solution

### Step 1: Delete Python Cache Files

**Option A: Manual Deletion**
1. Close your Streamlit app (if running)
2. Delete all `__pycache__` folders in your project:
   - `__pycache__/`
   - `pages/__pycache__/`
   - Any other `__pycache__` folders
3. Delete any `.pyc` files if you see them

**Option B: Use the Script**
```bash
python clear_cache.py
```

**Option C: PowerShell Command**
```powershell
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
```

### Step 2: Verify the Module Name

Make sure you're importing from `nba_supabase_auth`, NOT `supabase_auth`:

```python
# ✅ CORRECT
from nba_supabase_auth import login_user, register_user

# ❌ WRONG
from supabase_auth import login_user, register_user
```

### Step 3: Restart Everything

1. **Close all Python processes:**
   - Close Streamlit app
   - Close any Python terminals
   - Close your IDE/editor

2. **Restart your IDE/editor**

3. **Start fresh:**
   ```bash
   streamlit run pages/Login_Supabase.py
   ```

### Step 4: If Still Not Working

Check if there's a directory or file named `supabase_auth`:
```bash
# Check for directories
dir supabase_auth

# Check for files
dir supabase_auth.*
```

If you find any, delete them (the module is now `nba_supabase_auth.py`).

### Step 5: Verify Installation

Make sure supabase package is installed:
```bash
pip install supabase>=2.0.0
```

## Quick Fix Command

Run this in PowerShell from your project directory:

```powershell
# Clear cache
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force

# Verify module exists
Test-Path nba_supabase_auth.py

# Test import (if streamlit is installed)
python -c "from nba_supabase_auth import login_user; print('Import successful!')"
```

## Why This Happened

The module was originally named `supabase_auth.py`, which conflicted with the `supabase` package. It was renamed to `nba_supabase_auth.py`, but Python cached the old name. Clearing the cache fixes this.

## Still Having Issues?

1. Make sure `nba_supabase_auth.py` exists in your project root
2. Check that `pages/Login_Supabase.py` imports from `nba_supabase_auth`
3. Restart your computer if cache clearing doesn't work
4. Try running in a fresh Python environment











