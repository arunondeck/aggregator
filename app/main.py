from collections import Counter, defaultdict

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from .database import Base, engine, get_db
from .models import AttributeDefinition, Listing, ListingAttributeValue, Location, ProductFamily
from .schemas import ListingCreate

app = FastAPI(title="Product Agnostic Aggregator")
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)


def _get_or_create_location(db: Session, state: str, district: str, city: str) -> Location:
    loc = db.scalar(select(Location).where(and_(Location.state == state, Location.district == district, Location.city == city)))
    if loc:
        return loc
    loc = Location(state=state, district=district, city=city)
    db.add(loc)
    db.flush()
    return loc


def _base_listing_query(db: Session):
    return select(Listing).options(
        joinedload(Listing.location),
        joinedload(Listing.product_family),
        joinedload(Listing.attributes).joinedload(ListingAttributeValue.attribute),
    )


@app.post("/api/listings")
def create_listing(payload: ListingCreate, db: Session = Depends(get_db)):
    family = db.scalar(select(ProductFamily).where(ProductFamily.slug == payload.product_family))
    if not family:
        raise HTTPException(status_code=404, detail="Product family not found. Run setup script first.")

    location = _get_or_create_location(db, payload.state, payload.district, payload.city)

    listing = Listing(
        product_family_id=family.id,
        location_id=location.id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        source_name=payload.source_name,
        source_url=payload.source_url,
    )
    db.add(listing)
    db.flush()

    defs = db.scalars(select(AttributeDefinition).where(AttributeDefinition.product_family_id == family.id)).all()
    defs_by_key = {d.key: d for d in defs}

    for key, val in payload.attributes.items():
        attr_def = defs_by_key.get(key)
        if not attr_def or val in (None, ""):
            continue
        db.add(ListingAttributeValue(listing_id=listing.id, attribute_id=attr_def.id, value=str(val)))

    db.commit()
    return {"id": listing.id}


@app.get("/api/listings")
def list_listings(
    product_family: str | None = None,
    state: str | None = None,
    district: str | None = None,
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    brand: str | None = None,
    model: str | None = None,
    year: str | None = None,
    sort_by: str = Query("date_desc", pattern="^(date_asc|date_desc|price_asc|price_desc)$"),
    db: Session = Depends(get_db),
):
    q = _base_listing_query(db)

    if product_family:
        q = q.join(ProductFamily).where(ProductFamily.slug == product_family)
    if state:
        q = q.join(Location).where(Location.state == state)
    if district:
        q = q.join(Location).where(Location.district == district)
    if city:
        q = q.join(Location).where(Location.city == city)
    if min_price is not None:
        q = q.where(Listing.price >= min_price)
    if max_price is not None:
        q = q.where(Listing.price <= max_price)

    listings = db.scalars(q).unique().all()

    def matches_optional_attr(l: Listing, key: str, expected: str | None) -> bool:
        if not expected:
            return True
        attrs = {x.attribute.key: x.value for x in l.attributes}
        return attrs.get(key) == expected

    filtered = []
    for l in listings:
        if not (matches_optional_attr(l, "brand", brand) and matches_optional_attr(l, "model", model) and matches_optional_attr(l, "year", year)):
            continue
        filtered.append(l)

    if sort_by == "date_asc":
        filtered.sort(key=lambda x: x.created_at)
    elif sort_by == "price_asc":
        filtered.sort(key=lambda x: (x.price is None, x.price if x.price is not None else 0))
    elif sort_by == "price_desc":
        filtered.sort(key=lambda x: (x.price is not None, x.price if x.price is not None else -1), reverse=True)
    else:
        filtered.sort(key=lambda x: x.created_at, reverse=True)

    output = []
    for l in filtered:
        attrs = {av.attribute.key: av.value for av in l.attributes if av.value not in (None, "")}
        output.append(
            {
                "id": l.id,
                "product_family": l.product_family.slug,
                "title": l.title,
                "price": l.price,
                "created_at": l.created_at.isoformat() if l.created_at else None,
                "source_name": l.source_name,
                "source_url": l.source_url,
                "location": {"state": l.location.state, "district": l.location.district, "city": l.location.city},
                "attributes": attrs,
            }
        )
    return output


@app.get("/")
def home(
    request: Request,
    product_family: str | None = None,
    state: str | None = None,
    district: str | None = None,
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "date_desc",
    db: Session = Depends(get_db),
):
    all_listings = db.scalars(_base_listing_query(db)).unique().all()

    def in_scope(l: Listing) -> bool:
        if product_family and l.product_family.slug != product_family:
            return False
        if state and l.location.state != state:
            return False
        if district and l.location.district != district:
            return False
        if city and l.location.city != city:
            return False
        if min_price is not None and (l.price is None or l.price < min_price):
            return False
        if max_price is not None and (l.price is None or l.price > max_price):
            return False
        return True

    filtered = [l for l in all_listings if in_scope(l)]

    attr_defs = db.scalars(select(AttributeDefinition).where(AttributeDefinition.filterable.is_(True))).all()
    attr_values: dict[str, set[str]] = defaultdict(set)
    for l in filtered:
        for av in l.attributes:
            if av.value:
                attr_values[av.attribute.key].add(av.value)

    scope_for_geo_cards = [l for l in all_listings if (not product_family or l.product_family.slug == product_family)]
    popular_locations = Counter([l.location.city for l in scope_for_geo_cards]).most_common(5)
    popular_brands = Counter([av.value for l in scope_for_geo_cards for av in l.attributes if av.attribute.key == "brand" and av.value]).most_common(5)

    latest = sorted(filtered, key=lambda x: x.created_at, reverse=True)
    if sort_by == "date_asc":
        latest = sorted(filtered, key=lambda x: x.created_at)
    elif sort_by == "price_asc":
        latest = sorted(filtered, key=lambda x: (x.price is None, x.price if x.price is not None else 0))
    elif sort_by == "price_desc":
        latest = sorted(filtered, key=lambda x: (x.price is not None, x.price if x.price is not None else -1), reverse=True)

    all_locations = db.scalars(select(Location)).all()
    states = sorted({l.state for l in all_locations})
    districts = sorted({l.district for l in all_locations if not state or l.state == state})
    cities = sorted({l.city for l in all_locations if (not state or l.state == state) and (not district or l.district == district)})

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "listings": latest,
            "states": states,
            "districts": districts,
            "cities": cities,
            "state": state,
            "district": district,
            "city": city,
            "product_family": product_family,
            "sort_by": sort_by,
            "min_price": min_price,
            "max_price": max_price,
            "popular_locations": popular_locations,
            "popular_brands": popular_brands,
            "filter_defs": attr_defs,
            "filter_values": {k: sorted(v) for k, v in attr_values.items()},
        },
    )


@app.get("/api/listings/{listing_id}")
def listing_detail(listing_id: int, db: Session = Depends(get_db)):
    listing = db.scalar(
        select(Listing)
        .where(Listing.id == listing_id)
        .options(
            joinedload(Listing.location),
            joinedload(Listing.product_family),
            joinedload(Listing.attributes).joinedload(ListingAttributeValue.attribute),
        )
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    attrs = {av.attribute.label: av.value for av in listing.attributes if av.value not in (None, "")}
    return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "source_name": listing.source_name,
        "source_url": listing.source_url,
        "location": {"state": listing.location.state, "district": listing.location.district, "city": listing.location.city},
        "product_family": listing.product_family.slug,
        "attributes": attrs,
    }


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    families = db.scalars(select(ProductFamily)).all()
    attrs = db.scalars(select(AttributeDefinition)).all()
    listings = db.scalars(
        select(Listing).options(joinedload(Listing.location), joinedload(Listing.product_family), joinedload(Listing.attributes).joinedload(ListingAttributeValue.attribute))
    ).unique().all()
    return templates.TemplateResponse("admin.html", {"request": request, "families": families, "attrs": attrs, "listings": listings})
