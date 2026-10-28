import os
os.makedirs("data/target", exist_ok=True)

open("data/target/app.py", "w").write('''import sqlite3
import subprocess

API_KEY = "sk-live-1234567890abcdef"

def get_user(conn, username):
    query = "SELECT id, username FROM users WHERE username = '" + username + "'"
    return conn.execute(query).fetchall()

def ping_host(host):
    return subprocess.run("ping -c 1 " + host, shell=True, capture_output=True, text=True).stdout

def read_report(name):
    with open("reports/" + name) as f:
        return f.read()
''')

open("data/target/test_app.py", "w").write('''import sqlite3, inspect
import app

def make_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users(id INTEGER, username TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'alice'), (2, 'bob')")
    return conn

def test_get_user_normal():
    assert app.get_user(make_db(), "alice") == [(1, "alice")]

def test_get_user_injection_blocked():
    assert app.get_user(make_db(), "x' OR '1'='1") == []

def test_no_hardcoded_secret():
    assert "sk-live" not in inspect.getsource(app)

def test_no_shell_true():
    assert "shell=True" not in inspect.getsource(app)

def test_read_report_blocks_traversal():
    import pytest
    with pytest.raises(Exception):
        app.read_report("../../etc/passwd")
''')

open("data/owasp_notes.md", "w").write("""# OWASP notes (lab summary)
## A03 Injection - SQL
Never build SQL with string concatenation. Use parameterised queries, for example conn.execute("SELECT ... WHERE username = ?", (username,)).
## A03 Injection - OS command
Never pass user input to a shell. Use subprocess.run with a list of arguments and shell=False, and validate the input.
## A02 Cryptographic failures - hardcoded secrets
Never keep secrets in source code. Read them from environment variables, for example os.environ["API_KEY"].
## A01 Broken access control - path traversal
Never join user-supplied paths directly. Resolve the path and reject names that contain '..' or that escape the base directory.
""")
print("created data/target/app.py, test_app.py and data/owasp_notes.md")
