import json
from Logic.ErrorHandling import AccountCantBefoundError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from Logic.tools import Tools
class Profile:
    def profile_web(request, session_id): # To check if user is already logged in via the website
        cursor = Tools.cursorRequest(request)
        cursor.execute("SELECT UserID FROM Session WHERE sessionID = %s", (session_id,))

        ses = cursor.fetchone()
        if not ses:
            return {
                    "message": "is not logged in",
                    "Username": "None",
                    "logged_in": False
                }
        cursor.execute("SELECT username FROM users where UserId = %s", ses)
        username = cursor.fetchone()

        if None in (ses, username):
            return {
                    "message": "is not logged in",
                    "Username": "None",
                    "logged_in": False
                }
        
        return {
            "message": "Account found",
            "Username": username,
            "logged_in": True
        }
    
    def profile_backend(request, session_id): # To check if user is logged in via class, returns None if not logged in
        cursor = Tools.cursorRequest(request)
        cursor.execute("SELECT UserID FROM Session where sessionID = %s", (session_id,))
        userid = cursor.fetchone()

        cursor.execute("SELECT username from users where userID = %s", userid)
        username = cursor.fetchone()
        if None in (username, userid):
            return None
        return username
        