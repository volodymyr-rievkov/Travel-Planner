from fastapi import FastAPI
import models
from database import engine
from routers import projects, places, system

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
)

app.include_router(system.router)
app.include_router(projects.router)
app.include_router(places.router)

@app.get("/")
def root():
    return {"message": "Welcome to Travel Planner API. Go to /docs for API explorer."}