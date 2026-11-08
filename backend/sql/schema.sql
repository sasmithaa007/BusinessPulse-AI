-- ===================================================================
-- BusinessPulse AI - MySQL Database Schema
-- Unified Customer, Revenue & Operational Intelligence Platform
-- ===================================================================

CREATE DATABASE IF NOT EXISTS businesspulse_ai
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE businesspulse_ai;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB;

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL,
    customer_type VARCHAR(20) NOT NULL DEFAULT 'individual',
    business_scenario VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    segment VARCHAR(20) NOT NULL DEFAULT 'standard',
    lifetime_value DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
    churn_risk_score DECIMAL(5, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customers_scenario (business_scenario),
    INDEX idx_customers_status (status),
    INDEX idx_customers_segment (segment),
    INDEX idx_customers_signup (signup_date)
) ENGINE=InnoDB;

-- 3. Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    subscription_code VARCHAR(64) NOT NULL UNIQUE,
    plan_name VARCHAR(100) NOT NULL,
    monthly_amount DECIMAL(10, 2) NOT NULL,
    annual_amount DECIMAL(12, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    renewal_date DATE NULL,
    subscription_status VARCHAR(20) NOT NULL DEFAULT 'active',
    business_scenario VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_subscriptions_customer (customer_id),
    INDEX idx_subscriptions_scenario (business_scenario),
    INDEX idx_subscriptions_status (subscription_status),
    CONSTRAINT fk_subscriptions_customer FOREIGN KEY (customer_id)
        REFERENCES customers (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    transaction_code VARCHAR(64) NOT NULL UNIQUE,
    transaction_date TIMESTAMP NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    payment_method VARCHAR(30) NOT NULL,
    failure_reason VARCHAR(500) NULL,
    gateway VARCHAR(100) NOT NULL,
    processing_time_ms INT NOT NULL DEFAULT 0,
    business_scenario VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_transactions_customer (customer_id),
    INDEX idx_transactions_date (transaction_date),
    INDEX idx_transactions_status (status),
    INDEX idx_transactions_method (payment_method),
    INDEX idx_transactions_scenario (business_scenario),
    CONSTRAINT fk_transactions_customer FOREIGN KEY (customer_id)
        REFERENCES customers (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Product Usage Table
CREATE TABLE IF NOT EXISTS product_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    feature_name VARCHAR(200) NOT NULL,
    usage_count INT NOT NULL DEFAULT 1,
    usage_date DATE NOT NULL,
    session_duration_minutes DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    business_scenario VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_usage_customer (customer_id),
    INDEX idx_usage_feature (feature_name),
    INDEX idx_usage_date (usage_date),
    INDEX idx_usage_scenario (business_scenario),
    CONSTRAINT fk_usage_customer FOREIGN KEY (customer_id)
        REFERENCES customers (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. API Logs Table
CREATE TABLE IF NOT EXISTS api_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_time_ms INT NOT NULL DEFAULT 0,
    status_code INT NOT NULL,
    request_date TIMESTAMP NOT NULL,
    error_type VARCHAR(200) NULL,
    user_agent VARCHAR(500) NULL,
    business_scenario VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_api_endpoint (endpoint),
    INDEX idx_api_status (status_code),
    INDEX idx_api_date (request_date),
    INDEX idx_api_scenario (business_scenario)
) ENGINE=InnoDB;

-- 7. Operational Records Table
CREATE TABLE IF NOT EXISTS operational_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    process_name VARCHAR(200) NOT NULL,
    processing_time_seconds DECIMAL(8, 3) NOT NULL DEFAULT 0.000,
    operational_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    process_status VARCHAR(20) NOT NULL DEFAULT 'success',
    recorded_date DATE NOT NULL,
    department VARCHAR(100) NOT NULL,
    business_scenario VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ops_process (process_name),
    INDEX idx_ops_status (process_status),
    INDEX idx_ops_date (recorded_date),
    INDEX idx_ops_scenario (business_scenario)
) ENGINE=InnoDB;
