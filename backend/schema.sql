CREATE DATABASE IF NOT EXISTS vehicle_damage;

USE vehicle_damage;

CREATE TABLE IF NOT EXISTS damage_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(255) NOT NULL,
    damage_result TEXT NOT NULL,
    cost_estimation VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
