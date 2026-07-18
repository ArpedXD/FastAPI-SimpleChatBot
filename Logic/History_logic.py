import json
from Logic.Profile import Profile
from Logic.ErrorHandling import MissingHistory
from Logic.tools import Tools

class History:
    def __init__(self, request,session_id):
        self.request = request
        self.ActSys = Profile
        self.cursor = Tools.cursorRequest(request)
        self.session_id = session_id
    
    def titleCheck(self, title):
        cursor = self.cursor
        cursor.execute("SELECT userID from session WHERE sessionID = %s", (self.session_id,)) # pull userID using session
        ses = cursor.fetchone()
        
        cursor.execute("SELECT title FROM chats WHERE title = %s AND UserID = %s", (title, ses[0])) # pull title using userID

        res = cursor.fetchone()
        if None in (ses, res):
            return False
        else:
            return res[0] # returns the title again after verifying its existence to the database

    def getChatID(self, TitleVerification): # gets chatID usign title
        cursor = self.cursor
        cursor.execute("SELECT chatID FROM chats WHERE title = %s", (TitleVerification,))
        res = cursor.fetchone()

        return res[0]
    
    def getUserID(self):
        cursor = self.cursor
        cursor.execute("SELECT UserID from Session WHERE sessionID = %s", (self.session_id,))
        res = cursor.fetchone()

        if res is None:
            return None
        return res[0]
        
    def loadchats(self, ChatID):
        cursor = self.cursor
        cursor.execute("SELECT role, content FROM messages WHERE chatID = %s", (ChatID,))

        JSONPLACEHOLDER = [] # THIS IS WHERE YOU'LL ADD THE CHATS AND RETURN IT
        for load in cursor.fetchall():
            JSONPLACEHOLDER.append({
                "role" : load[0],
                "content" : load[1]
            })
        return JSONPLACEHOLDER

    def savechats(self, Prompt, TitleVerification, title, text):
        cursor = self.cursor
        if TitleVerification is False: # saves title if it doesn't exist in DB
            cursor.execute("SELECT userID from session WHERE sessionID = %s", (self.session_id,))
            userID = cursor.fetchone()

            cursor.execute("INSERT INTO chats(title, UserID) VALUES (%s, %s)", (title, userID[0]))
            Tools.connectionCommit(self.request)

            # Get the chatID of the newly inserted chat
            cursor.execute("SELECT LAST_INSERT_ID()")
            chatID = cursor.fetchone()[0]
        else:
            # Get chatID using the existing title
            cursor.execute("SELECT chatID FROM chats WHERE title = %s", (TitleVerification,))
            chatID = cursor.fetchone()[0]

        cursor.execute("INSERT INTO messages(chatID, role, content) VALUES (%s,%s,%s)", (chatID, "user", Prompt.question))
        cursor.execute("INSERT INTO messages(chatID, role, content) VALUES (%s,%s,%s)", (chatID, "assistant", text))
        Tools.connectionCommit(self.request)
        return

    def loadChatHistory(self, title):
        userID = self.getUserID()
        cursor = self.cursor
        cursor.execute("SELECT chatID FROM chats WHERE UserID = %s AND title = %s", (userID,title.title))

        # Load ALL messages into memory first to avoid MySQL timeout during streaming
        all_messages = []
        for each in cursor.fetchall():
            cursor.execute("SELECT role, content FROM messages WHERE chatID = %s", (each[0],))
            print("hi")
            for values in cursor.fetchall():
                print(values[0], " + ", values[1])
                all_messages.append({
                    "role": values[0],
                    "content": values[1]
                })
            print("----------------")
        print(all_messages)
        # Yield all messages after loading is complete
        return all_messages
    
    def loadHistory(self):
        userID = self.getUserID()
        cursor = self.cursor
        cursor.execute("SELECT title FROM chats WHERE userID = %s", (userID,))

        all_titles = []
        for each in cursor.fetchall():
            print(each[0])
            all_titles.append(each[0])

        return all_titles