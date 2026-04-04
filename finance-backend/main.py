from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import Base, engine

app = FastAPI(
    title="Finance Dasboard API",
    description=(
        "A role-based finance records management system. \n\n"
        "## Roles\n"
        "- **viewer** — can view transactions only\n"
        "- **analyst** — can view transactions and access dashboard summaries\n"
        "- **admin** — full access: create, update, delete transactions and manage users\n\n"
        "## Auth\n"
        "Register via `POST /auth/register`, then login via `POST /auth/login` "
        "to receive a JWT token. Pass it as `Authorization: Bearer <token>` on all other requests."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )