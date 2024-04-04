import sqlite3

from fastapi import FastAPI

app = FastAPI()

db = sqlite3.connect("db.sqlite3")


@app.get("/")
async def root():
    cur = db.cursor()
    res = cur.execute("SELECT asdad FROM asdasd WHERE id = :id", {"id": 3})
    return {"message": "Hello World"}
