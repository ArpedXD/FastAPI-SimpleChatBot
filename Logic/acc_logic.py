import json
import secrets
from fastapi import Response
from Logic.tools import Tools
from Logic.ErrorHandling import LoginError

class Account_System:
    def Session_creator(self, Account_Info, Message, request):
        cursor = Tools.cursorRequest(request)
        session_id = secrets.token_hex(32)
        cursor.execute("SELECT userID FROM users WHERE username = %s", (Account_Info.username,))

        result = cursor.fetchone()
        if not result:
            raise Exception("User not found after creation")
        user_id = result[0]

        cursor.execute("INSERT INTO Session (UserID, sessionID) VALUES (%s, %s)", (user_id, session_id))

        Tools.connectionCommit(request)

        value_to_return = json.dumps({
                "Message" : Message,
                "logged_in" : True
            })
        
        print("setCookied")
        response = Response(content=value_to_return)

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="none"
        )

        return response


class Login(Account_System):
    def __init__(self):
        self.AccountSys = Account_System()

    def account_login(self, request, login_info):
        cursor = Tools.cursorRequest(request)
        cursor.execute("SELECT username, password FROM users WHERE username = %s AND password = %s", (login_info.username, login_info.password))

        if cursor.fetchone():
            return self.AccountSys.Session_creator(login_info, "Successfully Logged in", request)
        else:
            return {"Message" : "Account not found"}

class Signup:
    def __init__(self):
        self.AccountSys = Account_System()
    
    def account_signup(self, request, signup_info):
        cursor = Tools.cursorRequest(request)

        cursor.execute("SELECT username FROM users WHERE username = %s", (signup_info.username,))
        if cursor.fetchone():
                return {"Message" : "Account Already Exists"}
        
        cursor.execute("SELECT gmail FROM users WHERE gmail = %s", (signup_info.gmail,))
        if cursor.fetchone():
                return {"Message" : "Mail Already Used"}
        

        cursor.execute("""
            INSERT INTO users(username, password, gmail, age) VALUES (%s,%s,%s,%s)
        """, (signup_info.username,signup_info.password,signup_info.gmail, signup_info.age))

        Tools.connectionCommit(request)
        cursor.close()
        return self.AccountSys.Session_creator(signup_info, "Successfully Signed Up", request)
