Database structure as following

## Local PostgreSQL
PostgreSQL server: localhost
Database: James
Schema: NBA
Username: postgres
Password: jcjc1749

## Supabase (Cloud)
Account: jamescho@jumbosoft.com
Organization: jamescho@jumbosoft.com's Org
Project name: NBA_Predict
Project ID: mxnpfsiyaqqwdcokukij
URL: https://mxnpfsiyaqqwdcokukij.supabase.co
Database Host: db.mxnpfsiyaqqwdcokukij.supabase.co
Database: postgres
Schema: NBA
Username: postgres
Password: VXUXqY9Uofg9ujoo
Port: 5432 (direct) / 6543 (pooler)

## Switch between Local and Supabase
Use environment variable: `USE_SUPABASE=true` or `USE_SUPABASE=false`

Example:
```bash
# Use local database
python your_script.py

# Use Supabase
$env:USE_SUPABASE="true"
python your_script.py
```

## Sample Table Structure
CREATE TABLE IF NOT EXISTS "NBA"."VectorNews"
(
    "NewsID" integer NOT NULL,
    "NewsVector" vector NOT NULL,
    CONSTRAINT "VectorNews_pkey" PRIMARY KEY ("NewsID")
)

## Migration
See SUPABASE_SETUP.md for migration instructions.