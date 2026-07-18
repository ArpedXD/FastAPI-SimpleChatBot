import ollama
from Logic.Profile import Profile
import json
from Logic.ErrorHandling import StreamingResponseError, AccountCantBefoundError
from fastapi.responses import JSONResponse, StreamingResponse
from Logic.History_logic import History
import re
from dotenv import load_dotenv
import os

load_dotenv()

class Chat:
    def __init__(self):
        self.ActSys = Profile


    def ollamachat(self, Prompt, request, session_id):
        try:
            if session_id is None:
                raise StreamingResponseError("Not Logged In")
            
            if self.ActSys.profile_backend(request, session_id) is None:
                raise AccountCantBefoundError("Cannot Find User")
        except StreamingResponseError as e:
            return JSONResponse(
                status_code=401,
                content={"message": str(e)}
            )
        except AccountCantBefoundError as e:
            return JSONResponse(
                status_code=401,
                content={"message": str(e)}
            )
        
        return StreamingResponse(self.generate_response(Prompt,request, session_id), media_type="text/plain")
        
    def generate_response(self, Prompt,request, session_id):
        history = History(request, session_id) # Creates a local class

        new_response = [{ # Blue print for the new response
            "role": "user",
            "content" : Prompt.question
        }]
        TitleVerification = history.titleCheck(Prompt.title) # returns title from the backend

        if TitleVerification is False: # if the title doesn't exist in the backemd, a title will be created 
            title_generation = ollama.chat(
                model=os.getenv("MODEL"),
                messages=[{
                    "role":"user",
                    "content": f"""
                        Create A File Title Name based on the user's prompt : {Prompt.question}

                            RULES: 
                            - One Line
                            - 4 words
                            - Be Creative and make it simple (AVOID dramatic names)
                            - No unnecessary text
                            """
                }],
                stream=True
            )
            
        else: # Load's all your chats
            ChatID = history.getChatID(TitleVerification) # self explanatory
            LoadedChats = history.loadchats(ChatID)
            new_response[:0] = LoadedChats
            pass

        ollama_chat = ollama.chat( # main chat
            model=os.getenv("MODEL"),
            messages=new_response,
            stream=True
        )

        # <-- Generate Response -->
        try:
            text = ""
            title = "" # Placeholder for title
            if not TitleVerification:
                for gen_title in title_generation:
                    gen_title["message"]["content"] = re.sub(r'[^a-zA-Z ]', '', gen_title["message"]["content"]) # REmove random stupid symbolsz
                    yield json.dumps({
                        "title" : gen_title["message"]["content"],
                        "titleSuccess": True
                    }) + "\n"
                    title += gen_title["message"]["content"]

            for chats in ollama_chat:
                yield json.dumps({
                    "text": chats["message"]["content"],
                    "Success": True
                }) + "\n"

                text += chats["message"]["content"]

            
            # Save Response
            history.savechats(Prompt, TitleVerification, title, text)
        finally:
            pass
    
    def newDiv(self, title, request, session_id):
        history = History(request, session_id);
        return history.loadChatHistory(title)

    def history(self, request, session_id):
        history = History(request, session_id)
        return history.loadHistory()
