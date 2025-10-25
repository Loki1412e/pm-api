import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import TRAEFIK_PATH_PREFIX, API_PORT

from db.session import engine, wait_for_db
from db.base import Base
from models import user, credential

from routes import user, credential, utils

app = FastAPI(
    title="Password Manager API",
    description="API pour gérer les utilisateurs et leurs credentials",
    version="0.1.0",
    root_path=TRAEFIK_PATH_PREFIX,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Startup : attendre que la DB soit prête
@app.on_event("startup")
async def startup_event():
    await wait_for_db(engine, retries=15, delay=2)
    
    # Créer les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Routes
app.include_router(user.router, tags=["User"])
app.include_router(credential.router, tags=["Credentials"])
app.include_router(utils.router, tags=["Utils"])

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=API_PORT, reload=True)
