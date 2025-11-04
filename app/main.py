import os
from dotenv import load_dotenv
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from openai import OpenAI

# --- Settings ---
load_dotenv()

# We can just grab our settings directly from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_INPUT_CHARS = 4000  # Global app constant

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file! App cannot start.")

client = OpenAI(api_key=OPENAI_API_KEY)


# --- Schemas ---

class GenerateFollowupsRequest(BaseModel):
    # required
    question: str = Field(..., min_length=3)
    answer: str = Field(..., min_length=3)
    
    # optional
    role: str | None = None
    interview_type: list[str] | None = None

    # Use a validator to ensure our main fields aren't just whitespace
    @field_validator("question", "answer")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty or whitespace only.")
        return v.strip()


class FollowupData(BaseModel):
    followup_question: str

class GenerateFollowupsResponse(BaseModel):
    result: str
    message: str
    data: FollowupData


# --- App ---
app = FastAPI(
    title="Woyage AI – Follow-up Generator",
    version="1.0.0"
)

SYSTEM_PROMPT = (
    "You are an interview co-pilot. Given the original question and the candidate’s answer, "
    "return ONE concise, specific, open-ended follow-up (≤20 words). "
    "Do not restate the original question. Avoid yes/no, leading, or unsafe content. "
    "Return ONLY the question text."
)

@app.get("/healthz")
def healthz():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.post("/interview/generate-followups", response_model=GenerateFollowupsResponse)
def generate_followups(payload: GenerateFollowupsRequest):
    
    # Input validation is now handled by Pydantic's `field_validator`
    
    # Quick size guard
    if len(payload.question) + len(payload.answer) > MAX_INPUT_CHARS:
        raise HTTPException(status_code=413, detail="Input too large.")

    # Build the user-facing prompt
    user_content = (
        "Context:\n"
        f"- Role: {payload.role or 'N/A'}\n"
        f"- Interview type(s): {', '.join(payload.interview_type or []) or 'N/A'}\n\n"
        f"Original question:\n{payload.question}\n\n"  # Already stripped by validator
        f"Candidate answer:\n{payload.answer}\n\n"    # Already stripped by validator
        "Return ONLY the follow-up question."
    )

    try:
        res = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,  # Low temp to keep it focused and not overly "creative"
            max_tokens=120,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )

        followup = (res.choices[0].message.content or "").strip()
        
        if not followup:
            # This handles cases where the model returns None, "", or just " "
            raise HTTPException(status_code=502, detail="Model returned empty output.")

        return GenerateFollowupsResponse(
            result="success",
            message="Follow-up question generated.",
            data=FollowupData(followup_question=followup),
        )
        
    except HTTPException:
        # Re-raise known HTTP exceptions (like 413, 502)
        raise
    except Exception as e:
        # Catch any other unexpected errors (e.g., OpenAI API down)
        print(f"!!! UNEXPECTED ERROR: {e}") # Log for debugging
        raise HTTPException(status_code=502, detail="An upstream error occurred.")