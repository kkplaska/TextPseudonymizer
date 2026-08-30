<div align="center">
  <h1>TextPseudonymizer 🕵️‍♂️</h1>
  <p><strong>A stateless, zero-data-retention web application for text pseudonymization and restoration.</strong></p>
</div>

## 📌 Overview

**TextPseudonymizer** is a lightweight, highly secure web application designed to anonymize sensitive text data (e.g., names, personal identifiers, internal code words) by replacing them with collision-proof random tokens (`<[ANON_XXXX]>`). 

**Primary Motivation:** This tool was specifically created to sanitize and prepare sensitive texts so that they can be safely passed to and processed by AI models (like ChatGPT, Claude, or Gemini) without exposing confidential data. Once the AI returns the processed text, you can use the generated dictionary to perfectly restore the original sensitive strings locally.

It works entirely **in-memory**. No text, dictionaries, or logs are ever saved to a database or written to disk. The tool provides a two-way process:
1. **Pseudonymization:** Replace specific phrases in a text with random tokens, generating a JSON dictionary mapping.
2. **Restoration (Deanonymization):** Use the generated JSON dictionary to restore the original text.

### ✨ Key Features
- **Zero Data Retention:** 100% stateless backend processing.
- **Robust Text Processing:** Safely handles Regex special characters and complex Unicode (e.g., Polish diacritics).
- **Smart Case-Insensitivity:** Automatically detects different casing of the same word (e.g., `word`, `Word`, `WORD`) and maps them uniquely.
- **Modern Dark UI:** Beautiful, responsive interface built with Tailwind CSS.
- **Client-Side Persistence:** Remembers your phrases and last generated dictionary in your browser's local storage (so you don't lose data on accidental refresh).
- **Bilingual Support:** Built-in i18n (English / Polish) with preference saved in cookies.

---

## 🛠️ Architecture & Technologies

The application follows a simple but robust Client-Server architecture, packaged via Docker for instant deployment.

**Backend (Python / FastAPI):**
- **[FastAPI](https://fastapi.tiangolo.com/):** High-performance asynchronous web framework. Handles routing and exception management.
- **[Pydantic v2](https://docs.pydantic.dev/):** Enforces strict validation on incoming JSON payloads.
- **`re` & `secrets`:** The core NLP engine relies on Python's built-in libraries to compile dynamic, boundary-aware Regular Expressions (`re.UNICODE | re.IGNORECASE`) and cryptographically secure token generation (`secrets`).

**Frontend (Vanilla Web):**
- **HTML5 & Vanilla JS:** A lightning-fast Single Page Application (SPA) with zero npm dependencies. Uses the native `fetch` API.
- **[Tailwind CSS](https://tailwindcss.com/):** Injected via CDN for rapid, modern Dark Mode styling.
- **`localStorage` & Cookies:** Used strictly on the client-side to persist the user's phrase list and UI preferences across sessions.

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose (Recommended)
- *OR* Python 3.11+ (if running locally)

### Option A: Running with Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/PhantomText.git
   cd PhantomText
   ```

2. **Build and start the container:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8000`.

### Option B: Running Locally (Without Docker)

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies and build Tailwind CSS:**
   *(Requires Node.js installed)*
   ```bash
   npm install
   npm run build:css
   ```

4. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## ⚙️ Configuration

The application can be configured via environment variables.

### Environment Variables
| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | The port the FastAPI server listens on. |
| `MAX_TEXT_LENGTH` | `1000000` | Maximum allowed characters in the source text payload. Protects against resource exhaustion. |
| `MAX_WORDS_COUNT` | `1000` | Maximum allowed phrases in the dictionary. |

### Changing settings with Docker Compose
Edit the `docker-compose.yml` file to modify ports or limits. For example:
```yaml
ports:
  - "8080:8000"
environment:
  - PORT=8000
  - MAX_TEXT_LENGTH=2000000
  - MAX_WORDS_COUNT=500
```

**Using Environment Variables:**
The `Dockerfile` is configured to respect the `$PORT` environment variable. 
```bash
docker run -e PORT=5000 -p 5000:5000 text-pseudonymizer
```

---

## 🔒 Security Considerations for Production

### Is the REST API inherently secure?
Yes, from an application logic standpoint. The API uses strict Pydantic schemas to validate data, escapes all regular expression inputs to prevent ReDoS (Regex Denial of Service), and strictly processes everything in RAM without logging payloads.

### Network Sniffing & Interception
By default, the Docker container exposes the application over standard unencrypted **HTTP**. 
- If you run this on `localhost` for personal use, the traffic never leaves your machine and cannot be intercepted by external network sniffers (e.g., Wireshark).
- **WARNING**: If you expose this application to a public network or the internet, **all text and JSON dictionaries are transmitted in plain text**. Anyone on the network path can intercept your data.

### Securing the Deployment
To safely expose this application over a network, you **MUST** place it behind a Reverse Proxy that terminates SSL/TLS (providing HTTPS). 

1. **Do not** expose the Docker port directly to the internet.
2. Use a reverse proxy like **Nginx**, **Caddy**, or **Traefik**.
3. Configure the proxy with an SSL/TLS certificate (e.g., via Let's Encrypt).
4. Route the encrypted HTTPS traffic from your proxy to the internal Docker container port.
