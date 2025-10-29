import uvicorn
from datetime import datetime, timezone
import json

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import URL_PATH_PREFIX, API_PORT

from db.session import engine, wait_for_db
from db.base import Base
from models import user, credential

from routes import user, credential, utils

app = FastAPI(
    title="Password Manager API",
    description="API pour gérer les utilisateurs et leurs credentials",
    version="1.0.1",
    root_path=URL_PATH_PREFIX,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.state.identifier = "passmanager_api"

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        # "chrome-extension://XXXXXX",
        # "moz-extension://XXXXXX",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_meta_to_response(request: Request, call_next):
    response = await call_next(request)
    
    # Pour les réponses JSON uniquement
    if isinstance(response, JSONResponse) or response.headers.get("content-type") == "application/json":
        # Lire le body existant
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        try:
            # Parser et modifier
            data = json.loads(body)
            data["meta"] = {
                "name": app.title,
                "version": app.version,
                "identifier": "passmanager_api",
                "documentation_url": f"{app.root_path}/{app.docs_url.lstrip('/')}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Créer nouvelle réponse avec les headers corrects (Content-Length sera recalculé)
            return JSONResponse(
                content=data,
                status_code=response.status_code
            )
        except json.JSONDecodeError:
            # Si le body n'est pas du JSON valide, retourner la réponse originale
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    
    return response

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
    uvicorn.run("main:app", host="0.0.0.0", port=API_PORT, reload=True)