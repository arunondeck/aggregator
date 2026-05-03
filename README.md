# Product-Agnostic Aggregator (FastAPI + SEO-friendly SSR frontend)

A FastAPI-based aggregator platform for classified listings (e.g., bikes, cameras) with:

- Product-family-aware taxonomy and attributes
- Location hierarchy (state -> district -> city)
- Filterable public listings endpoint
- Listing detail endpoint with source URL support
- SEO-friendly server-rendered frontend listing pages
- Basic admin pages for listings, taxonomies, and attributes
- Setup script to bootstrap any product family + frontend

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup_aggregator.py --product bikes --attributes brand,model,year,price,cc,mileage,features,owners,km_run --with-frontend
uvicorn app.main:app --reload
```

Open:
- Home UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`
- Admin UI: `http://127.0.0.1:8000/admin`

## Home frontend features

- Latest listings and location-aware listing view
- Location selector at top: state -> district -> locality narrowing
- "View all from state" and "View all from district" options
- Popular geolocations and brands cards
- Quick criteria links (e.g., all listings under 2000)
- Filter and sort support (date/price asc/desc)
- Dynamic filter values sourced from current listings + attribute definitions in DB

## Setup for another product family

```bash
python scripts/setup_aggregator.py --product cameras --attributes brand,model,megapixels,sensor_type,price,features --with-frontend
```

This creates the product family and attribute definitions without locking schema to any one product category.
