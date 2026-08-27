from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types, auth, users

# Creates tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Allows the Quasar frontend (a different origin/port, e.g. http://localhost:9000)
# to call this API from the browser. Wide open here since this is a learning
# project with no real users; a production app would restrict allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles)
app.include_router(account_types)
app.include_router(banks)
app.include_router(fee_types)
app.include_router(auth)
app.include_router(users)


# --- Development/demo seed data: create basic roles and demo users if not present ---
def seed_demo():
    from app.database.session import SessionLocal
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        # roles
        is_sqlite = str(engine.url).startswith("sqlite")
        roles_to_add = [('admin', 'Administrator'), ('staff', 'Staff'), ('customer', 'Customer')]
        for idx, (code, name) in enumerate(roles_to_add, start=1):
            if not db.query(Role).filter(Role.role_code == code).first():
                if is_sqlite:
                    # explicitly set id for sqlite to avoid autoincrement edgecases
                    db.add(Role(id=idx, role_code=code, role_name=name))
                else:
                    db.add(Role(role_code=code, role_name=name))
        db.commit()

        # refresh roles to get ids
        admin_role = db.query(Role).filter(Role.role_code == 'admin').first()
        staff_role = db.query(Role).filter(Role.role_code == 'staff').first()
        customer_role = db.query(Role).filter(Role.role_code == 'customer').first()

        # demo users
        def ensure_user(email, name, role_id):
            if not db.query(User).filter(User.email == email).first():
                db.add(User(full_name=name, email=email, hashed_password=hash_password('password123'), role_id=role_id, is_active=True))

        ensure_user('admin@example.com', 'Alex Morgan', admin_role.id)
        ensure_user('staff@example.com', 'Jordan Lee', staff_role.id)
        ensure_user('customer@example.com', 'Taylor Smith', customer_role.id)
        db.commit()
    finally:
        db.close()


seed_demo()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}

    