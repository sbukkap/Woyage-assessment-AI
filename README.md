# Woyage AI – Interview Follow-Up Generator

This repository contains a solution for the Woyage AI Engineer Exercise 1.
It is a FastAPI backend that generates contextual follow-up interview questions based on a candidate’s answer by using the OpenAI API.

---

## Tech Stack

- Python 3.10+
- FastAPI (backend framework)
- Pydantic (data validation)
- OpenAI (question generation)
- Uvicorn (ASGI server)
- python-dotenv (environment variable loader)

---

## Setup Instructions

### Clone the Repository

```
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### Create a Virtual Environment

```
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```
pip install fastapi uvicorn openai pydantic pydantic-settings python-dotenv
```

### Configure your OpenAI Key

Create a `.env` file in the project root, and add the following lines:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Run the Server

```
uvicorn main:app --reload
```

After startup, the API will be available at: http://127.0.0.1:8000

---

## How to Test

Open your browser and go to http://127.0.0.1:8000/docs  
Find the endpoint: POST `/interview/generate-followups`  
Click "Try it out" and enter this sample JSON:

```
{
  "question": "Tell me about a time you handled conflicting priorities.",
  "answer": "In my last role, two urgent client requests came in at once. I triaged by impact and aligned stakeholders.",
  "role": "Senior Backend Engineer",
  "interview_type": ["Behavioral"]
}
```

Click Execute.  
The result will be shown under Response body.

You can also check the health endpoint:
- GET `/healthz` → `{ "status": "ok" }`

---

## API Summary

### POST /interview/generate-followups

Generates a concise follow-up interview question.

**Request Body:**

| Field          | Type          | Required | Description                     |
|----------------|---------------|----------|---------------------------------|
| question       | string        | Yes      | Original interview question     |
| answer         | string        | Yes      | Candidate’s answer              |
| role           | string        | No       | Target role or title            |
| interview_type | array[string] | No       | Type(s) of interview            |

**Example Response:**

```
{
  "result": "success",
  "message": "Follow-up question generated.",
  "data": {
    "followup_question": "How did you communicate your prioritization decisions to stakeholders?"
  }
}
```

Possible Errors:

- 422: Missing or invalid fields
- 413: Input too long
- 502: OpenAI API error

---

## Example cURL

```
curl -X POST "http://127.0.0.1:8000/interview/generate-followups" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Tell me about a time you had to learn a new technology quickly.\", \"answer\": \"I learned Kafka for a project by building a weekend POC.\", \"role\": \"Software Engineer\"}"
```

---

## Author

Shreekar Bukkapattanam  
AI & Software Engineer Enthusiast
```
