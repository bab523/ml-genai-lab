import sqlite3
import subprocess
import os

def get_user(conn, username):
    query = "SELECT id, username FROM users WHERE username = ?"
    return conn.execute(query, (username,)).fetchall()

def ping_host(host):
    return subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True).stdout

def read_report(name):
    # Resolve the path and reject names that contain '..' or that escape the base directory.
    if '..' in name or name.startswith('.'):
        raise ValueError("Invalid report name")
    report_path = "reports/" + name
    return open(report_path).read()

def main():
    # Read secrets from environment variables
    global API_KEY
    API_KEY = os.environ.get("API_KEY")

    # Connect to the database
    conn = sqlite3.connect("database.db")
    try:
        # Get user
        username = input("Enter username: ")
        users = get_user(conn, username)
        for user in users:
            print(f"Username: {user[1]}")

        # Ping host
        host = input("Enter host: ")
        ping_result = ping_host(host)
        print(ping_result)

        # Read report
        name = input("Enter report name: ")
        report = read_report(name)
        print(report)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
