# Get Supabase Anon Key

## Quick Steps

1. **Go to Supabase Dashboard:**
   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api

2. **Copy the "anon" or "public" key** (the long string under "Project API keys")
   - ⚠️ **DO NOT** use the "service_role" key (it has admin access)
   - ✅ Use the "anon" or "public" key (safe for client-side use)

3. **Set it as environment variable:**

   **Windows PowerShell:**
   ```powershell
   $env:SUPABASE_ANON_KEY="your_anon_key_here"
   ```

   **Windows CMD:**
   ```cmd
   set SUPABASE_ANON_KEY=your_anon_key_here
   ```

   **To make it permanent (PowerShell):**
   ```powershell
   [System.Environment]::SetEnvironmentVariable('SUPABASE_ANON_KEY', 'your_anon_key_here', 'User')
   ```

4. **Or create `.env` file in project root:**
   ```
   SUPABASE_URL=https://mxnpfsiyaqqwdcokukij.supabase.co
   SUPABASE_ANON_KEY=your_anon_key_here
   ```

5. **Restart your Streamlit app** after setting the environment variable

## Verify Setup

Run:
```bash
python setup_supabase_auth.py
```

It will check if the key is set and if the supabase package is installed.










