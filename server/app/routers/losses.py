from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from app.db import get_db
from app import models, schemas
from typing import List, Optional

router = APIRouter(prefix="/loss", tags=["loss"])

@router.post("/", response_model=schemas.LossRead)
async def create_loss(loss: schemas.LossCreate, db: AsyncSession = Depends(get_db)):
    loss = models.Loss(
        run_id=loss.run_id,
        step=loss.step,
        split=loss.split,
        value=loss.value        
    )
    db.add(loss)
    await db.commit()
    await db.refresh(loss)    
    return loss

@router.post("/batch", response_model=list[schemas.LossRead])
async def create_loss_batch(loss_batch: schemas.LossBatchCreate, db: AsyncSession = Depends(get_db)):
    losses = [models.Loss(**loss.model_dump()) for loss in loss_batch.losses]
    db.add_all(losses)
    await db.commit()
    for loss in losses:
        await db.refresh(loss)
    return losses

@router.get("/", response_model=List[schemas.LossRead])
async def get_losses(
        run_id: str,
        split: Optional[str] = None,
        limit: Optional[int] = None,
        db: AsyncSession = Depends(get_db)):

    stmt = select(models.Loss).where(models.Loss.run_id == run_id)
    if split:
        stmt = stmt.where(models.Loss.split == split)
    if limit:
        stmt = stmt.limit(limit)
    stmt = stmt.order_by(models.Loss.step.desc())
    result = await db.execute(stmt)
    return result.scalars().all()