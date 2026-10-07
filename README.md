# Flask + Docker + MySQL + Jenkins CI/CD Project

A complete, 100% free CI/CD starter project demonstrating how to build, test, and deploy a containerized Python Flask web application connected to a MySQL database using Jenkins pipelines and Docker.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Jenkins Server (Docker)   |
                      |   http://localhost:8080     |
                      +--------------+--------------+
                                     |
               (CI/CD Pipeline: Build, Test, Deploy)
                                     v
+-------------------------------------------------------------------+
|                        Docker Compose Network                     |
|                                                                   |
|   +--------------------------+     +--------------------------+   |
|   |   Flask App Container    |     |     MySQL Container      |   |
|   |  http://localhost:5000   | <-> |       Port 3306          |   |
|   |        (app.py)          |     |    (Persistent Volume)   |   |
|   +--------------------------+     +--------------------------+   |
+-------------------------------------------------------------------+
```

---

## Project Structure

```
.
├── app.py                             # Flask application with MySQL CRUD operations
├── requirements.txt                   # Python dependencies (Flask, PyMySQL, PyTest)
├── test_app.py                        # Automated tests executed during CI pipeline
├── init.sql                           # Database initialization schema and seed data
├── Dockerfile                         # Container build instructions for Flask app
├── docker-compose.yml                 # Orchestrates Flask web app + MySQL containers
├── Jenkinsfile                        # Declarative Jenkins CI/CD pipeline
├── jenkins/
│   ├── Dockerfile                     # Jenkins LTS image with Docker CLI installed
│   └── docker-compose-jenkins.yml     # Compose file to run Jenkins with Docker socket mount
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Quick Start: Run App with Docker Compose

You can test the Flask + MySQL application directly before running Jenkins:

### 1. Start Flask and MySQL
```powershell
docker compose up -d --build
```

### 2. Verify Containers
```powershell
docker compose ps
```
Both `flask_mysql_db` (healthy) and `flask_web_app` should be running.

### 3. Open the App in Your Browser
- URL: **[http://localhost:5000](http://localhost:5000)**
- Health check endpoint: **[http://localhost:5000/health](http://localhost:5000/health)**

You can add, toggle, and delete tasks. All changes are stored in the MySQL database!

### 4. Stop the App
```powershell
docker compose down
```

---

## Setting Up Jenkins (Free & Local)

### 1. Launch Jenkins Container
Run Jenkins with Docker CLI access (mounting the Docker daemon socket):

```powershell
docker compose -f jenkins/docker-compose-jenkins.yml up -d --build
```

### 2. Get Jenkins Initial Admin Password
```powershell
docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword
```
Copy the 32-character password.

### 3. Complete Initial Setup
1. Open your browser and navigate to **[http://localhost:8080](http://localhost:8080)**.
2. Paste the administrator password.
3. Choose **Install suggested plugins**.
4. Create an admin user or proceed as admin.

---

## Creating the CI/CD Pipeline in Jenkins

1. On the Jenkins dashboard, click **New Item**.
2. Enter item name (e.g. `flask-mysql-pipeline`), choose **Pipeline**, and click **OK**.
3. Scroll to the **Pipeline** section:
   - **Option A (Local/Inline script)**: Set Definition to **Pipeline script** and copy-paste the contents of [`Jenkinsfile`](./Jenkinsfile).
   - **Option B (Git SCM)**: Set Definition to **Pipeline script from SCM**, choose **Git**, and provide your repository URL.
4. Click **Save**.
5. Click **Build Now** to trigger the pipeline!

### What the Pipeline Does:
1. **Lint & Sanity Check**: Verifies project structure and required files.
2. **Build Image**: Builds `flask-mysql-app` Docker image.
3. **Run Unit Tests**: Runs `pytest` inside the newly built Docker container.
4. **Deploy Containers**: Executes `docker compose up -d` to deploy Flask + MySQL.
5. **Health Check**: Validates that the application is reachable and running.

---

## Useful Docker Commands

```powershell
# View logs of the Flask app
docker logs -f flask_web_app

# View logs of the MySQL container
docker logs -f flask_mysql_db

# Connect to MySQL via CLI inside container
docker exec -it flask_mysql_db mysql -u appuser -papppassword taskdb

# Stop everything including Jenkins
docker compose down
docker compose -f jenkins/docker-compose-jenkins.yml down
```
