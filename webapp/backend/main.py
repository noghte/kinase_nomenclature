from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import psycopg2
import os
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, status
# use python-jose for JWT handling
from jose import jwt
import json

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")

# Initialize app, limiter, and logger
app = FastAPI()
# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Input model
class LoginRequest(BaseModel):
    username: str
    password: str

# Login endpoint with rate limiting
@app.post("/login")
@limiter.limit("5/minute")  # 5 login attempts per minute per IP
async def login(request: Request, body: LoginRequest):
    try:
        with psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            port=DB_PORT,
            connect_timeout=5
        ) as conn:
            with conn.cursor() as cur:
                # fetch user id and hashed password
                cur.execute(
                    "SELECT id, password FROM users WHERE username = %s", 
                    (body.username,)
                )
                row = cur.fetchone()
    except Exception as e:
        logger.error(f"Login error for user '{body.username}': {e}")
        return JSONResponse(status_code=500, content={"status": "Internal Server Error"})

    # row: (user_id, password_hash)
    if row and pwd_context.verify(body.password, row[1]):
        user_id = row[0]
        # create JWT token valid for 1 hour, embed user id
        payload = {"sub": body.username, "uid": user_id, "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return {"status": "OK", "token": token}
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"status": "Invalid credentials"}
        )
    
@app.get("/me")
async def me(request: Request):
    # Get token from Authorization header
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"username": payload.get("sub")}

# -----------------------------
# Review and Proposals endpoints
# -----------------------------
class ReviewRequest(BaseModel):
    completeness: int
    factual_accuracy: int
    specificity: int
    coherence: int
    structure: int
    usability: int
    strengths: str
    weaknesses: str
    suggestions: str

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload

@app.get("/proposals")
async def list_proposals(request: Request):
    payload = get_current_user(request)
    try:
        conn = psycopg2.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME, port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM proposals ORDER BY id")
        rows = cur.fetchall()
    except Exception as e:
        logger.error(f"Error fetching proposals: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not fetch proposals")
    finally:
        cur.close()
        conn.close()
    proposals = [{"id": r[0], "title": r[1]} for r in rows]
    return {"proposals": proposals}

@app.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: int, request: Request):
    payload = get_current_user(request)
    user_id = payload.get("uid")
    try:
        conn = psycopg2.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME, port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT id, title, document_markdown FROM proposals WHERE id = %s", (proposal_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
        proposal = {"id": row[0], "title": row[1], "document_markdown": row[2]}
        # fetch existing review if any
        cur.execute("SELECT review_data FROM reviews WHERE user_id = %s AND proposal_id = %s", (user_id, proposal_id))
        rev_row = cur.fetchone()
        review = rev_row[0] if rev_row else None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching proposal {proposal_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not fetch proposal")
    finally:
        cur.close()
        conn.close()
    return {"proposal": proposal, "review": review}

@app.post("/proposals/{proposal_id}/review")
async def submit_review(proposal_id: int, review: ReviewRequest, request: Request):
    payload = get_current_user(request)
    user_id = payload.get("uid")
    try:
        conn = psycopg2.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME, port=DB_PORT
        )
        cur = conn.cursor()
        # check existing review
        cur.execute("SELECT id FROM reviews WHERE user_id = %s AND proposal_id = %s", (user_id, proposal_id))
        existing = cur.fetchone()
        review_json = json.dumps(review.dict())
        if existing:
            cur.execute(
                "UPDATE reviews SET review_data = %s, updated_at = now(), is_submitted = true WHERE id = %s",
                (review_json, existing[0])
            )
        else:
            cur.execute(
                "INSERT INTO reviews (user_id, proposal_id, review_data, submitted_at, is_submitted) VALUES (%s, %s, %s, now(), true)",
                (user_id, proposal_id, review_json)
            )
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving review for proposal {proposal_id} by user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save review")
    finally:
        cur.close()
        conn.close()
    return {"status": "OK"}