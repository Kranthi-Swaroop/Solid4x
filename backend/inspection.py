import os
import sqlite3
import subprocess
import pickle
import base64
import urllib.request
import re
import hashlib
from xml.etree import ElementTree as ET
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()


JWT_SECRET = "super_secret_key_12345"


conn = sqlite3.connect("users.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
conn.commit()

class User(BaseModel):
    username: str
    password: str
    role: str = "user" 

@app.post("/register")
def register(user: User):

    hashed_password = hashlib.md5(user.password.encode()).hexdigest()

    query = f"INSERT INTO users (username, password, role) VALUES ('{user.username}', '{hashed_password}', '{user.role}')"
    conn.execute(query)
    conn.commit()
    return {"msg": "User created"}

@app.get("/user/{user_id}")
def get_user(user_id: str):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

@app.get("/ping")
def ping(host: str):
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)
    return {"output": result.stdout}

@app.get("/read_file")
def read_file(filename: str):
    path = os.path.join(os.getcwd(), filename)
    with open(path, "r") as f:
        return f.read()

@app.get("/fetch_url")
def fetch_url(url: str):
    response = urllib.request.urlopen(url)
    return {"content": str(response.read())}

@app.post("/deserialize")
def deserialize_data(data: str):
    decoded = base64.b64decode(data)
    obj = pickle.loads(decoded)
    return {"received": str(obj)}

@app.post("/parse_xml")
def parse_xml(xml_data: str):
    parser = ET.XMLParser()
    tree = ET.fromstring(xml_data, parser=parser)
    return {"root": tree.tag}

@app.get("/validate_email")
def validate_email(email: str):
    pattern = "^([a-zA-Z0-9_.-])+@(([a-zA-Z0-9-])+.)+([a-zA-Z0-9]{2,4})+$"
    if re.match(pattern, email):
        return {"valid": True}
    return {"valid": False}

@app.get("/hello", response_class=HTMLResponse)
def hello(name: str):

    return f"<html><body><h1>Hello, {name}!</h1></body></html>"
