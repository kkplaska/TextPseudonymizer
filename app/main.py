from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import os

from app.schemas import AnonymizeRequest, AnonymizeResponse, DeanonymizeRequest, DeanonymizeResponse
from app.engine import anonymize_text, deanonymize_text

app = FastAPI(title="Text Pseudonymizer API")

# Setup templates and static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
static_dir = os.path.join(BASE_DIR, "static")

# Ensure static dir exists (important for local running if output.css not generated yet)
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Global exception handlers for standard JSON format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error: " + str(exc.errors())}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error: " + str(exc)}
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the single-page application."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/api/anonymize", response_model=AnonymizeResponse)
async def anonymize(payload: AnonymizeRequest):
    """Anonymize text based on a list of words."""
    try:
        result_text, mapping = anonymize_text(payload.text, payload.words)
        return AnonymizeResponse(result_text=result_text, mapping=mapping)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/deanonymize", response_model=DeanonymizeResponse)
async def deanonymize(payload: DeanonymizeRequest):
    """Deanonymize text using the provided mapping."""
    try:
        result_text = deanonymize_text(payload.text, payload.mapping)
        return DeanonymizeResponse(result_text=result_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
