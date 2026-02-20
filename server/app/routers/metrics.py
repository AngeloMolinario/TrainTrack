from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app import models, schemas
from typing import List, Optional

router = APIRouter(prefix="/metric", tags=["metric"])

@router.post("/", response_model=schemas.MetricRead)
async def create_metric(metric: schemas.MetricCreate, db: AsyncSession = Depends(get_db)):
    mtc = models.Metric(**metric.model_dump())
    db.add(mtc)
    await db.commit()
    await db.refresh(mtc)    
    return mtc

@router.post("/batch", response_model=list[schemas.MetricRead])
async def create_loss_batch(metrics: schemas.MetricBatchCreate, db: AsyncSession = Depends(get_db)):
    mtcs = [models.Metric(**mtc.model_dump()) for mtc in metrics.metrics]
    db.add_all(mtcs)
    await db.commit()
    for mtc in mtcs:
        await db.refresh(mtc)
    return mtcs

@router.get("/", response_model=List[schemas.MetricRead])
async def get_metrics(
        run_id: str,
        split: Optional[str] = None,
        metric_name: Optional[str] = None,
        limit: Optional[int] = None,
        db: AsyncSession = Depends(get_db)):

    stmt = select(models.Metric).where(models.Metric.run_id == run_id)
    if split:
        stmt = stmt.where(models.Metric.split == split)
    if limit:
        stmt = stmt.limit(limit)
    if metric_name:
        stmt = stmt.where(models.Metric.metric_name == metric_name)
    stmt = stmt.order_by(models.Metric.step.desc())
    result = await db.execute(stmt)
    return result.scalars().all()