from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from chat_api import chat_router
from acc_api import acc_router
import mysql.connector
import os 
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("connecting to database..")

    try:
        app.state.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
            user = os.getenv("DB_USERNAME"),
            password = os.getenv("DB_PASSWORD")
        )

        if app.state.db.is_connected():
            print("success")
            
    except mysql.connector.Error as e:
        print(e)

    yield

    app.state.db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://arpedxd.github.io", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(acc_router)
app.include_router(chat_router)

# run through 'fastapi dev main.py'