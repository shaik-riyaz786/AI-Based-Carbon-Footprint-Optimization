-- Create a database named depression_db
CREATE DATABASE IF NOT EXISTS esg_db;

-- Use the created database
USE esg_db;

-- Create a table to store user information
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,           -- Unique ID for each user, auto-incremented
    username VARCHAR(50) UNIQUE NOT NULL,       -- Username, must be unique
    email VARCHAR(100) UNIQUE NOT NULL,         -- Email address, must be unique
    password VARCHAR(255) NOT NULL,             -- Password (plain text for simplicity; consider hashing in production)
    mobile VARCHAR(15) NOT NULL                 -- Mobile number
);

-- Optional: Insert a sample user for testing
INSERT INTO users (username, email, password, mobile) 
VALUES ('testuser', 'test@example.com', 'password123', '1234567890');