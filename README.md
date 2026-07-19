bla bla blah pull this website : https://github.com/ArpedXD/SimpleChatBot

run it local

download ollama
download model ollama3.2:3b or just change the model in .env,

create a MYSQL database with this code then change everything in .env file: 

CREATE DATABASE IF NOT EXISTS userinfo;
use userinfo;

CREATE TABLE IF NOT EXISTS users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    gmail VARCHAR(50),
    password VARCHAR(50),
    age INT
);

CREATE TABLE IF NOT EXISTS chats(
	UserID int NOT NULL,
    chatID int AUTO_INCREMENT PRIMARY KEY,
	title TEXT,
    FOREIGN KEY (UserID)
		REFERENCES users(UserID)
);

CREATE TABLE IF NOT EXISTS messages(
	message_id INT auto_increment PRIMARY KEY,
    chatID int NOT NULL,
    role text,
    content text,
    foreign key (chatID)
		REFERENCES chats(chatID)
);

CREATE TABLE IF NOT EXISTS Session(
	UserID int NOT NULL,
    sessionID text,
    FOREIGN KEY (UserID)
		REFERENCES users(UserID)
);

select * from users;




run fastapi dev main.py then you're good 
