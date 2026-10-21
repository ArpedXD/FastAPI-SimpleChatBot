# SimpleChatBot

A small chat app that runs entirely on your own computer. You sign up, talk to a local AI model, and your conversations are saved and auto-titled.

**Stack:** FastAPI (API) · Ollama (AI model) · MySQL (storage) · plain HTML/CSS/JS (frontend)

This repo is the **backend**. The web pages live in a second repo, [SimpleChatBot](https://github.com/ArpedXD/SimpleChatBot). You need both.

---

## How the pieces fit

Think of a restaurant. Each part has one job, which is why they are separate programs.

- **Ollama is the chef.** It runs the AI model on your own machine, so every reply is cooked locally. That's why no API key or internet is needed after the download, and your chats never leave your computer.
- **FastAPI is the waiter.** The browser hands it an order (a request), it checks who is asking, carries the order to the chef or the filing cabinet, and brings the answer back. That's why the frontend never talks to Ollama or MySQL directly.
- **MySQL is the filing cabinet.** Four drawers hold users, chats, messages, and sessions, linked by ID numbers. It's there so your conversations survive a restart and the model can be shown earlier messages, which is how it remembers context.
- **The session cookie is a concert wristband.** After login the server hands your browser a random token, stored in the `Session` table, and the browser shows it on every request. That's how the API knows who you are without asking for your password each time.
- **CORS is the bouncer's guest list.** The API only lets in pages served from `http://127.0.0.1:5500`, so a browser blocks any other origin. That's why you must open the frontend at exactly that address, not `localhost` or a `file://` path.

```
 Browser  ──►  FastAPI  ──►  Ollama   (the AI model)
 :5500         :8000    └─►  MySQL    (users, chats, messages, sessions)
                              :3306
```

| Part | Default address |
|---|---|
| Frontend (static pages) | `http://127.0.0.1:5500` |
| FastAPI backend | `http://127.0.0.1:8000` |
| MySQL | `3306` |
| Ollama | `11434` |

---

## Prerequisites

- **Python 3.12+** (the Dockerfile uses 3.12)
- **Git**
- **MySQL Server**, plus a way to run SQL (MySQL Workbench or the `mysql` command line)
- **[Ollama](https://ollama.com/download)**
- A way to serve static files on port 5500: the VS Code **Live Server** extension, or Python's built-in server (shown below)

---

## Quick start

### 1. Get the code

Clone both repos side by side:

```bash
git clone https://github.com/ArpedXD/FastAPI-SimpleChatBot   # backend
git clone https://github.com/ArpedXD/SimpleChatBot           # frontend
```

### 2. Install Ollama and download a model

Install Ollama, then pull the default model (about 2 GB):

```bash
ollama pull llama3.2:3b
ollama list          # llama3.2:3b should appear here
```

Want a different model? Pull it, then set `MODEL` in `.env` (step 4) to the exact same name. The model writes both the replies and the chat titles.

Ollama must be running in the background. The desktop app starts it for you; otherwise run `ollama serve`.

### 3. Create the MySQL database

Run this in MySQL Workbench, or save it as `schema.sql` and run `mysql -u root -p < schema.sql`:

```sql
CREATE DATABASE IF NOT EXISTS userinfo;
USE userinfo;

CREATE TABLE IF NOT EXISTS users (
    UserID   INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    gmail    VARCHAR(50),
    password VARCHAR(50),
    age      INT
);

CREATE TABLE IF NOT EXISTS chats (
    UserID INT NOT NULL,
    chatID INT AUTO_INCREMENT PRIMARY KEY,
    title  TEXT,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

CREATE TABLE IF NOT EXISTS messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    chatID     INT NOT NULL,
    role       TEXT,
    content    TEXT,
    FOREIGN KEY (chatID) REFERENCES chats(chatID)
);

CREATE TABLE IF NOT EXISTS Session (
    UserID    INT NOT NULL,
    sessionID TEXT,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);
```

Check it worked: `SHOW TABLES;` should list `chats`, `messages`, `Session`, and `users`. Keep the table name exactly `Session` with a capital S.

### 4. Fill in `.env`

Open `.env` in the backend folder (next to `main.py`) and set every value:

| Variable | What it is | Example |
|---|---|---|
| `DB_HOST` | Where MySQL runs | `127.0.0.1` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_DATABASE` | Database name from step 3 | `userinfo` |
| `DB_USERNAME` | Your MySQL user | `root` |
| `DB_PASSWORD` | That user's password | `your-mysql-password` |
| `MODEL` | Ollama model used for chat and titles | `llama3.2:3b` |

> **Heads-up:** `.env` is tracked by Git in this repo (with blank values), so it will show as modified once you fill it in. Don't commit your real password. Run `git update-index --assume-unchanged .env` to keep it out of your commits.

### 5. Start the backend

```bash
cd FastAPI-SimpleChatBot
python -m venv .venv
```

Activate it (Windows: `.venv\Scripts\activate` · macOS/Linux: `source .venv/bin/activate`), then:

```bash
pip install -r requirements.txt
fastapi dev main.py
```

The repo contains a `venv/` folder. It was built on another machine, so ignore it and use your own `.venv`.

You should see `connecting to database..` followed by `ssuccess` (yes, two s's). Interactive API docs are at `http://127.0.0.1:8000/docs`.

If a MySQL error prints instead, the server still starts, but every request will fail. Fix `.env`, then restart.

### 6. Serve the frontend

In a second terminal, use either option:

- **VS Code Live Server:** open the `SimpleChatBot` folder, click **Go Live**, and confirm the address is `127.0.0.1:5500`.
- **Python:**
  ```bash
  cd SimpleChatBot
  python -m http.server 5500 --bind 127.0.0.1
  ```

Open **http://127.0.0.1:5500/index.html**. Sign up, switch to **Log In**, and you'll land on the chat dashboard. Your first message creates a new chat and the model names it.

### Every time after that

1. Make sure Ollama and MySQL are running.
2. `fastapi dev main.py` in the backend folder (with `.venv` active).
3. Serve the frontend on port 5500 and open `index.html`.

---

## API reference

| Method | Path | What it does |
|---|---|---|
| `POST` | `/account/signup` | Creates an account (`username`, `gmail`, `age`, `password`) and starts a session |
| `POST` | `/account/login` | Checks `username` and `password`, sets the `session_id` cookie |
| `GET` | `/account/profile` | Says whether the current cookie belongs to a logged-in user |
| `POST` | `/main/chat` | Sends `{question, new_chat, title}` and streams the reply as newline-separated JSON |
| `POST` | `/main/loadchat` | Takes `{title}` and returns that chat's messages |
| `GET` | `/main/loadhistory` | Returns the titles of your saved chats |
| `GET` | `/main/logout` | Asks the browser to delete the session cookie |

In the `/main/chat` stream, lines with `"titleSuccess": true` carry pieces of the new chat title, and lines with `"Success": true` carry pieces of the reply text.

---

## Project layout

```
FastAPI-SimpleChatBot/            (backend)
├── main.py               App setup: database connection, CORS, routers
├── acc_api.py            /account routes: signup, login, profile
├── chat_api.py           /main routes: chat, history, logout
├── Logic/
│   ├── acc_logic.py      Signup, login, session creation
│   ├── chat_logic.py     Talks to Ollama and streams the reply
│   ├── History_logic.py  Saves and loads chats in MySQL
│   ├── Profile.py        "Who does this cookie belong to?"
│   ├── ErrorHandling.py  Custom error types
│   └── tools.py          Database cursor and commit helpers
├── requirements.txt
├── Dockerfile            API only (not covered in this guide)
└── .env

SimpleChatBot/                    (frontend)
├── index.html            Sign up / log in page
├── dashboard.html        Chat page
├── Js/                   forms.js (auth), main.js (chat)
└── Css/                  main.css, form.css, dashboard.css
```

---

## Troubleshooting

| What you see | Why | Fix |
|---|---|---|
| CORS error in the browser console | The page isn't served from the one origin the API allows | Open exactly `http://127.0.0.1:5500` (not `localhost`, not `file://`) |
| Every request returns a 500 error | MySQL connection failed at startup | Check the `DB_*` values and that MySQL is running, then restart `fastapi dev` |
| "Failed to connect to Ollama" | Ollama isn't running | Open the Ollama app, or run `ollama serve` |
| `model "…" not found` | The model in `MODEL` was never downloaded | `ollama pull <model>`, and make sure `ollama list` shows the same name as `.env` |
| `Table 'userinfo.session' doesn't exist` | `History_logic.py` (lines 15 and 57) says `session` but the table is `Session`, and MySQL on Linux is case-sensitive | Change those two occurrences to `Session` |
| Login seems to work but you land back on the login page | The cookie is set as `Secure` and `SameSite=None` over plain HTTP | Use Chrome, Edge or Firefox, which generally accept it on `127.0.0.1`; Safari may not |
| Port 8000 or 5500 already in use | Another program has it | For 8000: `fastapi dev main.py --port 8001`, then update `url` at the top of `Js/forms.js` and `Js/main.js`. For 5500: change `allow_origins` in `main.py` to match |

---

## Known limitations

This is a learning project built for local use. Don't expose it to the internet as is.

- **Passwords are stored and compared as plain text.** Use throwaway passwords.
- **Sessions never expire.** Logout only clears the browser cookie; the row stays in the `Session` table.
- **One shared database connection** serves the whole app, so it isn't designed for many simultaneous users.
- **Chats are looked up by title** in some queries, without checking the user. Two users with identically titled chats could see mixed-up history.
- **Addresses are hard-coded** to `127.0.0.1` in the frontend and in the CORS setting.
