from sqlalchemy import Column, Index, Integer, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from src.core.db import Base   


user_products = Table(
    "user_products",
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id")),
    Column("product_id", ForeignKey("products.id")),
    Column("quantity", Integer, default=1),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="buyer")
    balance = Column(Integer, default=0)
    product_owner = relationship("Product", cascade="all, delete")
    products = relationship('Product', secondary=user_products, back_populates="users", cascade="all, delete")




class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, index=True)
    price = Column(Integer)
    quantity = Column(Integer, default=1)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    users = relationship('User', secondary=user_products, back_populates="products", cascade="all, delete")
    __table_args__ = (
        Index('idx_owner_id_title', 'owner_id', 'title', unique=True),
    )

