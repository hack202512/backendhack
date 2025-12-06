-- Migration script to add found_time and circumstances columns to found_items table
-- Run this script in your PostgreSQL database

ALTER TABLE found_items 
ADD COLUMN IF NOT EXISTS found_time VARCHAR(5);

ALTER TABLE found_items 
ADD COLUMN IF NOT EXISTS circumstances VARCHAR(500);

