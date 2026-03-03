#!/usr/bin/env python3
"""
Data Validation Tests for NBA Prediction Model
Verifies factual accuracy of stats and news data used in predictions
"""

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
import os
import requests
import json
from typing import Dict, List, Tuple, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import (
    get_team_stats, 
    get_team_news, 
    get_time_weighted_team_news,
    get_player_stats,
    get_head_to_head_record,
    calculate_team_form,
    get_team_context_data
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataValidator:
    """Comprehensive data validation system for NBA prediction model"""
    
    def __init__(self):
        self.conn = None
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        
    def connect_to_database(self):
        """Connect to the PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logging.info("Database connection successful")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def test_database_schema(self):
        """Test database schema and table structure"""
        print("🔍 Testing Database Schema...")
        print("-" * 50)
        
        if not self.conn:
            self.errors.append("No database connection")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Check if NBA schema exists
            cursor.execute("""
                SELECT schema_name FROM information_schema.schemata 
                WHERE schema_name = 'NBA'
            """)
            if not cursor.fetchone():
                self.errors.append("NBA schema does not exist")
                return False
            
            # Check required tables
            required_tables = ['Teams', 'Players', 'News', 'Schedule', 'Matches']
            existing_tables = []
            
            for table in required_tables:
                cursor.execute(f"""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'NBA' AND table_name = '{table}'
                """)
                if cursor.fetchone():
                    existing_tables.append(table)
                else:
                    self.warnings.append(f"Table 'NBA.{table}' does not exist")
            
            print(f"✅ Found {len(existing_tables)}/{len(required_tables)} required tables")
            for table in existing_tables:
                print(f"   ✓ {table}")
            
            # Check table structures
            for table in existing_tables:
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_schema = 'NBA' AND table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"\n📋 {table} table structure:")
                for col_name, col_type, nullable in columns:
                    print(f"   {col_name}: {col_type} ({'nullable' if nullable == 'YES' else 'not null'})")
            
            self.validation_results['schema'] = {
                'existing_tables': existing_tables,
                'missing_tables': [t for t in required_tables if t not in existing_tables]
            }
            
            return True
            
        except Exception as e:
            self.errors.append(f"Schema validation error: {e}")
            return False
    
    def test_team_stats_data(self):
        """Test team statistics data for accuracy and completeness"""
        print("\n🏀 Testing Team Statistics Data...")
        print("-" * 50)
        
        if not self.conn:
            self.errors.append("No database connection for team stats test")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Check if Teams table has data
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Teams"')
            team_count = cursor.fetchone()[0]
            print(f"📊 Total teams in database: {team_count}")
            
            if team_count == 0:
                self.warnings.append("No team data found in Teams table")
                return False
            
            # Get sample team data
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Teams" LIMIT 5')
            sample_teams = cursor.fetchall()
            
            print(f"\n📋 Sample team data:")
            for team in sample_teams:
                print(f"   {team}")
            
            # Test team stats retrieval function
            test_teams = ['Boston Celtics', 'Los Angeles Lakers', 'Golden State Warriors']
            stats_results = {}
            
            for team in test_teams:
                try:
                    stats = get_team_stats(team)
                    if stats:
                        stats_results[team] = stats
                        print(f"✅ {team}: {stats}")
                    else:
                        self.warnings.append(f"No stats found for {team}")
                except Exception as e:
                    self.errors.append(f"Error getting stats for {team}: {e}")
            
            self.validation_results['team_stats'] = {
                'total_teams': team_count,
                'sample_data': sample_teams,
                'stats_retrieval': stats_results
            }
            
            return True
            
        except Exception as e:
            self.errors.append(f"Team stats validation error: {e}")
            return False
    
    def test_news_data(self):
        """Test news data for accuracy and recency"""
        print("\n📰 Testing News Data...")
        print("-" * 50)
        
        if not self.conn:
            self.errors.append("No database connection for news test")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Check if News table has data
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."News"')
            news_count = cursor.fetchone()[0]
            print(f"📊 Total news articles in database: {news_count}")
            
            if news_count == 0:
                self.warnings.append("No news data found in News table")
                return False
            
            # Get recent news sample
            cursor.execute(f'''
                SELECT "NewsID", "Title", "Date", "Content" 
                FROM "{DB_SCHEMA}"."News" 
                ORDER BY "Date" DESC 
                LIMIT 5
            ''')
            recent_news = cursor.fetchall()
            
            print(f"\n📋 Recent news sample:")
            for news in recent_news:
                news_id, title, date, content = news
                print(f"   ID: {news_id}, Date: {date}")
                print(f"   Title: {title[:100]}...")
                print(f"   Content: {content[:150]}...")
                print()
            
            # Test news retrieval functions
            test_teams = ['Boston Celtics', 'Los Angeles Lakers']
            news_results = {}
            
            for team in test_teams:
                try:
                    # Test regular news retrieval
                    news = get_team_news(team, limit=5)
                    news_results[team] = {
                        'regular_news_count': len(news),
                        'regular_news': news[:2] if news else []
                    }
                    
                    # Test time-weighted news retrieval
                    time_weighted_news = get_time_weighted_team_news(team, days_back=30, limit=5)
                    news_results[team]['time_weighted_count'] = len(time_weighted_news)
                    news_results[team]['time_weighted_news'] = time_weighted_news[:2] if time_weighted_news else []
                    
                    print(f"✅ {team}: {len(news)} regular news, {len(time_weighted_news)} time-weighted news")
                    
                except Exception as e:
                    self.errors.append(f"Error getting news for {team}: {e}")
            
            # Check news date distribution
            cursor.execute(f'''
                SELECT 
                    DATE_TRUNC('month', "Date") as month,
                    COUNT(*) as count
                FROM "{DB_SCHEMA}"."News"
                GROUP BY DATE_TRUNC('month', "Date")
                ORDER BY month DESC
                LIMIT 6
            ''')
            date_distribution = cursor.fetchall()
            
            print(f"\n📅 News distribution by month:")
            for month, count in date_distribution:
                print(f"   {month.strftime('%Y-%m')}: {count} articles")
            
            self.validation_results['news'] = {
                'total_articles': news_count,
                'sample_news': recent_news,
                'retrieval_tests': news_results,
                'date_distribution': date_distribution
            }
            
            return True
            
        except Exception as e:
            self.errors.append(f"News validation error: {e}")
            return False
    
    def test_player_data(self):
        """Test player data for accuracy and completeness"""
        print("\n👥 Testing Player Data...")
        print("-" * 50)
        
        if not self.conn:
            self.errors.append("No database connection for player test")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Check if Players table has data
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Players"')
            player_count = cursor.fetchone()[0]
            print(f"📊 Total players in database: {player_count}")
            
            if player_count == 0:
                self.warnings.append("No player data found in Players table")
                return False
            
            # Get sample player data
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Players" LIMIT 5')
            sample_players = cursor.fetchall()
            
            print(f"\n📋 Sample player data:")
            for player in sample_players:
                print(f"   {player}")
            
            # Test player stats retrieval
            test_teams = ['Boston Celtics', 'Los Angeles Lakers']
            player_results = {}
            
            for team in test_teams:
                try:
                    players = get_player_stats(team, limit=5)
                    if not players.empty:
                        player_results[team] = {
                            'count': len(players),
                            'sample': players.head(2).to_dict('records')
                        }
                        print(f"✅ {team}: {len(players)} players")
                    else:
                        self.warnings.append(f"No players found for {team}")
                except Exception as e:
                    self.errors.append(f"Error getting players for {team}: {e}")
            
            self.validation_results['players'] = {
                'total_players': player_count,
                'sample_data': sample_players,
                'retrieval_tests': player_results
            }
            
            return True
            
        except Exception as e:
            self.errors.append(f"Player validation error: {e}")
            return False
    
    def test_schedule_data(self):
        """Test schedule data for accuracy and completeness"""
        print("\n📅 Testing Schedule Data...")
        print("-" * 50)
        
        if not self.conn:
            self.errors.append("No database connection for schedule test")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Check if Schedule table has data
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Schedule"')
            schedule_count = cursor.fetchone()[0]
            print(f"📊 Total scheduled games: {schedule_count}")
            
            if schedule_count == 0:
                self.warnings.append("No schedule data found in Schedule table")
                return False
            
            # Get upcoming games
            cursor.execute(f'''
                SELECT "Date", "HomeTeam", "AwayTeam", "Time", "Venue"
                FROM "{DB_SCHEMA}"."Schedule"
                WHERE "Date" >= CURRENT_DATE
                ORDER BY "Date" ASC
                LIMIT 10
            ''')
            upcoming_games = cursor.fetchall()
            
            print(f"\n📋 Upcoming games:")
            for game in upcoming_games:
                date, home, away, time, venue = game
                print(f"   {date} {time}: {away} @ {home} ({venue})")
            
            # Check date range
            cursor.execute(f'''
                SELECT MIN("Date") as earliest, MAX("Date") as latest
                FROM "{DB_SCHEMA}"."Schedule"
            ''')
            date_range = cursor.fetchone()
            print(f"\n📅 Schedule date range: {date_range[0]} to {date_range[1]}")
            
            # Check team distribution
            cursor.execute(f'''
                SELECT "HomeTeam", COUNT(*) as home_games
                FROM "{DB_SCHEMA}"."Schedule"
                GROUP BY "HomeTeam"
                ORDER BY home_games DESC
                LIMIT 5
            ''')
            team_distribution = cursor.fetchall()
            
            print(f"\n🏀 Teams with most home games:")
            for team, count in team_distribution:
                print(f"   {team}: {count} home games")
            
            self.validation_results['schedule'] = {
                'total_games': schedule_count,
                'upcoming_games': upcoming_games,
                'date_range': date_range,
                'team_distribution': team_distribution
            }
            
            return True
            
        except Exception as e:
            self.errors.append(f"Schedule validation error: {e}")
            return False
    
    def test_data_consistency(self):
        """Test data consistency across different sources"""
        print("\n🔄 Testing Data Consistency...")
        print("-" * 50)
        
        consistency_issues = []
        
        try:
            # Test team name consistency
            cursor = self.conn.cursor()
            
            # Get teams from different tables
            cursor.execute(f'SELECT DISTINCT "HomeTeam" FROM "{DB_SCHEMA}"."Schedule"')
            schedule_teams = set(row[0] for row in cursor.fetchall())
            
            cursor.execute(f'SELECT DISTINCT "TeamName" FROM "{DB_SCHEMA}"."Teams"')
            teams_table_teams = set(row[0] for row in cursor.fetchall())
            
            # Check for mismatches
            schedule_only = schedule_teams - teams_table_teams
            teams_only = teams_table_teams - schedule_teams
            
            if schedule_only:
                consistency_issues.append(f"Teams in schedule but not in Teams table: {list(schedule_only)}")
            if teams_only:
                consistency_issues.append(f"Teams in Teams table but not in schedule: {list(teams_only)}")
            
            print(f"📊 Team name consistency:")
            print(f"   Schedule teams: {len(schedule_teams)}")
            print(f"   Teams table: {len(teams_table_teams)}")
            print(f"   Common teams: {len(schedule_teams & teams_table_teams)}")
            
            # Test date consistency
            cursor.execute(f'''
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(DISTINCT "Date") as unique_dates,
                    MIN("Date") as earliest_date,
                    MAX("Date") as latest_date
                FROM "{DB_SCHEMA}"."Schedule"
            ''')
            date_stats = cursor.fetchone()
            
            print(f"\n📅 Date consistency:")
            print(f"   Total games: {date_stats[0]}")
            print(f"   Unique dates: {date_stats[1]}")
            print(f"   Date range: {date_stats[2]} to {date_stats[3]}")
            
            # Check for duplicate games
            cursor.execute(f'''
                SELECT "Date", "HomeTeam", "AwayTeam", COUNT(*)
                FROM "{DB_SCHEMA}"."Schedule"
                GROUP BY "Date", "HomeTeam", "AwayTeam"
                HAVING COUNT(*) > 1
            ''')
            duplicates = cursor.fetchall()
            
            if duplicates:
                consistency_issues.append(f"Duplicate games found: {len(duplicates)}")
                print(f"⚠️ Found {len(duplicates)} duplicate games")
            else:
                print(f"✅ No duplicate games found")
            
            self.validation_results['consistency'] = {
                'team_consistency': {
                    'schedule_teams': len(schedule_teams),
                    'teams_table_teams': len(teams_table_teams),
                    'common_teams': len(schedule_teams & teams_table_teams)
                },
                'date_stats': date_stats,
                'duplicates': len(duplicates),
                'issues': consistency_issues
            }
            
            return len(consistency_issues) == 0
            
        except Exception as e:
            self.errors.append(f"Consistency validation error: {e}")
            return False
    
    def test_prediction_data_flow(self):
        """Test the complete data flow used in predictions"""
        print("\n🔄 Testing Prediction Data Flow...")
        print("-" * 50)
        
        test_teams = ['Boston Celtics', 'Los Angeles Lakers']
        
        for home_team, away_team in [(test_teams[0], test_teams[1]), (test_teams[1], test_teams[0])]:
            print(f"\n🏀 Testing: {away_team} @ {home_team}")
            
            try:
                # Test team context data retrieval
                home_context = get_team_context_data(home_team)
                away_context = get_team_context_data(away_team)
                
                print(f"   Home context: {bool(home_context)}")
                print(f"   Away context: {bool(away_context)}")
                
                if home_context:
                    print(f"   Home team stats: {home_context.get('team_stats', {})}")
                    print(f"   Home recent form: {home_context.get('recent_form', {})}")
                    print(f"   Home news count: {len(home_context.get('news', []))}")
                
                if away_context:
                    print(f"   Away team stats: {away_context.get('team_stats', {})}")
                    print(f"   Away recent form: {away_context.get('recent_form', {})}")
                    print(f"   Away news count: {len(away_context.get('news', []))}")
                
                # Test head-to-head data
                h2h = get_head_to_head_record(home_team, away_team)
                print(f"   Head-to-head: {h2h}")
                
            except Exception as e:
                self.errors.append(f"Data flow test error for {home_team} vs {away_team}: {e}")
                print(f"   ❌ Error: {e}")
    
    def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🔍 Starting Comprehensive Data Validation")
        print("=" * 80)
        
        if not self.connect_to_database():
            print("❌ Failed to connect to database")
            return False
        
        # Run all tests
        tests = [
            ("Database Schema", self.test_database_schema),
            ("Team Statistics", self.test_team_stats_data),
            ("News Data", self.test_news_data),
            ("Player Data", self.test_player_data),
            ("Schedule Data", self.test_schedule_data),
            ("Data Consistency", self.test_data_consistency),
            ("Prediction Data Flow", self.test_prediction_data_flow)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.errors.append(f"{test_name} test error: {e}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Save results
        self.save_validation_results()
        
        return passed_tests == total_tests
    
    def save_validation_results(self):
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_validation_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'validation_results': self.validation_results,
                    'errors': self.errors,
                    'warnings': self.warnings
                }, f, indent=2, default=str)
            
            print(f"\n💾 Validation results saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """Main function to run data validation"""
    validator = DataValidator()
    success = validator.run_comprehensive_validation()
    
    if success:
        print("\n🎉 All validation tests passed!")
    else:
        print("\n⚠️ Some validation tests failed. Check the results above.")

if __name__ == "__main__":
    main()
