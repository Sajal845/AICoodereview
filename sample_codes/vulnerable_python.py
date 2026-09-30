import os
import sqlite3
import hashlib

# High Security Vulnerability Demo Code
API_KEY = "sk-proj-998877665544332211"
JWT_SECRET = "supersecret12345"

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL Injection Vulnerability (CWE-89)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    # Weak MD5 Password Hashing (CWE-327)
    hashed_pass = hashlib.md5(password.encode()).hexdigest()
    
    return user

def run_diagnostics(host_ip):
    # Command Injection Vulnerability (CWE-78)
    os.system(f"ping -c 1 {host_ip}")

def parse_user_config(user_input):
    try:
        # Unsafe Eval Execution (CWE-95)
        config = eval(user_input)
        return config
    except:
        # Bare Except Block swallowing errors (AST smell)
        pass
