from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db import engine, Base
from app.routers import models, runs, losses, metrics
import asyncio
import logging

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):    
    max_retries = 10
    for i in range(max_retries):
        try:
            async with engine.begin() as conn:
                # crea tutte le tabelle se non esistono
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")
            break
        except Exception as e:
            logger.warning(f"DB not ready yet ({i+1}/{max_retries}), retrying... Error: {e}")
            await asyncio.sleep(5)
    else:
        raise RuntimeError("Cannot connect to the database after multiple retries")
    yield    
    await engine.dispose()
    logger.info("DB connection pool closed")


app = FastAPI(title="Experiment monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def check_health():
    return {'status' : 'ok'}

app.include_router(models.router)
app.include_router(runs.router)
app.include_router(losses.router)
app.include_router(metrics.router)