import json
from sqlalchemy.orm import Session
from models import Recipe
from database import SessionLocal

def is_number(value):
    try:
        float(value)
        return True
    except:
        return False

def parse_and_store():
    db: Session = SessionLocal()

    with open("US_recipes_null.json", "r", encoding="utf-8") as file:
        data = json.load(file)

        if not isinstance(data, dict):
            print("Unexpected JSON format.")
            return

        print("Top-level keys:", list(data.keys())[:3])  # Show first few keys

        for index, item in enumerate(data.values()):
            if not isinstance(item, dict):
                print(f"Skipping non-dict at index {index}")
                continue

            try:
                recipe = Recipe(
                    title=item.get("title", ""),
                    cuisine=item.get("cuisine", ""),
                    rating=float(item["rating"]) if is_number(item.get("rating")) else None,
                    prep_time=int(item["prep_time"]) if is_number(item.get("prep_time")) else None,
                    cook_time=int(item["cook_time"]) if is_number(item.get("cook_time")) else None,
                    total_time=int(item["total_time"]) if is_number(item.get("total_time")) else None,
                    description=item.get("description", ""),
                    nutrients=item.get("nutrients", {}) if isinstance(item.get("nutrients"), dict) else {},
                    serves=item.get("serves", "")
                )
                db.add(recipe)
            except Exception as e:
                print(f"Error inserting at index {index}:", e)

        db.commit()
        db.close()
        print("✅ Done inserting recipes.")

if __name__ == "__main__":
    parse_and_store()
