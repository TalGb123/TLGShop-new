import sqlite3
import os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(current_dir, "..", "db.sqlite3")

db = sqlite3.connect(db_file)


@app.get("/")
async def display_message():
    cur = db.cursor()
    rows = cur.execute(
        f"""
            SELECT id, message_subject, message_content, username, date_time 
            FROM admin_messages
            ORDER BY date_time DESC
            LIMIT 10
        """
    ).fetchall()
    messages = []
    for id, subject, content, username, date_time in rows:
        messages.append(
            {
                "id": id,
                "username": username,
                "subject": subject,
                "content": content,
                "date_time": date_time,
            }
        )
    return messages


class InsertMessageReq(BaseModel):
    username: str
    subject: str
    content: str


@app.post("/insert")
async def insert_message(req: InsertMessageReq):
    cur = db.cursor()
    print(req.username, req.subject, req.content)
    cur.execute(
        f"INSERT INTO admin_messages (message_subject, message_content, username, date_time) VALUES (:subject, :content, :username, :date_time)",
        {
            "subject": req.subject,
            "content": req.content,
            "username": req.username,
            "date_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        },
    )


class UpdateMessageReq(BaseModel):
    id: int
    subject: str
    content: str


@app.post("/update")
async def update_message(req: UpdateMessageReq):
    cur = db.cursor()
    cur.execute(
        """
        UPDATE admin_messages 
        SET message_subject = :subject, message_content = :content
        WHERE id= :id
        """,
        {"subject": req.subject, "content": req.content, "id": req.id},
    )


class SearchMessageReq(BaseModel):
    id: int


@app.get("/search")
async def search_message(req: SearchMessageReq):
    cur = db.cursor()
    message = cur.execute(
        f"SELECT id, message_subject, message_content, username, date_time FROM admin_messages WHERE id= :id",
        {"id": req.id},
    ).fetchall()
    return message


@app.post("/delete")
async def delete_message(req: SearchMessageReq):
    cur = db.cursor()
    cur.execute(f"DELETE FROM admin_messages WHERE id= :id", {"id": req.id})
