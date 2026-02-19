from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import engine, Base
from app.routers import models, runs, losses
import asyncio
import logging

logger = logging.getLogger("uvicorn")
# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # retry loop per aspettare DB live
    max_retries = 10
    for i in range(max_retries):
        try:
            async with engine.begin() as conn:
                # crea tutte le tabelle se non esistono
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables created successfully")
            break
        except Exception as e:
            logger.warning(f"DB not ready yet ({i+1}/{max_retries}), retrying... Error: {e}")
            await asyncio.sleep(10)
    else:
        raise RuntimeError("❌ Cannot connect to the database after multiple retries")

    yield  # tutto quello che sta dentro il contesto lifespan

    # shutdown logic
    await engine.dispose()
    logger.info("DB connection pool closed")

# crea app FastAPI usando lifespan
app = FastAPI(lifespan=lifespan)

app.include_router(models.router)
app.include_router(runs.router)
app.include_router(losses.router)