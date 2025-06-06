import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.db.base import Base
from app.models import (
    customer,
    invoice,
    charge,
    payment_intent,
    payment_method,
    price,
    products,
    subscription
)

from app.utils.env_loader import load_project_env
from app.utils.db_url import get_database_url

# ============ ENV SETUP ============
load_project_env()
ENV = os.getenv("ENV", "DEV").upper()

# ============ DATABASE SETUP ============
db_url = get_database_url()
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============ MODELS ============
MODELS = [
    customer.Customer,
    invoice.Invoice,
    charge.Charge,
    payment_intent.PaymentIntent,
    payment_method.PaymentMethod,
    price.Price,
    products.Product,
    subscription.Subscription
]

# ============ SERIALIZATION ============
def serialize(model_obj):
    return {
        c.name: getattr(model_obj, c.name)
        for c in model_obj.__table__.columns
    }

# ============ DUMP FUNCTION ============
def dump_to_json():
    session = SessionLocal()
    dump_data = {}
    try:
        for model in MODELS:
            table_name = model.__tablename__
            records = session.query(model).all()
            dump_data[table_name] = [serialize(r) for r in records]
    finally:
        session.close()

    dump_dir = os.path.join("data", "db_dump")
    os.makedirs(dump_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(dump_dir, f"db_dump_{ENV.lower()}_{timestamp}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dump_data, f, indent=2, default=str)

    print(f"✅ Dump saved to: {filename}")

# ============ ENTRYPOINT ============
if __name__ == "__main__":
    print(f"🚀 Running database dump in ENV={ENV}")
    dump_to_json()
