import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse

from app.database import Base, SessionLocal, engine
from app.models import AttributeDefinition, ProductFamily


def to_label(key: str) -> str:
    return key.replace("_", " ").strip().title()


def infer_type(key: str) -> str:
    numeric_like = {"year", "price", "cc", "mileage", "owners", "km_run", "megapixels"}
    return "number" if key in numeric_like else "text"


def bootstrap(product: str, attributes: list[str]):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        fam = db.query(ProductFamily).filter(ProductFamily.slug == product).first()
        if not fam:
            fam = ProductFamily(slug=product, name=product.replace("_", " ").title())
            db.add(fam)
            db.flush()

        existing = {a.key for a in db.query(AttributeDefinition).filter(AttributeDefinition.product_family_id == fam.id).all()}
        for key in attributes:
            key = key.strip()
            if not key or key in existing:
                continue
            db.add(
                AttributeDefinition(
                    product_family_id=fam.id,
                    key=key,
                    label=to_label(key),
                    data_type=infer_type(key),
                    filterable=True,
                )
            )
        db.commit()
        print(f"Setup complete for '{product}'.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup product family and attributes for aggregator")
    parser.add_argument("--product", required=True, help="Product family slug (e.g., bikes, cameras)")
    parser.add_argument("--attributes", required=True, help="Comma-separated keys")
    args = parser.parse_args()

    attrs = [x.strip() for x in args.attributes.split(",") if x.strip()]
    bootstrap(args.product.strip(), attrs)
