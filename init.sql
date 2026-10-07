CREATE DATABASE IF NOT EXISTS taskdb;
USE taskdb;

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tasks (title, description, status) VALUES 
('Setup Jenkins', 'Install Jenkins via Docker and mount Docker socket', 'Completed'),
('Configure Pipeline', 'Run CI/CD pipeline using Jenkinsfile', 'In Progress'),
('Verify MySQL Integration', 'Confirm tasks are stored in MySQL container', 'Pending');
