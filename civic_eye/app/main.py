import os
import json
import sqlite3
from datetime import datetime
import numpy as np
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from jose import JWTError, jwt
import joblib
import pandas as pd
import sqlite3 as sq
from pydantic import BaseModel, Field

# --- ML Models ---
cat_model = joblib.load('models/category_model.pkl')
pri_model = joblib.load('models/priority_model.pkl')

with open('models/metrics.json', 'r') as f:
    metrics = json.load(f)

# --- Security ---
pwd_context = CryptContext(schemes=["auto"], deprecated="auto")
SECRET_KEY = "civic-eye-secret-key-2025"
ALGORITHM = "HS256"

# --- Database ---
DB_PATH = "civic_eye.db"


def init_db():
    """Initialize SQLite database with required tables."""
    conn = sq.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Pending',
            resolution_note TEXT,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    # Seed admin user if not exists
    cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@civic.com",))
    if cursor.fetchone() is None:
        hashed = pwd_context.hash("admin123")
        cursor.execute("INSERT INTO users (email, hashed_password, is_admin) VALUES (?, ?, ?)",
                       ("admin@civic.com", hashed, True))
    conn.commit()
    conn.close()


init_db()

# --- Pydantic models ---
class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    location: str = Field(default="", max_length=200)


class IssueUpdate(BaseModel):
    status: str
    resolution_note: str = Field(default="", max_length=500)


class UserCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)


# --- FastAPI app ---
app = FastAPI(title="Crowdsourced Civic Issue Reporting System", version="1.0.0")

# Setup sessions using signed cookies
from fastapi.security import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key="session-secret-key-change-in-production",
)


# --- Helper: Predict category and priority ---
def predict_issue(text_combine: str):
    """Predict category and priority from combined title+description text."""
    combined = text_combine or "civic issue"

    cat_pred = cat_model.predict([combined])[0]
    cat_confidence = float(np.max(cat_model.predict_proba([combined])[0]) * 100)

    pri_pred = pri_model.predict([combined])[0]
    pri_confidence = float(np.max(pri_model.predict_proba([combined])[0]) * 100)

    # If category confidence below 40%, mark "Needs review"
    if cat_confidence < 40:
        cat_pred = "Needs review"

    return {
        "category": cat_pred,
        "category_confidence": round(cat_confidence, 1),
        "priority": pri_pred,
        "priority_confidence": round(pri_confidence, 1)
    }


# --- Dependency: get DB connection ---
def get_db():
    conn = sq.connect(DB_PATH)
    conn.row_factory = sq.Row
    try:
        yield conn
    finally:
        conn.close()


# --- Auth helpers ---
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def authenticate_user(email, password, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, hashed_password, is_admin FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row and verify_password(password, row[2]):
        return {"id": row[0], "email": row[1], "is_admin": row[3]}
    return None


def get_user_from_session(request: Request, conn) -> dict | None:
    """Get user from session data stored in cookie."""
    session_data = request.session.get("user")
    if session_data:
        return session_data
    return None


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, conn=Depends(get_db)):
    """Landing page - show options for user or admin."""
    user = get_user_from_session(request, conn)
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "user": user,
        "page": "home"
    })


@app.post("/api/register")
async def register(user: UserCreate, conn=Depends(get_db)):
    """Register a new user."""
    cursor = conn.cursor()
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = pwd_context.hash(user.password)
    cursor.execute(
        "INSERT INTO users (email, hashed_password, is_admin) VALUES (?, ?, ?)",
        (user.email, hashed_pwd, False)
    )
    conn.commit()
    
    return {"message": "Registration successful. Please login."}


@app.post("/api/login")
async def login(form_data: dict, request: Request, response: Response, conn=Depends(get_db)):
    """Login and create session cookie."""
    email = form_data.get("email", "")
    password = form_data.get("password", "")
    
    user = authenticate_user(email, password, conn)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session - store user info in signed cookie
    request.session["user"] = {
        "id": user["id"],
        "email": user["email"],
        "is_admin": user["is_admin"]
    }
    
    # Also set a JWT-like cookie for backwards compatibility
    import time
    token = jwt.encode(
        {"sub": user["email"], "is_admin": user["is_admin"], "iat": int(time.time())},
        SECRET_KEY, algorithm=ALGORITHM
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 1 week
    )
    
    return {"message": "Login successful", "is_admin": user["is_admin"]}


@app.get("/api/me")
async def me(request: Request):
    """Get current user info from session."""
    user = get_user_from_session(request, None)
    if user:
        return {"email": user["email"], "is_admin": user["is_admin"], "id": user["id"]}
    return {"is_admin": False}


@app.post("/api/logout")
async def logout(request: Request, response: Response):
    """Logout - clear session cookie."""
    request.session.pop("user", None)
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@app.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, conn=Depends(get_db)):
    """User dashboard - view only their own issues."""
    user = get_user_from_session(request, conn)
    if not user or not user.get("is_admin") is False:
        return RedirectResponse(url="/", status_code=302)
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, category, priority, status, resolution_note, created_at 
        FROM issues 
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user["id"],))
    issues = cursor.fetchall()
    
    return templates.TemplateResponse("user_dashboard.html", {
        "request": request, 
        "issues": issues,
        "user": user,
        "page": "user_dashboard"
    })


@app.post("/user/report")
async def report_issue(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    photo = None,
    conn=Depends(get_db)
):
    """Report a new issue - with ML prediction."""
    user = get_user_from_session(request, conn)
    if not user or user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Predict category and priority from title + description
    combined_text = f"{title} {description}"
    prediction = predict_issue(combined_text)
    
    category = prediction["category"]
    priority = prediction["priority"]
    
    # Handle photo upload
    photo_path = None
    if photo:
        import base64
        if hasattr(photo, 'filename') and photo.filename:
            # Accept only image files
            if not photo.contenttype or not photo.contenttype.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            if photo.size > 5 * 1024 * 1024:  # 5 MB
                raise HTTPException(status_code=400, detail="File too large (>5MB)")
            # Save photo
            os.makedirs("static/uploads", exist_ok=True)
            filename = f"{int(datetime.now().timestamp())}_{photo.filename}"
            filepath = os.path.join("static/uploads", filename)
            with open(filepath, "wb") as f:
                f.write(photo.file.read())
            photo_path = f"/static/uploads/{filename}"
    
    # Save issue to database
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO issues (user_id, title, description, category, priority, status, photo_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user["id"], title, description, category, priority, "Pending", photo_path)
    )
    conn.commit()
    
    return {
        "message": "Issue reported successfully",
        "category": category,
        "priority": priority,
        "category_confidence": prediction["category_confidence"],
        "priority_confidence": prediction["priority_confidence"],
        "needs_review": prediction["category"] == "Needs review"
    }


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    conn=Depends(get_db)
):
    """Admin dashboard - view all issues with filters."""
    user = get_user_from_session(request, conn)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/", status_code=302)
    
    cursor = conn.cursor()
    
    # Build query with filters
    query = "SELECT i.id, i.title, i.category, i.priority, i.status, i.resolution_note, i.photo_path, i.created_at, u.email FROM issues i JOIN users u ON i.user_id = u.id WHERE 1=1"
    params = []
    
    # Get filter parameters from request query string
    category = request.query_params.get("category", "")
    priority = request.query_params.get("priority", "")
    status = request.query_params.get("status", "")
    
    if category:
        query += " AND i.category = ?"
        params.append(category)
    if priority:
        query += " AND i.priority = ?"
        params.append(priority)
    if status:
        query += " AND i.status = ?"
        params.append(status)
    
    query += " ORDER BY i.priority DESC, i.created_at DESC"
    
    cursor.execute(query, params)
    issues = cursor.fetchall()
    
    # Get counts by status and category
    cursor.execute("SELECT status, COUNT(*) as cnt FROM issues GROUP BY status")
    status_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT category, COUNT(*) as cnt FROM issues GROUP BY category")
    category_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT priority, COUNT(*) as cnt FROM issues GROUP BY priority")
    priority_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "issues": issues,
        "page": "admin_dashboard",
        "categories": ["All", "Pothole", "Garbage", "Streetlight", "Water Leakage", "Drainage", "Other"],
        "priorities": ["All", "Low", "Medium", "High"],
        "statuses": ["All", "Pending", "In Progress", "Resolved"],
        "status_counts": status_counts,
        "category_counts": category_counts,
        "priority_counts": priority_counts,
        "selected_category": category,
        "selected_priority": priority,
        "selected_status": status,
        "metrics": metrics
    })


@app.post("/admin/issue/{issue_id}/status")
async def update_issue_status(
    issue_id: int,
    update: IssueUpdate,
    conn=Depends(get_db)
):
    """Update issue status: Pending -> In Progress -> Resolved."""
    user = get_user_from_session(request, conn)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cursor = conn.cursor()
    
    # Check current status
    current_cursor = cursor.execute("SELECT status FROM issues WHERE id = ?", (issue_id,))
    row = current_cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    current_status = row[0]
    
    # Validate status transition
    valid_transitions = {
        "Pending": ["In Progress"],
        "In Progress": ["Resolved", "Pending"],
        "Resolved": []  # Final state
    }
    
    if update.status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status transition from {current_status} to {update.status}"
        )
    
    cursor.execute(
        "UPDATE issues SET status = ?, resolution_note = ? WHERE id = ?",
        (update.status, update.resolution_note, issue_id)
    )
    conn.commit()
    
    return {"message": f"Issue status updated to {update.status}", "new_status": update.status}


@app.post("/admin/issue/{issue_id}/correct-category")
async def correct_category(
    issue_id: int,
    new_category: str = Form(...),
    conn=Depends(get_db)
):
    """Admin correct a wrong ML category."""
    user = get_user_from_session(request, conn)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cursor = conn.cursor()
    
    # Validate category
    valid_categories = ["Pothole", "Garbage", "Streetlight", "Water Leakage", "Drainage", "Other", "Needs review"]
    if new_category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    cursor.execute("UPDATE issues SET category = ? WHERE id = ?", (new_category, issue_id))
    conn.commit()
    
    return {"message": f"Category corrected to {new_category}", "new_category": new_category}


@app.get("/admin/ml-insights", response_class=HTMLResponse)
async def ml_insights(request: Request, conn=Depends(get_db)):
    """ML Insights page - dataset metrics and live prediction."""
    user = get_user_from_session(request, conn)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/", status_code=302)
    
    # Read metrics from saved file
    with open('models/metrics.json', 'r') as f:
        metrics = json.load(f)
    
    # Add dataset origin note
    metrics['dataset_note'] = "This dataset is synthetic and generated for demo purposes."
    
    return templates.TemplateResponse("ml_insights.html", {
        "request": request,
        "page": "ml_insights",
        "metrics": metrics
    })


@app.post("/admin/ml-insights/predict")
async def ml_predict(request: Request, sentence: str = Form(...)):
    """Live prediction from user-input sentence."""
    prediction = predict_issue(sentence)
    return {"prediction": prediction}


# --- Startup event ---
@app.on_event("startup")
async def startup():
    print("🏙️  CivicEye Application Starting...")
    print("   ML models loaded from models/ directory")
    print("   Database initialized")
    print("   Admin credentials: admin@civic.com / admin123")