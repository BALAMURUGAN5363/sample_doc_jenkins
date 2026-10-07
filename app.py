import os
import time
import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Database configuration from environment variables
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "appuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "apppassword")
DB_NAME = os.environ.get("DB_NAME", "taskdb")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))

def get_db_connection(max_retries=5, delay=3):
    """Establishes connection to MySQL with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                cursorclass=DictCursor,
                autocommit=True
            )
            return connection
        except pymysql.MySQLError as err:
            app.logger.warning(f"Connection attempt {attempt}/{max_retries} failed: {err}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                raise

def perform_calculation(num1, op, num2):
    """
    Pure business logic for mathematical calculations.
    Returns (result, expression_string).
    Raises ValueError on invalid operations or ZeroDivisionError.
    """
    try:
        num1 = float(num1)
        num2 = float(num2)
    except (ValueError, TypeError):
        raise ValueError("Inputs num1 and num2 must be valid numbers")

    if op == "+":
        res = num1 + num2
    elif op == "-":
        res = num1 - num2
    elif op == "*":
        res = num1 * num2
    elif op == "/":
        if num2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        res = num1 / num2
    elif op == "%":
        if num2 == 0:
            raise ZeroDivisionError("Cannot compute modulo with zero")
        res = num1 % num2
    elif op in ("^", "**"):
        res = num1 ** num2
    else:
        raise ValueError(f"Unsupported operation: {op}. Supported: +, -, *, /, %, ^")

    # Round result to 4 decimal places for clean display
    res = round(res, 4)
    # If whole number, format without .0
    if res.is_integer():
        res = int(res)

    expression = f"{num1} {op} {num2} = {res}"
    return res, expression

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if title:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO tasks (title, description, status) VALUES (%s, %s, 'Pending')"
                    cursor.execute(sql, (title, description))
            finally:
                conn.close()
            return redirect(url_for("index"))

    # Fetch tasks and calculation history
    tasks = []
    calculations = []
    db_connected = False
    try:
        conn = get_db_connection(max_retries=2, delay=1)
        with conn.cursor() as cursor:
            # Auto-create calculations table if it doesn't exist yet
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    num1 DOUBLE NOT NULL,
                    operation VARCHAR(10) NOT NULL,
                    num2 DOUBLE NOT NULL,
                    result DOUBLE NOT NULL,
                    expression VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
            tasks = cursor.fetchall()
            cursor.execute("SELECT * FROM calculations ORDER BY id DESC LIMIT 10")
            calculations = cursor.fetchall()
        conn.close()
        db_connected = True
    except Exception as e:
        app.logger.error(f"Database query error: {e}")

    return render_template("index.html", tasks=tasks, calculations=calculations, db_connected=db_connected)

@app.route("/calculate", methods=["POST"])
def calculate():
    """Handles calculator form submission from the web UI."""
    num1 = request.form.get("num1")
    op = request.form.get("op", "+")
    num2 = request.form.get("num2")

    try:
        result, expression = perform_calculation(num1, op, num2)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO calculations (num1, operation, num2, result, expression) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (float(num1), op, float(num2), float(result), expression))
        finally:
            conn.close()
    except Exception as e:
        app.logger.error(f"Calculation failed: {e}")

    return redirect(url_for("index"))

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """JSON API endpoint for calculation tests and integrations."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON payload"}), 400

    num1 = data.get("num1")
    op = data.get("op")
    num2 = data.get("num2")

    if num1 is None or op is None or num2 is None:
        return jsonify({"success": False, "error": "Missing required fields: num1, op, num2"}), 400

    try:
        result, expression = perform_calculation(num1, op, num2)
    except ZeroDivisionError as zde:
        return jsonify({"success": False, "error": str(zde)}), 400
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400

    # Save to database if accessible
    try:
        conn = get_db_connection(max_retries=1, delay=0)
        with conn.cursor() as cursor:
            sql = "INSERT INTO calculations (num1, operation, num2, result, expression) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (float(num1), op, float(num2), float(result), expression))
        conn.close()
    except Exception as db_err:
        app.logger.warning(f"Could not persist calculation to DB: {db_err}")

    return jsonify({
        "success": True,
        "num1": num1,
        "operation": op,
        "num2": num2,
        "result": result,
        "expression": expression
    }), 200

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()
            if task:
                new_status = "Completed" if task["status"] != "Completed" else "Pending"
                cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
    finally:
        conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    finally:
        conn.close()
    return redirect(url_for("index"))

@app.route("/health")
def health():
    """Health check endpoint for Jenkins CI/CD tests and container monitors."""
    try:
        conn = get_db_connection(max_retries=1, delay=0)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS check_status")
            result = cursor.fetchone()
        conn.close()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "result": result["check_status"]
        }), 200
    except Exception as err:
        return jsonify({
            "status": "degraded",
            "database": f"error: {str(err)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
