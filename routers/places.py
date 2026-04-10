from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, services, database

router = APIRouter(tags=["Places"])

@router.post("/projects/{project_id}/places/", response_model=schemas.PlaceRead)
async def add_place(project_id: int, place_data: schemas.PlaceCreate, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or len(project.places) >= 10:
        raise HTTPException(400, "Project not found or limit reached")
    
    if not await services.validate_artwork(place_data.external_id):
        raise HTTPException(400, "Invalid External ID")

    new_place = models.Place(**place_data.model_dump(), project_id=project_id)
    project.is_completed = False
    db.add(new_place)
    db.commit()
    db.refresh(new_place)
    return new_place

@router.patch("/places/{place_id}", response_model=schemas.PlaceRead)
def update_place(place_id: int, update_data: schemas.PlaceUpdate, db: Session = Depends(database.get_db)):
    place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not place:
        raise HTTPException(404, "Place not found")

    if update_data.notes is not None:
        place.notes = update_data.notes
    if update_data.is_visited is not None:
        place.is_visited = update_data.is_visited
        db.flush()
        project = place.project
        project.is_completed = all(p.is_visited for p in project.places)

    db.commit()
    db.refresh(place)
    return place