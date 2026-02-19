from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/models", tags=["models"])

@router.post("/", response_model=schemas.ModelRead)
async def create_model(model: schemas.ModelCreate, db: AsyncSession = Depends(get_db)):
    model = models.Model(**model.dict())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model

@router.get("/", response_model=list[schemas.ModelRead])
async def read_models(db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Model))
    return result.scalars().all()

@router.delete("/{model_id}")
async def delete_model(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Model).where(models.Model.id == model_id))
    model = result.scalar_one_or_none()
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    await db.delete(model)
    await db.commit()
    return {"detail": "Model deleted"}

@router.delete("/project/{project_name}")
async def delete_models_by_project(project_name: str, db: AsyncSession = Depends(get_db)):
    stmt = delete(models.Model).where(models.Model.project_name == project_name)
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No models found for this project")
    
    return {"detail": f"Deleted {result.rowcount} models for project '{project_name}'"}