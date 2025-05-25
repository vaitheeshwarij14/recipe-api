from fastapi import FastAPI, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from database import SessionLocal
from models import Recipe
from schema import RecipeBase

import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
@app.get("/api/recipes", response_model=List[RecipeBase])
def get_all_recipes(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    recipes = db.query(Recipe).order_by(desc(Recipe.rating)).offset(offset).limit(limit).all()
    return recipes

def apply_operator(column, operator: str, value):
    if operator == ">":
        return column > value
    elif operator == ">=":
        return column >= value
    elif operator == "<":
        return column < value
    elif operator == "<=":
        return column <= value
    elif operator == "=":
        return column == value
    else:
        return None

@app.get("/api/recipes/search", response_model=List[RecipeBase])
def search_recipes(
    title: Optional[str] = None,
    cuisine: Optional[str] = None,
    rating: Optional[str] = None,       
    total_time: Optional[str] = None,   
    calories: Optional[str] = None,     
    db: Session = Depends(get_db)
):
    query = db.query(Recipe)

    if title:
        query = query.filter(Recipe.title.ilike(f"%{title}%"))
    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))

    if rating:
        for op in [">=", "<=", ">", "<", "="]:
            if rating.startswith(op):
                val = float(rating[len(op):])
                query = query.filter(apply_operator(Recipe.rating, op, val))
                break

    if total_time:
        for op in [">=", "<=", ">", "<", "="]:
            if total_time.startswith(op):
                val = int(total_time[len(op):])
                query = query.filter(apply_operator(Recipe.total_time, op, val))
                break

    if calories:
        for op in [">=", "<=", ">", "<", "="]:
            if calories.startswith(op):
                val = int(calories[len(op):])
                query = query.filter(apply_operator(Recipe.nutrients["calories"].as_integer(), op, val))
                break

    return query.all()
