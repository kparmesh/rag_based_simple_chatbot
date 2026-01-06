"""
Script to seed fake data for testing purposes.
"""
from sqlalchemy.orm import Session
from backend.db.models import User, Submission
from backend.db.session import engine, SessionLocal


# Fake user data
FAKE_USERS = [
    {"email": "john.doe@example.com", "password": "password123"},
    {"email": "jane.smith@example.com", "password": "password123"},
    {"email": "bob.wilson@example.com", "password": "password123"},
    {"email": "alice.brown@example.com", "password": "password123"},
    {"email": "charlie.johnson@example.com", "password": "password123"},
]

# Fake questionnaire titles
QUESTIONNAIRE_TITLES = [
    "Living Will",
    "Mirror will",
    "Single Will - Scotland",
    "LPA Health & Welfare - Scotland",
    "Executor Toolkit Plus",
    "Executor Toolkit",
]

# Fake submission data templates
FAKE_SUBMISSIONS_TEMPLATE = [
    {"questionnaire_title": "Living Will", "step": 1, "is_complete": False},
    {"questionnaire_title": "Living Will", "step": 2, "is_complete": False},
    {"questionnaire_title": "Living Will", "step": 3, "is_complete": True},
    {"questionnaire_title": "Mirror will", "step": 1, "is_complete": True},
    {"questionnaire_title": "Mirror will", "step": 2, "is_complete": False},
    {"questionnaire_title": "Single Will - Scotland", "step": 1, "is_complete": False},
    {"questionnaire_title": "LPA Health & Welfare - Scotland", "step": 1, "is_complete": True},
    {"questionnaire_title": "LPA Health & Welfare - Scotland", "step": 2, "is_complete": True},
    {"questionnaire_title": "Executor Toolkit Plus", "step": 1, "is_complete": True},
    {"questionnaire_title": "Executor Toolkit", "step": 1, "is_complete": True},
    {"questionnaire_title": "Executor Toolkit", "step": 1, "is_complete": False},
    {"questionnaire_title": "Executor Toolkit Plus", "step": 2, "is_complete": False},
]


def seed_fake_data(force: bool = False):
    """
    Seed the database with fake users and submissions.
    
    Args:
        force: If True, clear existing data and reseed.
    """
    # Create a new session
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0 and not force:
            print(f"Database already has {existing_users} users. Use --force to reseed.")
            return
        
        if existing_users > 0 and force:
            # Clear existing submissions and users
            db.query(Submission).delete()
            db.query(User).delete()
            db.commit()
            print("Cleared existing data.")
        
        print("Seeding fake data...")
        
        # Create fake users
        created_users = []
        for user_data in FAKE_USERS:
            user = User(
                email=user_data["email"],
                hashed_password=user_data["password"]  # Plain text password as per existing code
            )
            db.add(user)
            created_users.append(user)
        
        db.commit()
        print(f"Created {len(created_users)} fake users")
        
        # Create fake submissions
        submissions_count = 0
        for i, submission_template in enumerate(FAKE_SUBMISSIONS_TEMPLATE):
            # Distribute submissions across users (round-robin)
            user = created_users[i % len(created_users)]
            
            submission = Submission(
                user_id=user.id,
                questionnaire_title=submission_template["questionnaire_title"],
                step=submission_template["step"],
                is_complete=submission_template["is_complete"]
            )
            db.add(submission)
            submissions_count += 1
        
        db.commit()
        print(f"Created {submissions_count} fake submissions")
        print("Fake data seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding fake data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    seed_fake_data(force=force)

