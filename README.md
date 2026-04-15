# Clara — LEAD College Admissions FAQ Chatbot

Clara is an AI-powered admissions assistant for **LEAD College (Autonomous), Palakkad, Kerala**. Built with Python and Flask, it uses a Large Language Model (LLM) via OpenAI-compatible API to answer prospective students' questions about MBA and MCA programs — including fees, eligibility, facilities, hostel, and the application process.

---

## Preview

Clara features a clean, responsive two-panel chat UI — a sidebar with college info and a main chat window with quick-action buttons for common queries.

---

## Features

- **Conversational AI** — Powered by LLM (Meta LLaMA 3 via OpenAI-compatible endpoint) with a custom system prompt that defines Clara's identity, tone, and domain knowledge
- **Live Website Scraping** — Automatically fetches and parses content from [lead.ac.in](https://lead.ac.in/) to supplement answers with real-time data
- **Smart Caching** — Website data is cached for 24 hours to minimize redundant requests; a manual `/api/website-sync` endpoint allows forced refresh
- **Conversation History** — Maintains the last 15 messages in context for coherent multi-turn conversations
- **Quick Action Buttons** — Pre-built buttons for the most common queries (MBA, MCA, fees, eligibility, hostel, contact, etc.)
- **Prompt Engineering** — Carefully crafted system prompt with formatting rules, persona definition, domain-specific knowledge, and hallucination mitigation
- **Responsive UI** — Works on desktop, tablet, and mobile with clean layout adaptation

---

## Project Structure

```
faq-chatbot/
├── app.py               # Flask backend — API routes, LLM calls, web scraping, caching
├── home.html            # Frontend — chat UI (single-file HTML/CSS/JS)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API key, base URL) — not committed
├── .gitignore           # Ignores .env, venv, __pycache__, etc.
├── static/              # Static assets (if any)
├── templates/           # HTML templates folder
└── venv/                # Virtual environment (not committed)
```

---

## How It Works

```
User Message
     │
     ▼
Flask /api/chat endpoint
     │
     ├── Check message for keywords (admission, fee, hostel, etc.)
     │        │
     │        ▼
     │   Fetch lead.ac.in content (cached 24h)
     │   Inject as website context into system prompt
     │
     ▼
Build messages array:
  [system prompt + website context] + [last 15 history messages] + [user message]
     │
     ▼
LLM API Call (meta-llama/llama-3-8b-instruct via OpenRouter)
     │
     ▼
Return reply → Frontend renders in chat bubble
```

---

## Tech Stack

| Layer        | Technology                                      |
| ------------ | ----------------------------------------------- |
| Backend      | Python 3, Flask                                 |
| LLM API      | OpenAI-compatible API (OpenRouter — LLaMA 3 8B) |
| Web Scraping | requests, BeautifulSoup4                        |
| Frontend     | Vanilla HTML, CSS, JavaScript (single file)     |
| Config       | python-dotenv                                   |

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/faq-chatbot.git
cd faq-chatbot
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
FLASK_ENV=development
```

> **Note:** Clara uses [OpenRouter](https://openrouter.ai/) as the API gateway to access LLaMA 3. You can swap this for any OpenAI-compatible endpoint by changing `OPENAI_BASE_URL`.

### 5. Run the application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## API Endpoints

| Method | Endpoint              | Description                                          |
| ------ | --------------------- | ---------------------------------------------------- |
| `GET`  | `/`                   | Serves the chat UI (`home.html`)                     |
| `POST` | `/api/chat`           | Main chat endpoint — accepts `message` and `history` |
| `POST` | `/api/website-sync`   | Manually refresh the lead.ac.in website cache        |
| `GET`  | `/api/website-status` | Check cache status and last fetch time               |
| `GET`  | `/health`             | Health check — returns service status                |

### `/api/chat` Request Format

```json
{
  "message": "What is the MCA fee structure?",
  "history": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello! I'm Clara..." }
  ]
}
```

### `/api/chat` Response Format

```json
{
  "reply": "The MCA program fee for 2025-27 is ₹5,40,000 total..."
}
```

---

## Environment Variables

| Variable          | Required | Description                               |
| ----------------- | -------- | ----------------------------------------- |
| `OPENAI_API_KEY`  | ✅ Yes   | Your LLM API key                          |
| `OPENAI_BASE_URL` | ✅ Yes   | API base URL (OpenRouter or OpenAI)       |
| `FLASK_ENV`       | Optional | Set to `development` to enable debug mode |
| `PORT`            | Optional | Port to run on (default: `5000`)          |

---

## Prompt Engineering Highlights

Clara's system prompt is designed with the following strategies:

- **Persona definition** — Name, role, institution, and personality explicitly defined
- **Domain knowledge injection** — Full fee structures, eligibility, contacts, and application steps hardcoded as ground truth
- **Formatting rules** — Instructed to avoid markdown asterisks and use clean symbols (`•`, `✅`, emojis) for readable plain-text output
- **Hallucination mitigation** — Instructed to direct users to the admissions office or website when information is unavailable
- **Live context injection** — Website scraped content appended to system prompt dynamically when relevant keywords are detected in the user query

---

## Dependencies

```
openai
flask
python-dotenv
requests
beautifulsoup4
```

Install all with:

```bash
pip install -r requirements.txt
```

---

## Caching Behaviour

- On startup, Clara automatically fetches content from `https://lead.ac.in/`
- Cached data expires after **24 hours**
- Cache is used only when the user's query contains relevant keywords (`admission`, `fee`, `hostel`, `placement`, etc.)
- Force a manual refresh via `POST /api/website-sync`

---

## Responsive Design

| Screen                | Behaviour                                        |
| --------------------- | ------------------------------------------------ |
| Desktop (>1024px)     | Full two-panel layout with sidebar               |
| Tablet (768–1024px)   | Condensed two-panel layout                       |
| Mobile (<768px)       | Sidebar hidden; full-width chat view             |
| Small mobile (<480px) | Compact padding, larger input font for usability |

---

## Known Limitations & Future Improvements

- [ ] Add vector database (FAISS/Pinecone) for semantic search over college documents
- [ ] Integrate PDF document ingestion (prospectus, brochures) for richer answers
- [ ] Add streaming responses for faster perceived reply time
- [ ] Implement rate limiting per IP to prevent API abuse
- [ ] Add multilingual support (Malayalam, Hindi)
- [ ] Deploy to cloud (Railway / Render / AWS)

---

## Author

**Nandhana P Suresh**
MCA Student — LEAD College (Autonomous), Palakkad
[LinkedIn](https://linkedin.com/in/nandhana-p-suresh) • nandhanapsuresh75@gmail.com

---

## License

This project is for educational purposes. All college data belongs to LEAD College (Autonomous), Palakkad.
