import sqlite3, inspect
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
