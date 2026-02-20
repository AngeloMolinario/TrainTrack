from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from uuid import UUID
from app.db import get_db
from app import models, schemas
from datetime import datetime, timezone


router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/", response_model=schemas.RunRead)
async def create_run(run: schemas.RunCreate, db: AsyncSession = Depends(get_db)):
    run = models.TrainingRun(
        model_id=run.model_id,
        hyperparameters=run.hyperparameters,
        status = "running"        
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.get("/runbymodels/{model_id}", response_model=list[schemas.RunRead])
async def read_runs(model_id: str, db: AsyncSession = Depends(get_db)):
    run_exists = await db.execute(select(models.TrainingRun).where(models.TrainingRun.model_id == model_id))
    result = run_exists.scalars().all()
    if not result:
        raise HTTPException(status_code=404, detail="Run not found")
    return result

@router.get("/runbyproject/{project_name}", response_model=list[schemas.RunRead])
async def read_runs_by_project(project_name: str, db: AsyncSession = Depends(get_db)):
    project_exists = await db.execute(select(models.Model).where(models.Model.project_name == project_name))
    if not project_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    stmt = (select(models.TrainingRun)
    .join(models.Model, models.TrainingRun.model_id == models.Model.id)
    .where(models.Model.project_name == project_name)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/{run_id}")
async def delete_run(run_id: str, db: AsyncSession = Depends(get_db)):
    ids = [UUID(r) for r in run_id.split(",")]
    result = delete(models.TrainingRun).where(models.TrainingRun.id.in_(ids))
    result = await db.execute(result)
    await db.commit()
    return {"detail": "Run deleted", "Affected row" : result.rowcount}

@router.patch("/update_status")
async def update_status(payload: schemas.RunStatusUpdate, db: AsyncSession = Depends(get_db)):
    run_id = payload.run_id
    new_status = payload.new_status
    if new_status == 'completed':
        stmt = (update(models.TrainingRun).where(models.TrainingRun.id==run_id)
                .values(status=new_status)
                .values(finished_at=datetime.now(timezone.utc)))
    else:
        stmt = update(models.TrainingRun).where(models.TrainingRun.id==run_id).values(status=new_status)
    result = await db.execute(stmt)
    await db.commit()
    return {"rows_updated": result.rowcount}  
