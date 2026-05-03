# Product-Agnostic Aggregator (FastAPI)

A FastAPI-based aggregator platform for classified listings (e.g., bikes, cameras) with:

- Product-family-aware taxonomy and attributes
- Location hierarchy (state -> district -> city)
- Filterable public listings endpoint
- Listing detail endpoint with source URL support
- Basic admin pages for listings, taxonomies, and attributes
- Setup script to bootstrap any product family and attributes

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup_aggregator.py --product bikes --attributes brand,model,year,price,cc,mileage,features,owners,km_run
uvicorn app.main:app --reload
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Admin UI: `http://127.0.0.1:8000/admin`

## Setup for another product family

```bash
python scripts/setup_aggregator.py --product cameras --attributes brand,model,megapixels,sensor_type,price,features
```

This creates the product family and attribute definitions without locking schema to any one product category.
