DROP TABLE IF EXISTS "NBA"."MatchEmbeddings" CASCADE;
CREATE TABLE "NBA"."MatchEmbeddings" (
  "GameID" integer NOT NULL,
  "Embedding" vector,
  "Description" text,
  "HomeTeam" varchar(50),
  "AwayTeam" varchar(50),
  "GameDate" date,
  "CreatedAt" timestamp without time zone
);
DROP TABLE IF EXISTS "NBA"."MatchPlayer" CASCADE;
CREATE TABLE "NBA"."MatchPlayer" (
  "MatchID" integer NOT NULL,
  "PlayerID" integer NOT NULL,
  "MP" integer NOT NULL,
  "FG" integer NOT NULL,
  "FGA" integer NOT NULL,
  "FGPercentage" numeric NOT NULL,
  "3P" integer NOT NULL,
  "3PA" integer NOT NULL,
  "3PPercentage" numeric NOT NULL,
  "FT" integer NOT NULL,
  "FTPercentage" numeric NOT NULL,
  "TRB" integer NOT NULL,
  "AST" integer NOT NULL,
  "BLK" integer NOT NULL,
  "TOV" integer NOT NULL,
  "PF" integer NOT NULL,
  "PTS" integer NOT NULL,
  "PlusMinus" integer NOT NULL
);
DROP TABLE IF EXISTS "NBA"."Matches" CASCADE;
CREATE TABLE "NBA"."Matches" (
  "HomeTeamID" integer NOT NULL,
  "VisitorTeamID" integer NOT NULL,
  "Date" date NOT NULL,
  "VisitorTeamName" character varying NOT NULL,
  "VisitorPoints" integer NOT NULL,
  "HomeTeamName" character varying NOT NULL,
  "HomeTeamScore" integer NOT NULL,
  "MatchID" integer NOT NULL
);
DROP TABLE IF EXISTS "NBA"."News" CASCADE;
CREATE TABLE "NBA"."News" (
  "NewsID" integer NOT NULL,
  "Title" character varying NOT NULL,
  "Date" date NOT NULL,
  "Source" character varying NOT NULL,
  "Author" character varying,
  "Content" character varying NOT NULL,
  "Embedding" vector
);
DROP TABLE IF EXISTS "NBA"."PlayerEmbeddings" CASCADE;
CREATE TABLE "NBA"."PlayerEmbeddings" (
  "PlayerID" integer NOT NULL,
  "Embedding" vector,
  "Description" text,
  "TeamID" integer,
  "CreatedAt" timestamp without time zone
);
DROP TABLE IF EXISTS "NBA"."Players" CASCADE;
CREATE TABLE "NBA"."Players" (
  "PlayerID" integer NOT NULL,
  "PlayerName" character varying NOT NULL,
  "Number" integer,
  "Position" character varying NOT NULL,
  "Height" integer,
  "Weight" integer,
  "Colleges" character varying,
  "Country" character varying
);
DROP TABLE IF EXISTS "NBA"."Schedule" CASCADE;
CREATE TABLE "NBA"."Schedule" (
  "GameID" integer NOT NULL,
  "Date" date NOT NULL,
  "Time" time without time zone,
  "HomeTeam" varchar(100) NOT NULL,
  "AwayTeam" varchar(100) NOT NULL,
  "HomeTeamID" varchar(10),
  "AwayTeamID" varchar(10),
  "Season" varchar(10) NOT NULL,
  "SeasonType" varchar(20),
  "Status" varchar(20),
  "HomeScore" integer,
  "AwayScore" integer,
  "Venue" varchar(200),
  "City" varchar(100),
  "State" varchar(50),
  "CreatedAt" timestamp without time zone
);
DROP TABLE IF EXISTS "NBA"."Season2024_25_News" CASCADE;
CREATE TABLE "NBA"."Season2024_25_News" (
  "NewsID" integer NOT NULL,
  "Title" text NOT NULL,
  "Content" text,
  "Date" date NOT NULL,
  "Team" varchar(50),
  "Sentiment" varchar(20),
  "Season" varchar(10)
);
DROP TABLE IF EXISTS "NBA"."Season2024_25_Results" CASCADE;
CREATE TABLE "NBA"."Season2024_25_Results" (
  "GameID" integer NOT NULL,
  "Date" date NOT NULL,
  "HomeTeam" varchar(50) NOT NULL,
  "AwayTeam" varchar(50) NOT NULL,
  "HomeScore" integer NOT NULL,
  "AwayScore" integer NOT NULL,
  "Winner" varchar(50) NOT NULL,
  "Margin" integer NOT NULL,
  "TotalPoints" integer NOT NULL,
  "Overtime" boolean,
  "Season" varchar(10),
  "SeasonType" varchar(20)
);
DROP TABLE IF EXISTS "NBA"."Season2024_25_Schedule" CASCADE;
CREATE TABLE "NBA"."Season2024_25_Schedule" (
  "GameID" integer NOT NULL,
  "Date" date NOT NULL,
  "Time" varchar(20),
  "HomeTeam" varchar(50) NOT NULL,
  "AwayTeam" varchar(50) NOT NULL,
  "Venue" varchar(100),
  "Season" varchar(10),
  "SeasonType" varchar(20)
);
DROP TABLE IF EXISTS "NBA"."TeamEmbeddings" CASCADE;
CREATE TABLE "NBA"."TeamEmbeddings" (
  "TeamID" integer NOT NULL,
  "Embedding" vector,
  "Description" text,
  "CreatedAt" timestamp without time zone
);
DROP TABLE IF EXISTS "NBA"."TeamPlayer" CASCADE;
CREATE TABLE "NBA"."TeamPlayer" (
  "TeamID" integer NOT NULL,
  "PlayerID" character varying NOT NULL,
  "TeamName" character varying NOT NULL,
  "PlayerName" character varying NOT NULL,
  "From" date NOT NULL,
  "To" date NOT NULL,
  "Years" integer NOT NULL
);
DROP TABLE IF EXISTS "NBA"."Teams" CASCADE;
CREATE TABLE "NBA"."Teams" (
  "TeamID" integer NOT NULL,
  "TeamName" character varying NOT NULL,
  "From" date NOT NULL,
  "To" date,
  "Years" integer NOT NULL,
  "Games" integer NOT NULL,
  "WinPercentage" numeric NOT NULL,
  "Playoffs" integer NOT NULL,
  "ConferenceChampion" integer NOT NULL,
  "Championship" integer NOT NULL,
  "Conference" character varying,
  "Division" character varying
);
DROP TABLE IF EXISTS "NBA"."Test2024_25" CASCADE;
CREATE TABLE "NBA"."Test2024_25" (
  "ID" integer NOT NULL,
  "Team" varchar(50),
  "Wins" integer,
  "Losses" integer
);
DROP TABLE IF EXISTS "NBA"."VectorNews" CASCADE;
CREATE TABLE "NBA"."VectorNews" (
  "NewsID" integer NOT NULL,
  "NewsVector" vector NOT NULL
);
DROP TABLE IF EXISTS "NBA"."entity" CASCADE;
CREATE TABLE "NBA"."entity" (
  "id" uuid NOT NULL,
  "etype" entity_type NOT NULL,
  "name" text NOT NULL,
  "props" jsonb,
  "created_at" timestamp with time zone
);
DROP TABLE IF EXISTS "NBA"."entity_mention" CASCADE;
CREATE TABLE "NBA"."entity_mention" (
  "id" uuid NOT NULL,
  "news_id" uuid,
  "entity_id" uuid,
  "details" jsonb,
  "source" text NOT NULL,
  "created_at" timestamp with time zone
);
DROP TABLE IF EXISTS "NBA"."news" CASCADE;
CREATE TABLE "NBA"."news" (
  "id" uuid NOT NULL,
  "title" text,
  "body" text,
  "url" text,
  "published_at" timestamp with time zone,
  "source" text,
  "created_at" timestamp with time zone
);