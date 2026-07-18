from fastapi import  APIRouter, Cookie
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from Logic.chat_logic import Chat
from Logic.ErrorHandling import StreamingResponseError
from fastapi import Request
from fastapi.responses import Response

chat_router = APIRouter(prefix="/main")

chats = Chat()
class prompt(BaseModel):
    question : str
    new_chat: bool
    title: str

class Title(BaseModel):
    title : str
    
@chat_router.post("/chat")
async def chat(Prompt: prompt, request: Request, session_id : str = Cookie(None)):
    return chats.ollamachat(Prompt, request, session_id)

@chat_router.post("/loadchat")
async def load(title : Title, request: Request, session_id : str = Cookie(None)):
    return chats.newDiv(title, request, session_id)

@chat_router.get("/loadhistory")
async def History(request: Request, session_id : str = Cookie(None)):
    return chats.history(request, session_id)

@chat_router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_id")