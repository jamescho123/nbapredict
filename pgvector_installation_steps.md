# pgvector Installation Guide for Windows

This guide provides step-by-step instructions for installing the pgvector extension on Windows.

## Option 1: Install Pre-compiled Binary (Recommended)

This is the easiest method and doesn't require Visual Studio Build Tools.

1. **Run the download_pgvector.cmd script as Administrator**
   - Right-click on `download_pgvector.cmd` and select "Run as administrator"
   - Enter your PostgreSQL installation path when prompted

2. **Restart PostgreSQL Service**
   - Run `check_postgres_service.cmd` to find your PostgreSQL service name
   - Run `restart_postgres.cmd` as Administrator
   - Enter your PostgreSQL service name when prompted

3. **Create the pgvector Extension**
   - Run `create_extension.cmd`
   - Enter your PostgreSQL path, database name, username, and password when prompted

4. **Verify Installation**
   - The script will verify if the extension was installed successfully

## Option 2: Compile from Source (Requires Visual Studio Build Tools)

Use this method if the pre-compiled binary doesn't work for your PostgreSQL version.

1. **Install Visual Studio Build Tools**
   - Run `install_vs_build_tools.cmd`
   - In the installer, select "Desktop development with C++"
   - Complete the installation and restart your computer

2. **Set up Visual Studio Environment**
   - Run `setup_vs_env.cmd` as Administrator

3. **Compile and Install pgvector**
   - In the same Command Prompt window, run `compile_pgvector.cmd`
   - Enter your PostgreSQL installation path when prompted

4. **Restart PostgreSQL Service**
   - Run `check_postgres_service.cmd` to find your PostgreSQL service name
   - Run `restart_postgres.cmd` as Administrator
   - Enter your PostgreSQL service name when prompted

5. **Create the pgvector Extension**
   - Run `create_extension.cmd`
   - Enter your PostgreSQL path, database name, username, and password when prompted

6. **Verify Installation**
   - The script will verify if the extension was installed successfully

## Troubleshooting

### Common Issues:

1. **"Error: This script requires administrator privileges"**
   - Right-click on the script and select "Run as administrator"

2. **"Error: Failed to copy vector.dll"**
   - Make sure you're running the script as Administrator
   - Check if your PostgreSQL path is correct
   - Check if PostgreSQL service is running

3. **"Error: Failed to create pgvector extension"**
   - Make sure PostgreSQL service is restarted after copying the files
   - Check if vector.dll is in the PostgreSQL lib directory
   - Check if vector.control and vector.sql are in the PostgreSQL share\extension directory

4. **"此时不应有 \Microsoft"**
   - This error occurs when there are issues with paths containing spaces
   - Make sure all paths are properly quoted in the scripts

5. **"No PostgreSQL services found"**
   - Use `check_postgres_service.cmd` to find your PostgreSQL service name
   - Look for services in Windows Services (services.msc) with names containing "postgres" or "postgresql"

### Manual Installation:

If the scripts don't work, you can manually:

1. Download the pre-compiled binary from https://github.com/pgvector/pgvector/releases
2. Extract and copy vector.dll to your PostgreSQL lib directory
3. Copy vector.control and vector*.sql files to your PostgreSQL share\extension directory
4. Restart PostgreSQL service
5. Connect to your database and run: `CREATE EXTENSION vector;` 