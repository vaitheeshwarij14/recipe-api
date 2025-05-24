from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal
from models import Recipe
from schema import RecipeBase

import os

app = FastAPI()

# Serve HTML + static files from /static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route: Serve HTML file
@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Route: Get paginated recipes
@app.get("/api/recipes", response_model=List[RecipeBase])
def get_all_recipes(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    recipes = db.query(Recipe).order_by(Recipe.rating.desc().nullslast()).offset(offset).limit(limit).all()
    return recipes

# Route: Search API
@app.get("/api/recipes/search", response_model=List[RecipeBase])
def search_recipes(
    title: Optional[str] = None,
    cuisine: Optional[str] = None,
    calories: Optional[int] = None,
    total_time: Optional[int] = None,
    rating: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Recipe)

    if title:
        query = query.filter(Recipe.title.ilike(f"%{title}%"))
    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))
    if total_time is not None:
        query = query.filter(Recipe.total_time <= total_time)
    if rating is not None:
        query = query.filter(Recipe.rating >= rating)
    if calories is not None:
        query = query.filter(Recipe.nutrients['calories'].as_integer() <= calories)

    return query.all()
