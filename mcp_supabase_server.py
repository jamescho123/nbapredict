import asyncio
import json
import psycopg2
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("nba-database-server")

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

SUPABASE_CONFIG = {
    'host': 'aws-1-ap-southeast-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.mxnpfsiyaqqwdcokukij',
    'password': 'Jcjc1749!!!!',
    'port': 5432
}

DB_SCHEMA = 'NBA'

def get_db_connection(use_supabase=True):
    config = SUPABASE_CONFIG if use_supabase else LOCAL_CONFIG
    return psycopg2.connect(**config)

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="local://tables",
            name="Local Database Tables",
            description="List all tables in local NBA schema",
            mimeType="application/json",
        ),
        types.Resource(
            uri="local://teams",
            name="Local NBA Teams",
            description="NBA teams from local database",
            mimeType="application/json",
        ),
        types.Resource(
            uri="local://players",
            name="Local NBA Players",
            description="NBA players from local database",
            mimeType="application/json",
        ),
        types.Resource(
            uri="local://matches",
            name="Local NBA Matches",
            description="NBA matches from local database",
            mimeType="application/json",
        ),
        types.Resource(
            uri="local://news",
            name="Local NBA News",
            description="NBA news from local database",
            mimeType="application/json",
        ),
        types.Resource(
            uri="supabase://tables",
            name="Supabase Database Tables",
            description="List all tables in Supabase NBA schema",
            mimeType="application/json",
        ),
        types.Resource(
            uri="supabase://teams",
            name="Supabase NBA Teams",
            description="NBA teams from Supabase",
            mimeType="application/json",
        ),
        types.Resource(
            uri="supabase://players",
            name="Supabase NBA Players",
            description="NBA players from Supabase",
            mimeType="application/json",
        ),
        types.Resource(
            uri="supabase://matches",
            name="Supabase NBA Matches",
            description="NBA matches from Supabase",
            mimeType="application/json",
        ),
        types.Resource(
            uri="supabase://news",
            name="Supabase NBA News",
            description="NBA news from Supabase",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    use_supabase = uri.startswith("supabase://")
    resource_type = uri.split("://")[1]
    
    conn = get_db_connection(use_supabase=use_supabase)
    cursor = conn.cursor()
    
    try:
        if resource_type == "tables":
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{DB_SCHEMA}'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            source = "Supabase" if use_supabase else "Local"
            return json.dumps({"source": source, "tables": tables}, indent=2)
        
        elif resource_type == "teams":
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Teams" LIMIT 100')
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            teams = [dict(zip(columns, row)) for row in rows]
            source = "Supabase" if use_supabase else "Local"
            return json.dumps({"source": source, "teams": teams}, indent=2, default=str)
        
        elif resource_type == "players":
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Players" LIMIT 100')
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            players = [dict(zip(columns, row)) for row in rows]
            source = "Supabase" if use_supabase else "Local"
            return json.dumps({"source": source, "players": players}, indent=2, default=str)
        
        elif resource_type == "matches":
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Matches" ORDER BY "Match_Date" DESC LIMIT 100')
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            matches = [dict(zip(columns, row)) for row in rows]
            source = "Supabase" if use_supabase else "Local"
            return json.dumps({"source": source, "matches": matches}, indent=2, default=str)
        
        elif resource_type == "news":
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."News" ORDER BY "Published_Date" DESC LIMIT 100')
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            news = [dict(zip(columns, row)) for row in rows]
            source = "Supabase" if use_supabase else "Local"
            return json.dumps({"source": source, "news": news}, indent=2, default=str)
        
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")
    
    finally:
        cursor.close()
        conn.close()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_database",
            description="Execute a SQL query on the NBA database (local or Supabase)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute",
                    },
                    "params": {
                        "type": "array",
                        "description": "Query parameters for parameterized queries",
                        "items": {"type": "string"},
                    },
                    "use_supabase": {
                        "type": "boolean",
                        "description": "Use Supabase instead of local database (default: true)",
                        "default": True,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_team_info",
            description="Get detailed information about an NBA team",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "Name of the team (e.g., 'Lakers', 'Warriors')",
                    },
                    "use_supabase": {
                        "type": "boolean",
                        "description": "Use Supabase instead of local database (default: true)",
                        "default": True,
                    },
                },
                "required": ["team_name"],
            },
        ),
        types.Tool(
            name="get_player_stats",
            description="Get player statistics and information",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "Name of the player",
                    },
                    "use_supabase": {
                        "type": "boolean",
                        "description": "Use Supabase instead of local database (default: true)",
                        "default": True,
                    },
                },
                "required": ["player_name"],
            },
        ),
        types.Tool(
            name="predict_game",
            description="Get prediction for an upcoming NBA game",
            inputSchema={
                "type": "object",
                "properties": {
                    "home_team": {
                        "type": "string",
                        "description": "Home team name",
                    },
                    "away_team": {
                        "type": "string",
                        "description": "Away team name",
                    },
                },
                "required": ["home_team", "away_team"],
            },
        ),
        types.Tool(
            name="search_news",
            description="Search NBA news articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Term to search for in news",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10,
                    },
                    "use_supabase": {
                        "type": "boolean",
                        "description": "Use Supabase instead of local database (default: true)",
                        "default": True,
                    },
                },
                "required": ["search_term"],
            },
        ),
        types.Tool(
            name="compare_databases",
            description="Compare data between local and Supabase databases",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Table to compare (e.g., 'Teams', 'Players', 'Matches')",
                    },
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="migrate_table",
            description="Migrate a single table from local PostgreSQL to Supabase",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Table to migrate (e.g., 'Teams', 'Players')",
                    },
                    "truncate": {
                        "type": "boolean",
                        "description": "Truncate Supabase table before inserting (default: true)",
                        "default": True,
                    },
                    "batch_size": {
                        "type": "integer",
                        "description": "Number of rows per batch (default: 1000)",
                        "default": 1000,
                    },
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="migrate_all_tables",
            description="Migrate all tables from local PostgreSQL to Supabase automatically",
            inputSchema={
                "type": "object",
                "properties": {
                    "batch_size": {
                        "type": "integer",
                        "description": "Number of rows per batch (default: 1000)",
                        "default": 1000,
                    },
                },
                "required": [],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    use_supabase = arguments.get("use_supabase", True) if arguments else True
    conn = get_db_connection(use_supabase=use_supabase)
    cursor = conn.cursor()
    
    try:
        if name == "query_database":
            query = arguments.get("query")
            params = arguments.get("params", [])
            source = "Supabase" if use_supabase else "Local"
            
            cursor.execute(query, params)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                result_text = json.dumps({"source": source, "results": results, "row_count": len(results)}, indent=2, default=str)
            else:
                result_text = json.dumps({"source": source, "message": "Query executed successfully", "rowcount": cursor.rowcount})
            
            return [types.TextContent(type="text", text=result_text)]
        
        elif name == "get_team_info":
            team_name = arguments.get("team_name")
            source = "Supabase" if use_supabase else "Local"
            
            cursor.execute(f"""
                SELECT * FROM "{DB_SCHEMA}"."Teams" 
                WHERE "Team_Name" ILIKE %s OR "Team_Abbreviation" ILIKE %s
            """, (f"%{team_name}%", f"%{team_name}%"))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            teams = [dict(zip(columns, row)) for row in rows]
            
            return [types.TextContent(type="text", text=json.dumps({"source": source, "teams": teams}, indent=2, default=str))]
        
        elif name == "get_player_stats":
            player_name = arguments.get("player_name")
            source = "Supabase" if use_supabase else "Local"
            
            cursor.execute(f"""
                SELECT * FROM "{DB_SCHEMA}"."Players" 
                WHERE "Player_Name" ILIKE %s
                LIMIT 10
            """, (f"%{player_name}%",))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            players = [dict(zip(columns, row)) for row in rows]
            
            return [types.TextContent(type="text", text=json.dumps({"source": source, "players": players}, indent=2, default=str))]
        
        elif name == "predict_game":
            raise NotImplementedError("Game prediction logic not implemented")
        
        elif name == "search_news":
            search_term = arguments.get("search_term")
            limit = arguments.get("limit", 10)
            source = "Supabase" if use_supabase else "Local"
            
            cursor.execute(f"""
                SELECT * FROM "{DB_SCHEMA}"."News" 
                WHERE "Title" ILIKE %s OR "Content" ILIKE %s
                ORDER BY "Published_Date" DESC
                LIMIT %s
            """, (f"%{search_term}%", f"%{search_term}%", limit))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            news = [dict(zip(columns, row)) for row in rows]
            
            return [types.TextContent(type="text", text=json.dumps({"source": source, "news": news}, indent=2, default=str))]
        
        elif name == "compare_databases":
            table_name = arguments.get("table_name")
            
            local_conn = get_db_connection(use_supabase=False)
            local_cursor = local_conn.cursor()
            
            supabase_conn = get_db_connection(use_supabase=True)
            supabase_cursor = supabase_conn.cursor()
            
            try:
                local_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
                local_count = local_cursor.fetchone()[0]
                
                supabase_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
                supabase_count = supabase_cursor.fetchone()[0]
                
                comparison = {
                    "table": table_name,
                    "local_count": local_count,
                    "supabase_count": supabase_count,
                    "difference": local_count - supabase_count,
                    "in_sync": local_count == supabase_count
                }
                
                return [types.TextContent(type="text", text=json.dumps(comparison, indent=2))]
            finally:
                local_cursor.close()
                local_conn.close()
                supabase_cursor.close()
                supabase_conn.close()
        
        elif name == "migrate_table":
            table_name = arguments.get("table_name")
            truncate = arguments.get("truncate", True)
            batch_size = arguments.get("batch_size", 1000)
            
            local_conn = get_db_connection(use_supabase=False)
            local_cursor = local_conn.cursor()
            
            supabase_conn = get_db_connection(use_supabase=True)
            supabase_cursor = supabase_conn.cursor()
            
            try:
                local_cursor.execute(f"""
                    SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_schema = '{DB_SCHEMA}' 
                    AND table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                columns = [row[0] for row in local_cursor.fetchall()]
                
                if not columns:
                    raise ValueError(f"Table {table_name} not found in local database")
                
                column_list = ', '.join([f'"{col}"' for col in columns])
                
                local_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
                local_count = local_cursor.fetchone()[0]
                
                if truncate:
                    supabase_cursor.execute(f'TRUNCATE TABLE "{DB_SCHEMA}"."{table_name}" CASCADE')
                    supabase_conn.commit()
                
                if local_count == 0:
                    result = {
                        "table": table_name,
                        "status": "skipped",
                        "message": "No data to migrate",
                        "rows_migrated": 0
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                local_cursor.execute(f'SELECT {column_list} FROM "{DB_SCHEMA}"."{table_name}"')
                
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f'INSERT INTO "{DB_SCHEMA}"."{table_name}" ({column_list}) VALUES ({placeholders})'
                
                inserted = 0
                batch = []
                
                while True:
                    rows = local_cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    
                    batch.extend(rows)
                    
                    if len(batch) >= batch_size:
                        supabase_cursor.executemany(insert_query, batch)
                        supabase_conn.commit()
                        inserted += len(batch)
                        batch = []
                
                if batch:
                    supabase_cursor.executemany(insert_query, batch)
                    supabase_conn.commit()
                    inserted += len(batch)
                
                supabase_cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
                supabase_count = supabase_cursor.fetchone()[0]
                
                result = {
                    "table": table_name,
                    "status": "success",
                    "local_count": local_count,
                    "rows_migrated": inserted,
                    "supabase_count": supabase_count,
                    "verified": local_count == supabase_count
                }
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                supabase_conn.rollback()
                result = {
                    "table": table_name,
                    "status": "error",
                    "error": str(e)
                }
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            finally:
                local_cursor.close()
                local_conn.close()
                supabase_cursor.close()
                supabase_conn.close()
        
        elif name == "migrate_all_tables":
            batch_size = arguments.get("batch_size", 1000)
            
            local_conn = get_db_connection(use_supabase=False)
            local_cursor = local_conn.cursor()
            
            try:
                local_cursor.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = '{DB_SCHEMA}'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                tables = [row[0] for row in local_cursor.fetchall()]
                
                results = {}
                total_rows = 0
                
                for table in tables:
                    table_result = await handle_call_tool("migrate_table", {
                        "table_name": table,
                        "truncate": True,
                        "batch_size": batch_size
                    })
                    
                    result_data = json.loads(table_result[0].text)
                    results[table] = result_data
                    
                    if result_data.get("status") == "success":
                        total_rows += result_data.get("rows_migrated", 0)
                
                summary = {
                    "status": "complete",
                    "tables_processed": len(tables),
                    "total_rows_migrated": total_rows,
                    "results": results
                }
                
                return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]
                
            finally:
                local_cursor.close()
                local_conn.close()
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    finally:
        cursor.close()
        conn.close()

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="analyze_team_performance",
            description="Analyze NBA team performance and statistics",
            arguments=[
                types.PromptArgument(
                    name="team_name",
                    description="Name of the team to analyze",
                    required=True,
                )
            ],
        ),
        types.Prompt(
            name="compare_players",
            description="Compare statistics between two NBA players",
            arguments=[
                types.PromptArgument(
                    name="player1",
                    description="First player name",
                    required=True,
                ),
                types.PromptArgument(
                    name="player2",
                    description="Second player name",
                    required=True,
                ),
            ],
        ),
        types.Prompt(
            name="recent_news_summary",
            description="Summarize recent NBA news",
            arguments=[
                types.PromptArgument(
                    name="topic",
                    description="Topic to focus on (optional)",
                    required=False,
                ),
            ],
        ),
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    if name == "analyze_team_performance":
        team_name = arguments.get("team_name", "")
        return types.GetPromptResult(
            description=f"Analyze performance of {team_name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please analyze the performance of {team_name}. Include their win/loss record, recent games, and key player statistics.",
                    ),
                )
            ],
        )
    
    elif name == "compare_players":
        player1 = arguments.get("player1", "")
        player2 = arguments.get("player2", "")
        return types.GetPromptResult(
            description=f"Compare {player1} vs {player2}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Compare the statistics and performance of {player1} and {player2}. Include points, rebounds, assists, and other key metrics.",
                    ),
                )
            ],
        )
    
    elif name == "recent_news_summary":
        topic = arguments.get("topic", "NBA")
        return types.GetPromptResult(
            description=f"Recent news about {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Summarize the most recent and important news about {topic}. Focus on major developments, player movements, and team performance.",
                    ),
                )
            ],
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nba-database-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

