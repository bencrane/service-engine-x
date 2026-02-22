-- Migration: Remove systems and system_access tables
-- Run: psql $DATABASE_URL -f migrations/008_drop_systems.sql
DROP TABLE IF EXISTS system_access;
DROP TABLE IF EXISTS systems;
