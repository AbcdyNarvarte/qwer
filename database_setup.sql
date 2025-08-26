-- Reset and recreate database without separate suppliers table
CREATE DATABASE IF NOT EXISTS `db`;
USE `db`;

-- To allow dropping in any order
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `supplier_orders`;
DROP TABLE IF EXISTS `material_requests`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `raw_mats`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `clients`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

-- Create users table (includes suppliers via user_level='supplier')
CREATE TABLE IF NOT EXISTS `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL UNIQUE,
    `password` varchar(255) NOT NULL,
    `user_level` enum('owner', 'manager', 'supplier', 'employee') NOT NULL,
    `name` varchar(100) NOT NULL,
    `surname` varchar(100) NOT NULL,
    `email` varchar(150) NOT NULL,
    `number` varchar(20) NOT NULL,
    `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create clients table
CREATE TABLE IF NOT EXISTS `clients` (
    `client_id` int(11) NOT NULL AUTO_INCREMENT,
    `client_name` varchar(100) NOT NULL,
    `client_email` varchar(150) NOT NULL,
    `client_address` text NOT NULL,
    `client_contactnum` varchar(20) NOT NULL,
    `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create products table
CREATE TABLE IF NOT EXISTS `products` (
    `product_id` varchar(20) NOT NULL,
    `product_name` varchar(100) NOT NULL,
    `materials` text NOT NULL,
    `created_date` timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create raw materials table
-- supplier_id now references users(id) where users.user_level = 'supplier' (enforced at app level)
CREATE TABLE IF NOT EXISTS `raw_mats` (
    `mat_id` int(11) NOT NULL AUTO_INCREMENT,
    `mat_name` varchar(100) NOT NULL UNIQUE,
    `mat_volume` int(11) NOT NULL,
    `unit_of_measurement` varchar(20) NOT NULL DEFAULT 'units',
    `low_count` int(11) NOT NULL DEFAULT 10,
    `mat_order_date` timestamp DEFAULT CURRENT_TIMESTAMP,
    `supplier_id` int(11) NOT NULL,
    PRIMARY KEY (`mat_id`),
    CONSTRAINT `fk_raw_mats_supplier_user`
        FOREIGN KEY (`supplier_id`) REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create orders table
CREATE TABLE IF NOT EXISTS `orders` (
    `order_id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `order_name` VARCHAR(255) NOT NULL,
    `product_id` VARCHAR(20) NOT NULL,
    `client_id` INT(11) NOT NULL,
    `quantity` INT(11) NOT NULL,
    `deadline` DATE NOT NULL,
    `order_date` DATE NOT NULL,
    `mats_need` TEXT,
    `status_quo` VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
    FOREIGN KEY (`client_id`) REFERENCES `clients`(`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create material requests table
CREATE TABLE IF NOT EXISTS `material_requests` (
    `request_id` int(11) NOT NULL AUTO_INCREMENT,
    `mat_id` int(11) NOT NULL,
    `requested_quantity` int(11) NOT NULL,
    `reason` text NOT NULL,
    `status` enum('pending', 'approved', 'rejected') DEFAULT 'pending',
    `requested_by` int(11) NOT NULL,
    `requested_at` timestamp DEFAULT CURRENT_TIMESTAMP,
    `processed_at` timestamp NULL,
    `processed_by` int(11) NULL,
    PRIMARY KEY (`request_id`),
    FOREIGN KEY (`mat_id`) REFERENCES `raw_mats`(`mat_id`) ON DELETE CASCADE,
    FOREIGN KEY (`requested_by`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`processed_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create supplier orders table (supplier_id references users.id)
CREATE TABLE IF NOT EXISTS `supplier_orders` (
    `supplier_order_id` int(11) NOT NULL AUTO_INCREMENT,
    `mat_id` int(11) NOT NULL,
    `supplier_id` int(11) NOT NULL,
    `requested_quantity` int(11) NOT NULL,
    `order_date` timestamp DEFAULT CURRENT_TIMESTAMP,
    `expected_delivery_date` date NULL,
    `actual_delivery_date` date NULL,
    `status` enum('pending', 'confirmed', 'delivered') DEFAULT 'pending',
    `notes` text NULL,
    `ordered_by` int(11) NOT NULL,
    PRIMARY KEY (`supplier_order_id`),
    FOREIGN KEY (`mat_id`) REFERENCES `raw_mats`(`mat_id`) ON DELETE CASCADE,
    FOREIGN KEY (`supplier_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`ordered_by`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed sample users for each level
-- Password for all users is 'password123' (hashed)
INSERT INTO `users` (`username`, `password`, `user_level`, `name`, `surname`, `email`, `number`) VALUES
('owner', '$2y$10$rLrcKGpANLXdy9frUIhP7u6b34P6eo2bbJA/2NfdjWMkS4OorEmOC', 'owner', 'Owner', 'User', 'owner@example.com', '09123456789'),
('manager', '$2y$10$rLrcKGpANLXdy9frUIhP7u6b34P6eo2bbJA/2NfdjWMkS4OorEmOC', 'manager', 'Manager', 'User', 'manager@example.com', '09123456780'),
('supplier', '$2y$10$rLrcKGpANLXdy9frUIhP7u6b34P6eo2bbJA/2NfdjWMkS4OorEmOC', 'supplier', 'Supplier', 'User', 'supplier@example.com', '09123456781'),
('employee', '$2y$10$rLrcKGpANLXdy9frUIhP7u6b34P6eo2bbJA/2NfdjWMkS4OorEmOC', 'employee', 'Employee', 'User', 'employee@example.com', '09123456782');

-- Seed sample clients
INSERT INTO `clients` (`client_name`, `client_email`, `client_address`, `client_contactnum`) VALUES
('John Doe', 'john@example.com', '123 Client Street, City', '09123456789'),
('Jane Smith', 'jane@example.com', '456 Customer Ave, Town', '09876543210'),
('Bob Johnson', 'bob@example.com', '789 Business Blvd, District', '09111222333');
