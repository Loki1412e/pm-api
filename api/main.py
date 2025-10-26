import uvicorn
import datetime
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
    version="0.1.1",
    root_path=URL_PATH_PREFIX,
    docs_path="/docs",
    redoc_path="/redoc",
    openapi_path="/openapi.json",
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

# Middleware
@app.middleware("http")
async def add_meta_to_response(request: Request, call_next):
    
    response = await call_next(request)

    # Ne pas wrapper les docs, openapi, ou les réponses non-JSON
    if not request.url.path.startswith(URL_PATH_PREFIX) or \
       request.url.path in (app.docs_url, app.redoc_url, app.openapi_url) or \
       response.media_type != "application/json":
        return response

    # Lire le corps de la réponse (nécessaire car c'est un stream)
    response_body_bytes = b""
    async for chunk in response.body_iterator:
        response_body_bytes += chunk
    
    try:
        data = json.loads(response_body_bytes.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Réponse non-JSON (ex: 304 Not Modified), on la retourne telle quelle
        return Response(content=response_body_bytes, 
                        status_code=response.status_code, 
                        headers=dict(response.headers))

    final_meta = {
        "name": app.title,
        "identifier": app.state.identifier,
        "version": app.version,
        "documentation_url": f"/{app.root_path.lstrip('/')}/{app.docs_url.lstrip('/')}",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # On rajoute meta dans la réponse
    data["meta"] = final_meta
    
    return JSONResponse(content=data, status_code=response.status_code)

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
