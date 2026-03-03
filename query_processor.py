import re
import json
from typing import List, Optional, Tuple
from nba_entity_extractor_offline import NBAEntityExtractorOffline

class QueryProcessor:
    def __init__(self):
        self.extractor = NBAEntityExtractorOffline()
        
        # Common team names and variations
        self.team_mappings = {
            'boston celtics': ['boston', 'celtics', 'boston celtics'],
            'atlanta hawks': ['atlanta', 'hawks', 'atlanta hawks'],
            'los angeles lakers': ['lakers', 'la lakers', 'los angeles lakers'],
            'golden state warriors': ['warriors', 'golden state', 'gsw'],
            'miami heat': ['heat', 'miami', 'miami heat'],
            'chicago bulls': ['bulls', 'chicago', 'chicago bulls'],
            'new york knicks': ['knicks', 'new york', 'ny knicks'],
            'brooklyn nets': ['nets', 'brooklyn', 'brooklyn nets'],
            'philadelphia 76ers': ['76ers', 'philadelphia', 'sixers'],
            'toronto raptors': ['raptors', 'toronto', 'toronto raptors'],
            'milwaukee bucks': ['bucks', 'milwaukee', 'milwaukee bucks'],
            'indiana pacers': ['pacers', 'indiana', 'indiana pacers'],
            'charlotte hornets': ['hornets', 'charlotte', 'charlotte hornets'],
            'orlando magic': ['magic', 'orlando', 'orlando magic'],
            'washington wizards': ['wizards', 'washington', 'washington wizards'],
            'cleveland cavaliers': ['cavaliers', 'cavs', 'cleveland'],
            'detroit pistons': ['pistons', 'detroit', 'detroit pistons'],
            'minnesota timberwolves': ['timberwolves', 'wolves', 'minnesota'],
            'oklahoma city thunder': ['thunder', 'okc', 'oklahoma city'],
            'portland trail blazers': ['trail blazers', 'blazers', 'portland'],
            'utah jazz': ['jazz', 'utah', 'utah jazz'],
            'denver nuggets': ['nuggets', 'denver', 'denver nuggets'],
            'phoenix suns': ['suns', 'phoenix', 'phoenix suns'],
            'sacramento kings': ['kings', 'sacramento', 'sacramento kings'],
            'los angeles clippers': ['clippers', 'la clippers', 'los angeles clippers'],
            'dallas mavericks': ['mavericks', 'mavs', 'dallas'],
            'houston rockets': ['rockets', 'houston', 'houston rockets'],
            'memphis grizzlies': ['grizzlies', 'memphis', 'memphis grizzlies'],
            'new orleans pelicans': ['pelicans', 'new orleans', 'nola']
        }
        
        # Query patterns
        self.query_patterns = [
            r'who will win.*?(\w+(?:\s+\w+)*).*?(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*).*?vs.*?(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*).*?against.*?(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*).*?versus.*?(\w+(?:\s+\w+)*)',
            r'predict.*?(\w+(?:\s+\w+)*).*?(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*).*?(\w+(?:\s+\w+)*).*?prediction'
        ]
    
    def extract_teams_from_query(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract team names from a natural language query"""
        query_lower = query.lower()
        
        # Try each pattern
        for pattern in self.query_patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            if matches:
                for match in matches:
                    if len(match) == 2:
                        team1, team2 = match
                        team1_clean = self._normalize_team_name(team1.strip())
                        team2_clean = self._normalize_team_name(team2.strip())
                        
                        if team1_clean and team2_clean and team1_clean != team2_clean:
                            return team1_clean, team2_clean
        
        # Fallback: look for any team names in the query
        found_teams = []
        for team_name, variations in self.team_mappings.items():
            for variation in variations:
                if variation in query_lower:
                    found_teams.append(team_name)
                    break
        
        if len(found_teams) >= 2:
            return found_teams[0], found_teams[1]
        
        return None, None
    
    def _normalize_team_name(self, team_text: str) -> Optional[str]:
        """Normalize team name to standard format"""
        team_text = team_text.strip().lower()
        
        for team_name, variations in self.team_mappings.items():
            for variation in variations:
                if variation in team_text or team_text in variation:
                    return team_name
        
        return None
    
    def extract_entities_from_query(self, query: str) -> dict:
        """Extract entities from the query using the entity extractor"""
        try:
            # Use the offline extractor to find entities
            extracted_data = self.extractor.extract_entities_offline(query, "")
            
            if extracted_data:
                return {
                    'entities': extracted_data.get('entities', []),
                    'teams_found': self._find_teams_in_entities(extracted_data.get('entities', [])),
                    'query_type': self._classify_query(query)
                }
        except Exception as e:
            print(f"Error extracting entities: {e}")
        
        return {
            'entities': [],
            'teams_found': [],
            'query_type': 'unknown'
        }
    
    def _find_teams_in_entities(self, entities: List[dict]) -> List[str]:
        """Find team entities in the extracted entities"""
        teams = []
        for entity in entities:
            if entity.get('type') == 'team':
                teams.append(entity.get('name', ''))
        return teams
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['stats', 'statistics', 'performance', 'record']):
            return 'stats'
        elif any(word in query_lower for word in ['injury', 'injured', 'hurt', 'out']):
            return 'injury'
        elif any(word in query_lower for word in ['score', 'result', 'won', 'win', 'beat', 'defeat', 'lost', 'lose', 'last game', 'previous']):
            # Special case: "who will win" is prediction, while "who won" is result
            if 'will' in query_lower or 'predict' in query_lower:
                return 'prediction'
            return 'result'
        elif 'predict' in query_lower or 'prediction' in query_lower:
            return 'prediction'
        elif any(word in query_lower for word in ['news', 'recent', 'latest', 'update']):
            return 'news'
        else:
            return 'general'
    
    def process_query(self, query: str) -> dict:
        """Process a natural language query and return structured data"""
        # Extract teams using regex
        team1, team2 = self.extract_teams_from_query(query)
        
        # Extract entities using NLP
        entity_data = self.extract_entities_from_query(query)
        teams_found = entity_data['teams_found']
        
        # Fallback to entities if regex failed
        if team1 is None or team2 is None:
            if len(teams_found) >= 2:
                team1 = teams_found[0]
                team2 = teams_found[1]
                # Normalize names just in case
                t1_clean = self._normalize_team_name(team1)
                t2_clean = self._normalize_team_name(team2)
                if t1_clean and t2_clean:
                    team1 = t1_clean
                    team2 = t2_clean
        
        # If we found two teams but query type is unknown/general, it is likely a prediction or stats request
        # If it contains "vs" or "against", assume prediction
        query_type = entity_data['query_type']
        if query_type == 'general' and team1 and team2:
            if hasattr(self, 'query_patterns') and any(x in query.lower() for x in ['vs', 'versus', 'against', '@']):
                query_type = 'prediction'

        return {
            'original_query': query,
            'team1': team1,
            'team2': team2,
            'entities': entity_data['entities'],
            'teams_found': teams_found,
            'query_type': query_type,
            'is_valid_matchup': team1 is not None and team2 is not None
        }

if __name__ == "__main__":
    # Test the query processor
    processor = QueryProcessor()
    
    test_queries = [
        "who will win, Boston Celtics or Atlanta Hawks",
        "Boston vs Atlanta prediction",
        "Celtics against Hawks who wins",
        "predict Lakers vs Warriors",
        "Miami Heat versus Chicago Bulls"
    ]
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"Query: {query}")
        print(f"Teams: {result['team1']} vs {result['team2']}")
        print(f"Query Type: {result['query_type']}")
        print(f"Valid Matchup: {result['is_valid_matchup']}")
        print("-" * 50)
