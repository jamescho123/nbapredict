-- NBA Database Export - Part 1: Schema and Setup
-- Generated: 2025-10-24 20:38:31.055032

CREATE SCHEMA IF NOT EXISTS "NBA";

CREATE EXTENSION IF NOT EXISTS vector;

-- Custom ENUM types
CREATE TYPE entity_type AS ENUM ('player', 'team', 'game', 'injury', 'conflict', 'stat', 'penalty', 'trade', 'award', 'location', 'date');

