-- SQL script executed automatically on PostgreSQL container startup
-- Creates isolated databases for each microservice following Database-per-Service pattern

-- Create dedicated database for Authentication Service
CREATE DATABASE auth_db;

-- Create dedicated database for User Profile Service
CREATE DATABASE user_db;

-- Create dedicated database for Task Management Service
CREATE DATABASE task_db;
