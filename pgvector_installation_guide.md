# pgvector Installation Guide for Windows

This guide will help you install the pgvector extension for PostgreSQL on Windows.

## Prerequisites

- PostgreSQL 17 installed on your system
- Administrator privileges on your computer

## Installation Methods

There are three ways to install pgvector:

1. **Using pre-compiled binaries (Recommended)**
2. **Compiling from source**
3. **Manual file copying**

## Method 1: Using Pre-compiled Binaries (Recommended)

### Step 1: Download and Install

1. Run the `copy_pgvector_dll.bat` script as administrator:
   - Right-click on `copy_pgvector_dll.bat` and select "Run as administrator"
   - Enter your PostgreSQL installation path when prompted (e.g., `C:\Program Files\PostgreSQL\17`)

### Step 2: Restart PostgreSQL Service

1. Run the `restart_postgres.bat` script as administrator:
   - Right-click on `restart_postgres.bat` and select "Run as administrator"

### Step 3: Create the Extension

1. Connect to your database using psql or pgAdmin
2. Run the following SQL command:
   ```sql
   CREATE EXTENSION vector;
   ```

### Step 4: Verify Installation

1. Run the `check_pgvector.py` script to verify that pgvector is installed correctly:
   ```
   python check_pgvector.py
   ```

## Method 2: Compiling from Source

This method requires Visual Studio with C++ build tools installed.

### Step 1: Install Visual Studio Build Tools

1. Download and install Visual Studio Build Tools from:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. During installation, select "Desktop development with C++"

### Step 2: Compile and Install

1. Run the `compile_pgvector.bat` script as administrator:
   - Right-click on `compile_pgvector.bat` and select "Run as administrator"
   - Enter your PostgreSQL installation path when prompted (e.g., `C:\Program Files\PostgreSQL\17`)

### Step 3: Restart PostgreSQL Service

1. Run the `restart_postgres.bat` script as administrator:
   - Right-click on `restart_postgres.bat` and select "Run as administrator"

### Step 4: Create the Extension

1. Connect to your database using psql or pgAdmin
2. Run the following SQL command:
   ```sql
   CREATE EXTENSION vector;
   ```

### Step 5: Verify Installation

1. Run the `check_pgvector.py` script to verify that pgvector is installed correctly:
   ```
   python check_pgvector.py
   ```

## Method 3: Manual File Copying

If the automated methods don't work, you can manually copy the files.

### Step 1: Download pgvector

1. Download the pre-compiled binaries from:
   https://github.com/pgvector/pgvector/releases/download/v0.8.0/vector-0.8.0-pg17-windows-x86_64.zip

### Step 2: Extract and Copy Files

1. Extract the ZIP file
2. Copy `vector.dll` to `C:\Program Files\PostgreSQL\17\lib`
3. Copy `vector.control` and all SQL files to `C:\Program Files\PostgreSQL\17\share\extension`

### Step 3: Restart PostgreSQL Service

1. Open Services (services.msc)
2. Find the PostgreSQL service
3. Right-click and select "Restart"

### Step 4: Create the Extension

1. Connect to your database using psql or pgAdmin
2. Run the following SQL command:
   ```sql
   CREATE EXTENSION vector;
   ```

### Step 5: Verify Installation

1. Run the `check_pgvector.py` script to verify that pgvector is installed correctly:
   ```
   python check_pgvector.py
   ```

## Troubleshooting

### Error: "extension vector is not available"

This error occurs when PostgreSQL cannot find the pgvector extension files. Check:

1. The `vector.control` file exists in `C:\Program Files\PostgreSQL\17\share\extension`
2. The `vector.sql` file exists in `C:\Program Files\PostgreSQL\17\share\extension`
3. The `vector.dll` file exists in `C:\Program Files\PostgreSQL\17\lib`

### Error: "扩展 vector 没有安装脚本，也没有版本0.8.0的更新路径"

This error occurs when PostgreSQL can find the control file but not the module file. Check:

1. The `vector.dll` file exists in `C:\Program Files\PostgreSQL\17\lib`
2. You have restarted the PostgreSQL service after copying the files

### Error: "could not access file "$libdir/vector": No such file or directory"

This error occurs when PostgreSQL can find the SQL files but not the module file. Check:

1. The `vector.dll` file exists in `C:\Program Files\PostgreSQL\17\lib`
2. You have restarted the PostgreSQL service after copying the files

## Next Steps After Installation

Once pgvector is installed, you can:

1. Create tables with vector columns:
   ```sql
   CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(1024));
   ```

2. Insert vectors:
   ```sql
   INSERT INTO items (embedding) VALUES ('[1,2,3]');
   ```

3. Create indexes for faster similarity searches:
   ```sql
   -- HNSW index (faster search, slower inserts)
   CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);
   
   -- IVF index (balance between search and insert speed)
   CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
   ```

4. Perform similarity searches:
   ```sql
   -- Find similar items
   SELECT * FROM items ORDER BY embedding <=> '[3,1,2]' LIMIT 5;
   ```

## Using pgvector with Python

To use pgvector with Python:

1. Install the psycopg2 module:
   ```
   pip install psycopg2
   ```

2. Register the vector type with psycopg2:
   ```python
   import psycopg2
   import psycopg2.extras
   import numpy as np

   # Register the vector type
   psycopg2.extras.register_vector()

   # Connect to the database
   conn = psycopg2.connect(
       host='localhost',
       dbname='your_database',
       user='your_username',
       password='your_password'
   )
   cur = conn.cursor()

   # Create a vector
   embedding = np.random.rand(1024).tolist()

   # Insert the vector
   cur.execute("INSERT INTO items (embedding) VALUES (%s)", (embedding,))
   conn.commit()

   # Search for similar vectors
   cur.execute("SELECT * FROM items ORDER BY embedding <=> %s LIMIT 5", (embedding,))
   results = cur.fetchall()
   ``` 