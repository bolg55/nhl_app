from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import players, optimize, settings, status
from app.core.config import get_settings

app = FastAPI(title=get_settings().APP_NAME)

origins = [
    "http://localhost:5173",  # Vite's default port
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
# app.include_router(status.router, prefix="/api/status", tags=["status"])

@app.get("/")
async def root():
    return {"message": "NHL Fantasy Optimizer API"}