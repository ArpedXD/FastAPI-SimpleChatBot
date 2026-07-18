from fastapi import APIRouter, Cookie
from pydantic import BaseModel
from Logic.acc_logic import Login, Signup
from Logic.Profile import Profile
from fastapi import Request

acc_router = APIRouter(prefix="/account")

class login_information(BaseModel):
    username : str
    password : str

class signup_information(BaseModel):
    username : str
    gmail : str
    age : int
    password : str
    
class Account_Logic:
    @acc_router.post("/login")
    def login(request : Request, login : login_information):
        return Login().account_login(request, login)
    
    @acc_router.post("/signup")
    def signup(request : Request, signup : signup_information):
        return Signup().account_signup(request, signup)
    

class ProfileLogic: # PlaceHolder, (Delete next time and add the parameters and return func to where you'll use it(you can still decide to not delete it for seperation))
    @acc_router.get("/profile")
    def profile(request: Request, session_id: str = Cookie(None)): # Confirmation of account existence, returns the name if user exist, None if not
        return Profile.profile_web(request, session_id)