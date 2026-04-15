# app.py
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory
from typing import List, Dict
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# client = OpenAI(api_key=api_key)
client = OpenAI(
    api_key=api_key,
    base_url=os.getenv("OPENAI_BASE_URL")
)

# College website URL
COLLEGE_WEBSITE = "https://lead.ac.in/"

# Cache for website data
website_cache = {
    "data": None,
    "timestamp": None,
    "expires_in": 86400  # 24 hours
}


def fetch_website_data(url):
    """Fetch and parse college website data"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)

        # Extract key sections (programs, admissions, contact)
        relevant_sections = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in
                   ['program', 'admission', 'fee', 'eligibility', 'contact',
                    'mca', 'mba', 'facility', 'placement', 'hostel']):
                # Get context around keyword
                start = max(0, i - 2)
                end = min(len(lines), i + 5)
                relevant_sections.extend(lines[start:end])

        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.text.strip()
            if link_text and len(link_text) > 2:
                links.append({
                    'text': link_text,
                    'url': href
                })

        return {
            'content': '\n'.join(relevant_sections[:3000]),  # Relevant content
            'all_text': text[:2000],  # Fallback full text
            'links': links[:15],
            'title': soup.title.string if soup.title else 'LEAD College',
            'fetched_at': datetime.now().isoformat()
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website: {e}")
        return None


def get_cached_website_data():
    """Get website data from cache or fetch fresh"""
    current_time = datetime.now()

    # Check if cache is valid
    if (website_cache["data"] and
        website_cache["timestamp"] and
            (current_time - website_cache["timestamp"]).total_seconds() < website_cache["expires_in"]):
        print("✓ Using cached website data")
        return website_cache["data"]

    # Fetch fresh data
    print("📡 Fetching fresh website data from lead.ac.in...")
    data = fetch_website_data(COLLEGE_WEBSITE)

    if data:
        website_cache["data"] = data
        website_cache["timestamp"] = current_time
        print("✓ Website data cached successfully")
    else:
        print("⚠ Failed to fetch website data")

    return data


SYSTEM_PROMPT = """You are Clara, the official admissions assistant for LEAD College (Autonomous), Palakkad, Kerala, India.

YOUR IDENTITY:
- Name: Clara
- Role: Admissions Assistant
- Institution: LEAD College (Autonomous), Palakkad
- Personality: Helpful, friendly, and professional
- Website: https://lead.ac.in/

COLLEGE INFORMATION:
- Name: LEAD College (Autonomous)
- Location: Dhoni, Palakkad, Kerala - 678009
- Status: Autonomous institution
- Programs: MBA, MCA
- Website: https://lead.ac.in/

MBA PROGRAM:
- Duration: 2 years
- Eligibility: Bachelor's degree (any discipline) with 50% marks
- Entrance: CAT/MAT/CMAT/KMAT or LEAD entrance exam
- Specializations: Finance, Marketing, HR, Operations
- Seats: 60
- Total Fee: ₹8,00,000 for 2 years (₹4,00,000 per year)

MCA PROGRAM (2025-27):
- Duration: 2 years
- Eligibility: Bachelor's degree in Computer Science/IT/BCA or B.Sc with Mathematics
- Minimum: 50% marks in qualifying exam
- Entrance: KMAT/LEAD entrance exam
- Seats: 120

MCA FEE STRUCTURE (2025-27):
Total Program Fee: ₹5,40,000 for 2 years

Semester-wise breakdown:
- Semester 1: ₹1,65,000
- Semester 2: ₹1,25,000
- Semester 3: ₹1,25,000
- Semester 4: ₹1,25,000

Major Fee Components:
- Tuition Fees: ₹1,00,000 (total for 2 years)
- Admission Fees: ₹40,000 (one-time payment)
- Hostel & Mess Fees: ₹2,16,000 (₹27,000 per semester x 4)
- Training & Development: ₹35,000 (total)
- Books, Uniform & Others: ₹49,000 (total)

IMPORTANT NOTES:
- All fees include hostel and mess charges
- Educational loan facility available
- Payment via RTGS/NEFT/Cheque to Federal Bank, Palakkad
- Account No: 10810200162210
- IFSC: FDRL0001081

FACILITIES:
- Digital library with 10,000+ e-books
- Modern computer labs
- Hostel facilities (separate for boys/girls)
- Sports complex
- Wi-Fi enabled campus
- Cafeteria
- Placement cell

APPLICATION PROCESS:
1. Visit LEAD college website: https://lead.ac.in/
2. Fill online application form
3. Upload required documents
4. Pay application fee (₹500)
5. Submit and wait for entrance exam date

DOCUMENTS REQUIRED:
- 10th & 12th mark sheets
- Degree certificate & mark sheets
- Entrance exam score card
- Passport size photos
- ID proof (Aadhaar/PAN)

CONTACT:
- Phone: +91-4923-XXXXXX
- Email: admissions@leadcollege.edu.in
- Website: https://lead.ac.in/
- Address: LEAD College (Autonomous), Dhoni, Palakkad - 678009, Kerala

FORMATTING GUIDELINES - VERY IMPORTANT:

DO NOT use asterisks (*) or markdown formatting in your responses.
Use clean, professional formatting with these exact symbols:

✓ For bullet points, use: • (bullet symbol) or - (hyphen)
✓ For numbers, use: 1. 2. 3. (plain numbers with periods)
✓ For emphasis, use line breaks and spacing, NOT asterisks
✓ Use emojis sparingly for visual clarity (💰 📚 🎓 📍 ✅)

YOUR COMMUNICATION STYLE:
- Introduce yourself as Clara when appropriate
- Be warm, approachable, and professional
- Use bullet points (•) or hyphens (-) for lists
- Use numbered lists (1. 2. 3.) for sequential steps
- Add line breaks between sections for readability
- Use emojis sparingly (💰 📚 🎓 📍 ✅)
- NEVER use asterisks for emphasis or formatting
- Keep responses clear, structured, and easy to read
- When relevant, mention: "For more details, visit https://lead.ac.in/"
- If you don't know something, direct to admissions office or website

Always respond in a helpful, professional manner with clean, structured formatting."""


# def call_llm(messages: List[Dict[str, str]], website_context: str = "") -> str:
#     """Call OpenAI API with error handling and optional website context"""
#     try:
#         # Add website context to system prompt if available
#         system_content = messages[0]["content"]
#         if website_context:
#             system_content += f"\n\nRECENT WEBSITE INFORMATION FROM https://lead.ac.in/:\n{website_context}"
#             messages[0]["content"] = system_content

#         resp = client.chat.completions.create(
#             # model="gpt-4o-mini",
#             model="openchat/openchat-3.5",
#             messages=messages,
#             temperature=0.23,
#             max_tokens=700,
#         )
#         return resp.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"OpenAI API Error: {e}")
#         return "I'm experiencing technical difficulties. Please try again or contact the admissions office directly."
def call_llm(messages, website_context=""):
    try:
        if website_context:
            messages[0]["content"] += f"\n\nWebsite Info:\n{website_context}"

        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=messages,
            temperature=0.3,
            max_tokens=700,
            extra_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "LEAD Chatbot"
            }
        )

        return response.choices[0].message.content

    except Exception as e:
        print("ERROR:", e)
        return "API error occurred"


@app.route("/")
def index():
    """Serve the main HTML file"""
    return send_from_directory(".", "home.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat API requests with website integration"""
    try:
        data = request.get_json(force=True) or {}
        user_msg = (data.get("message") or "").strip()
        history = data.get("history") or []

        if not user_msg:
            return jsonify({"error": "Empty message"}), 400

        if len(user_msg) > 500:
            return jsonify({"error": "Message too long. Please keep it under 500 characters."}), 400

        # Get website data (cached)
        website_data = get_cached_website_data()
        website_context = ""

        # Use website data if query matches relevant keywords
        if website_data:
            keywords = ['admission', 'fee', 'program', 'facility', 'contact', 'apply',
                        'eligibility', 'placement', 'hostel', 'campus', 'lab', 'event', 'news']
            user_query_lower = user_msg.lower()

            if any(keyword in user_query_lower for keyword in keywords):
                # Include relevant website content
                website_context = website_data['content'] if website_data['content'] else website_data['all_text']

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for m in history[-15:]:
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_msg})

        reply = call_llm(messages, website_context)

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500


@app.route("/api/website-sync", methods=["POST"])
def sync_website():
    """Manually sync website data"""
    try:
        data = fetch_website_data(COLLEGE_WEBSITE)
        if data:
            website_cache["data"] = data
            website_cache["timestamp"] = datetime.now()
            return jsonify({
                "status": "success",
                "message": "Website data synced successfully",
                "fetched_at": data['fetched_at']
            })
        return jsonify({"status": "error", "message": "Failed to fetch website data"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/website-status", methods=["GET"])
def website_status():
    """Check website cache status"""
    if website_cache["timestamp"]:
        age = (datetime.now() - website_cache["timestamp"]).total_seconds()
        expires_in = website_cache["expires_in"] - age
        return jsonify({
            "cached": website_cache["data"] is not None,
            "last_updated": website_cache["timestamp"].isoformat(),
            "age_seconds": int(age),
            "expires_in_seconds": int(expires_in),
            "website_url": COLLEGE_WEBSITE
        })
    return jsonify({"cached": False, "last_updated": None, "website_url": COLLEGE_WEBSITE})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "Clara - LEAD College Chatbot"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"🤖 Starting Clara - LEAD College Chatbot")
    print(f"📍 Location: Dhoni, Palakkad - 678009")
    print(f"🌐 Website: https://lead.ac.in/")
    print(f"🌡️  Temperature: 0.23")
    print(f"💰 MCA Fee Structure (2025-27):")
    print(f"   - Semester 1: ₹1,65,000")
    print(f"   - Semester 2: ₹1,25,000")
    print(f"   - Semester 3: ₹1,25,000")
    print(f"   - Semester 4: ₹1,25,000")
    print(f"   - TOTAL: ₹5,40,000 (includes hostel & mess)")
    print(f"🏦 Bank: Federal Bank, Palakkad")
    print(f"🔄 Cache: 24-hour auto-refresh")
    print(f"🚀 Starting on port {port}")

    # Pre-fetch website data on startup
    print("📡 Fetching initial website data...")
    get_cached_website_data()
    print("✓ Clara is ready!")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
