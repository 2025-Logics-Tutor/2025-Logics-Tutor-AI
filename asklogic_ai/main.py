from fastapi import FastAPI
from asklogic_ai.api.ask_router import router as ask_router

app = FastAPI(title="AskLogic RAG API")

app.include_router(ask_router, prefix="/ask", tags=["AskLogic"])