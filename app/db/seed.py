from app.db.database import SessionLocal, create_tables
from app.models.user import Permission, Role, User
from app.models.document import Document  
from app.core.security import get_password_hash


DEFAULT_PERMISSIONS = [
    ("documents:upload", "Upload financial documents"),
    ("documents:read", "View documents"),
    ("documents:edit", "Edit document metadata"),
    ("documents:delete", "Delete documents"),
    ("documents:review", "Review and annotate documents"),
    ("rag:index", "Generate and manage embeddings"),
    ("rag:search", "Perform semantic search"),
    ("users:manage", "Manage users and roles"),
]


DEFAULT_ROLES = {
    "Admin": {
        "description": "Full system access",
        "permissions": [p[0] for p in DEFAULT_PERMISSIONS],
    },
    "Analyst": {
        "description": "Upload and edit documents",
        "permissions": ["documents:upload", "documents:read", "documents:edit", "rag:index", "rag:search"],
    },
    "Auditor": {
        "description": "Review documents",
        "permissions": ["documents:read", "documents:review", "rag:search"],
    },
    "Client": {
        "description": "View company documents",
        "permissions": ["documents:read"],
    },
}


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # Create permissions
        perm_map = {}
        for name, description in DEFAULT_PERMISSIONS:
            existing = db.query(Permission).filter(Permission.name == name).first()
            if not existing:
                perm = Permission(name=name, description=description)
                db.add(perm)
                db.flush()
                perm_map[name] = perm
            else:
                perm_map[name] = existing

        db.commit()

        # Create roles
        role_map = {}
        for role_name, config in DEFAULT_ROLES.items():
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                role = Role(name=role_name, description=config["description"])
                role.permissions = [perm_map[p] for p in config["permissions"]]
                db.add(role)
                db.flush()
                role_map[role_name] = role
                print(f"Created role: {role_name}")
            else:
                role_map[role_name] = existing
                print(f"Role exists: {role_name}")

        db.commit()

        # Create default admin user
        admin_username = "admin"
        if not db.query(User).filter(User.username == admin_username).first():
            admin = User(
                email="admin@example.com",
                username=admin_username,
                hashed_password=get_password_hash("Admin@1234"),
                full_name="System Administrator",
                is_active=True,
            )
            admin.roles = [role_map["Admin"]]
            db.add(admin)
            db.commit()
            print(f"Created admin user: {admin_username} / Admin@1234")
        else:
            print("Admin user already exists")

        print("\nDatabase seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
