from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, services, database

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    new_project = models.Project(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date
    )
    db.add(new_project)
    db.flush()

    if project_data.places:
        seen_ids = set()
        for p_in in project_data.places:
            if p_in.external_id in seen_ids:
                raise HTTPException(400, "Duplicate external ID")
            if not await services.validate_artwork(p_in.external_id):
                raise HTTPException(400, f"Artwork {p_in.external_id} not found")
            
            place = models.Place(**p_in.model_dump(), project_id=new_project.id)
            db.add(place)
            seen_ids.add(p_in.external_id)

    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[schemas.ProjectRead])
def list_projects(db: Session = Depends(database.get_db)):
    return db.query(models.Project).all()

@router.get("/{project_id}", response_model=schemas.ProjectRead)
def get_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return project

@router.patch("/{project_id}", response_model=schemas.ProjectRead)
def update_project(project_id: int, update_data: schemas.ProjectUpdate, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    data = update_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or any(p.is_visited for p in project.places):
        raise HTTPException(400, "Cannot delete project")
    db.delete(project)
    db.commit()
    return None