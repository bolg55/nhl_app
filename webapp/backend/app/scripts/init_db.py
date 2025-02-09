import pandas as pd
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import models
from datetime import datetime

def init_db():
    # Create all tables
    models.Base.metadata.create_all(bind=engine)

def seed_salary_data():
    df = pd.read_csv('nhl_players.csv')
    db = SessionLocal()

    try:
        for _, row in df.iterrows():
            # Create or update player
            player = (
                db.query(models.Player)
                .filter(models.Player.name == row['Player'],
                        models.Player.team == row['Team'],
                        models.Player.position == row['Position'])
                .first()
            )

            if not player:
                player = models.Player(
                    name=row['Player'],
                    team=row['Team'],
                    position=row['Position'],
                )
                db.add(player)
                db.flush() # flush to get player.id

            # Add salary
            salary = models.PlayerSalary(
                player_id=player.id,
                salary=row['pv'],
                updated_at=datetime.now(),
            )
            db.add(salary)

        db.commit()
        print(f"Successfully seeded {len(df)} player salaries")

    except Exception as e:
        db.rollback()
        print(f"Error seeding player salaries: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding salary data...")
    seed_salary_data()