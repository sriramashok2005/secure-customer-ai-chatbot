\# Secure Customer AI Chatbot



A secure AI-powered chatbot that helps customers communicate with an application, manage invoice information, and search invoice content using AI.



\## Features



\- OTP-based customer authentication

\- JWT-based authentication for protected API endpoints

\- Customer conversation history

\- Customer-specific data access

\- Invoice creation and preview

\- Invoice text embeddings and semantic search

\- PostgreSQL database with SQLAlchemy

\- Vector search using pgvector

\- AI responses using Ollama

\- Invoice indexing status tracking

\- Automated tests for authentication, OTP security, and customer data isolation



\## Technology Stack



\- \*\*Language:\*\* Python 3.11

\- \*\*Backend:\*\* FastAPI

\- \*\*Database:\*\* PostgreSQL

\- \*\*ORM and Migrations:\*\* SQLAlchemy and Alembic

\- \*\*Vector Database Extension:\*\* pgvector

\- \*\*AI Model Runtime:\*\* Ollama

\- \*\*Testing:\*\* pytest



\## Project Structure



```text

AI CUSTOMER CHATBOT/

├── app/

│   ├── api/

│   │   ├── auth.py

│   │   ├── chat.py

│   │   └── invoices.py

│   ├── core/

│   ├── services/

│   ├── embedding\_service.py

│   ├── indexing\_service.py

│   ├── models.py

│   ├── schemas.py

│   └── search\_service.py

├── migrations/

│   └── versions/

├── tests/

├── main.py

├── alembic.ini

├── requirements.txt

├── start\_server.bat

└── .gitignore

```



\## Requirements



Before running the project, install or configure:



\- Python 3.11

\- PostgreSQL with the pgvector extension

\- Ollama with the required chat and embedding models

\- Git



\## Setup



\### 1. Clone the repository



```bash

git clone https://github.com/sriramashok2005/secure-customer-ai-chatbot.git

cd secure-customer-ai-chatbot

```



\### 2. Create a virtual environment



Windows PowerShell:



```powershell

py -3.11 -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

python -m pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a local `.env` file in the project root. Configure the database connection, JWT settings, Ollama URL, model names, and other required settings.



Use the variable names expected by the application. Never upload `.env` or real credentials to GitHub.



\### 5. Configure PostgreSQL



Create the project database, enable the pgvector extension, and ensure the database connection settings match your local `.env` configuration.



Run the migrations:



```powershell

python -m alembic upgrade head

```



\### 6. Configure Ollama



Install and start Ollama, then make sure the chat model and embedding model configured in `.env` are available.



\### 7. Start the application



```powershell

python -m uvicorn main:app --reload

```



Open the local API documentation at:



http://127.0.0.1:8000/docs



\## Testing



Run the automated tests using:



```powershell

python -m pytest -v

```



\*\*Latest verified test result:\*\* 12 tests passed.



The tests cover health checks, authentication requirements, customer data isolation, OTP expiration, OTP attempt limits, one-time OTP use, and resend cooldown behavior.



\## Security Notes



\- Protected endpoints require authentication.

\- Customer data access is restricted by ownership checks.

\- OTP verification includes expiration and attempt limits.

\- Environment files and development OTP files are excluded through `.gitignore`.

\- Keep database passwords, JWT secrets, and other credentials private.



\## API Overview



The application includes endpoints for:



\- Customer registration and OTP verification

\- Current customer information

\- Chat conversations and messages

\- Invoice preview and creation

\- Invoice reindexing

\- Application health checks



For the exact request and response formats, run the application and open `/docs`.



\## Repository



GitHub: https://github.com/sriramashok2005/secure-customer-ai-chatbot



\## Project Status



The core API, database migrations, invoice indexing flow, and automated tests have been implemented. Invoice indexing failures can be marked for retry; an automatic background retry worker is not currently included.



