from query_processor import QueryProcessor
import re

def debug_query(query):
    print(f"\n--- Debugging: '{query}' ---")
    
    # 1. Processing
    processor = QueryProcessor()
    result = processor.process_query(query)
    
    print(f"Query Type: {result['query_type']}")
    print(f"Teams Detected (Regex/Entity): {result['team1']}, {result['team2']}")
    print(f"Teams Found List: {result['teams_found']}")
    print(f"Is Valid Matchup: {result['is_valid_matchup']}")
    
    # 2. Check Regex Directly
    print("\nRegex Checks:")
    for pattern in processor.query_patterns:
        matches = re.findall(pattern, query.lower(), re.IGNORECASE)
        if matches:
            print(f"  Matched: {pattern} -> {matches}")
            
    # 3. Simulate What Chatbot.py Does
    print("\nChatbot Logic Simulation:")
    if result['query_type'] == 'prediction' and result['is_valid_matchup']:
        print("  -> Would enter PREDICTION block")
    elif result['query_type'] == 'prediction':
        print("  -> Has PREDICTION intent but INVALID matchup")
        # This is where LLM fallback kicks in currently depending on conditions
        
if __name__ == "__main__":
    debug_query("predict warriors vs suns")
    debug_query("who will win lakers vs celtics")
