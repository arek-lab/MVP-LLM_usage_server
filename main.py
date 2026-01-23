from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import lifespan, ORIGIN_URL

app = FastAPI(title="MVP Agentic AI API", version="1.0.0", lifespan=lifespan)

origins = [ORIGIN_URL, "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.auth_routes import router as auth_router
from app.api.feedback_generator import router as feedback_gen_router
from app.api.email_generator import router as email_gen_router
from app.api.graph import router as graph_router
from app.api.stream import router as stream_router
from app.api.text_cratfer import router as text_crafter_router


app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(feedback_gen_router, prefix="/api/feedback", tags=["feedback generator"])
app.include_router(email_gen_router, prefix="/api/email", tags=["email generator"])
app.include_router(graph_router, prefix="/api/graph", tags=["Graph Operations"])
app.include_router(stream_router, prefix="/api/stream", tags=["Streaming"])
app.include_router(text_crafter_router, prefix="/api/text-craft", tags=["Text Crafting"])


@app.get("/")
async def root():
    return {"message": "MVP Agentic AI Server"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# heroku addons:create heroku-postgresql:essential-0
