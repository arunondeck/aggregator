from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class ProductFamily(Base):
    __tablename__ = "product_families"

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)

    listings = relationship("Listing", back_populates="product_family")
    attributes = relationship("AttributeDefinition", back_populates="product_family")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("state", "district", "city", name="uq_location"),)

    listings = relationship("Listing", back_populates="location")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    product_family_id = Column(Integer, ForeignKey("product_families.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True, index=True)
    source_name = Column(String(120), nullable=False)
    source_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product_family = relationship("ProductFamily", back_populates="listings")
    location = relationship("Location", back_populates="listings")
    attributes = relationship("ListingAttributeValue", back_populates="listing", cascade="all, delete-orphan")


class AttributeDefinition(Base):
    __tablename__ = "attribute_definitions"

    id = Column(Integer, primary_key=True)
    product_family_id = Column(Integer, ForeignKey("product_families.id"), nullable=False)
    key = Column(String(100), nullable=False)
    label = Column(String(150), nullable=False)
    data_type = Column(String(30), default="text")
    filterable = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("product_family_id", "key", name="uq_product_attribute_key"),)

    product_family = relationship("ProductFamily", back_populates="attributes")
    values = relationship("ListingAttributeValue", back_populates="attribute")


class ListingAttributeValue(Base):
    __tablename__ = "listing_attribute_values"

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False, index=True)
    attribute_id = Column(Integer, ForeignKey("attribute_definitions.id"), nullable=False, index=True)
    value = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("listing_id", "attribute_id", name="uq_listing_attribute"),)

    listing = relationship("Listing", back_populates="attributes")
    attribute = relationship("AttributeDefinition", back_populates="values")
