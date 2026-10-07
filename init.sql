CREATE DATABASE IF NOT EXISTS taskdb;
USE taskdb;

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calculations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    num1 DOUBLE NOT NULL,
    operation VARCHAR(10) NOT NULL,
    num2 DOUBLE NOT NULL,
    result DOUBLE NOT NULL,
    expression VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tasks (title, description, status) VALUES 
('Setup Jenkins', 'Install Jenkins via Docker and mount Docker socket', 'Completed'),
('Configure Pipeline', 'Run CI/CD pipeline using Jenkinsfile', 'In Progress'),
('Verify MySQL Integration', 'Confirm tasks are stored in MySQL container', 'Completed');

INSERT INTO calculations (num1, operation, num2, result, expression) VALUES
(100, '+', 250, 350, '100 + 250 = 350'),
(500, '*', 1.18, 590, '500 * 1.18 = 590 (18% GST/Tax)');
