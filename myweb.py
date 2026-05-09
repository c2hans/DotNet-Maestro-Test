from flask import Flask, request, render_template_string, redirect
import sqlite3
import os

app = Flask(__name__)

# --- Setup database ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'secret123')")
    c.execute("INSERT INTO users (username, password) VALUES ('user', 'password')")
    conn.commit()
    conn.close()

init_db()

# --- Home ---
@app.route("/")
def home():
    return """
    <h1>Vulnerable CTF App</h1>
    <ul>
        <li>/login</li>
        <li>/search?user=</li>
        <li>/template?name=</li>
        <li>/read?file=</li>
    </ul>
    """

# --- SQL Injection ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        # 🚨 VULNERABLE: SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = c.execute(query).fetchone()

        conn.close()

        if result:
            return f"Welcome {username}!"
        else:
            return "Login failed!"

    return """
    <form method="POST">
        Username: <input name="username"><br>
        Password: <input name="password"><br>
        <input type="submit">
    </form>
    """

# --- SQL Injection (search endpoint) ---
@app.route("/search")
def search():
    user = request.args.get("user", "")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # 🚨 VULNERABLE: SQL Injection
    query = f"SELECT username FROM users WHERE username LIKE '%{user}%'"
    results = c.execute(query).fetchall()

    conn.close()

    return "<br>".join([r[0] for r in results])

# --- SSTI ---
@app.route("/template")
def template():
    name = request.args.get("name", "Guest")

    # 🚨 VULNERABLE: Server-Side Template Injection
    template = f"Hello {name}!"
    return render_template_string(template)

# --- Path Traversal ---
@app.route("/read")
def read_file():
    filename = request.args.get("file", "")

    # 🚨 VULNERABLE: No sanitization
    try:
        with open(filename, "r") as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
