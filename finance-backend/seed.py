from datetime import datetime, timedelta, timezone
from database import SessionLocal, engine, Base
import models 

from models.user import User, UserRole
from models.transaction import Transaction, TransactionType
from utils.hashing import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Clear existing data ────────────────────────────────────────────────────────
db.query(Transaction).delete()
db.query(User).delete()
db.commit()

# ── Create users ───────────────────────────────────────────────────────────────
admin = User(
    name="Admin User",
    email="admin@example.com",
    hashed_password=hash_password("admin123"),
    role=UserRole.admin,
)
analyst = User(
    name="Analyst User",
    email="analyst@example.com",
    hashed_password=hash_password("analyst123"),
    role=UserRole.analyst,
)
viewer = User(
    name="Viewer User",
    email="viewer@example.com",
    hashed_password=hash_password("viewer123"),
    role=UserRole.viewer,
)

db.add_all([admin, analyst, viewer])
db.commit()
db.refresh(admin)

# ── Create transactions ────────────────────────────────────────────────────────
now = datetime.now(timezone.utc)

transactions = [
    Transaction(amount=5000.00,  type=TransactionType.income,  category="Salary",       date=now - timedelta(days=1),  notes="Monthly salary",          created_by=admin.id),
    Transaction(amount=1200.00,  type=TransactionType.income,  category="Freelance",    date=now - timedelta(days=5),  notes="Web design project",      created_by=admin.id),
    Transaction(amount=300.00,   type=TransactionType.expense, category="Utilities",    date=now - timedelta(days=3),  notes="Electricity bill",        created_by=admin.id),
    Transaction(amount=150.00,   type=TransactionType.expense, category="Groceries",    date=now - timedelta(days=2),  notes="Weekly groceries",        created_by=admin.id),
    Transaction(amount=800.00,   type=TransactionType.expense, category="Rent",         date=now - timedelta(days=10), notes="Monthly rent",            created_by=admin.id),
    Transaction(amount=250.00,   type=TransactionType.income,  category="Investments",  date=now - timedelta(days=15), notes="Dividend payout",         created_by=admin.id),
    Transaction(amount=90.00,    type=TransactionType.expense, category="Subscriptions",date=now - timedelta(days=7),  notes="Streaming + cloud tools", created_by=admin.id),
    Transaction(amount=2000.00,  type=TransactionType.income,  category="Salary",       date=now - timedelta(days=32), notes="Previous month salary",   created_by=admin.id),
    Transaction(amount=400.00,   type=TransactionType.expense, category="Travel",       date=now - timedelta(days=20), notes="Flight tickets",          created_by=admin.id),
    Transaction(amount=60.00,    type=TransactionType.expense, category="Groceries",    date=now - timedelta(days=9),  notes="Weekend shopping",        created_by=admin.id),
]

db.add_all(transactions)
db.commit()

print("✅ Seed complete.")
print()
print("Test accounts:")
print("  admin@example.com   / admin123   (role: admin)")
print("  analyst@example.com / analyst123 (role: analyst)")
print("  viewer@example.com  / viewer123  (role: viewer)")
