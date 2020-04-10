import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from flask_login import UserMixin

Base = declarative_base()

class Owner(Base, UserMixin):
    __tablename__ = 'ownerDetails'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)    
    email = Column(String(250), unique=True)
    password = Column(String(250), nullable=False)
    mobile = Column(String(15), nullable=False)
    address = Column(String(250), nullable=False)
    is_restaurant_user = Column(Boolean, default=False)


class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    owner_id = Column(Integer, ForeignKey('ownerDetails.id'))
    owner = relationship(Owner,backref='restaurants')
    location = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    image = Column(String(250), nullable=False)
    chairs_2 = Column(Integer, nullable = False)
    chairs_3 = Column(Integer, nullable=False)
    chairs_4 = Column(Integer, nullable=False)
    chairs_8 = Column(Integer, nullable= False)


class MenuItem(Base):
    __tablename__ = 'menu_items'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant, backref="menu_items")
    owner_id = Column(Integer, ForeignKey('ownerDetails.id'))
    owner = relationship(Owner)
    image = Column(String(250))

    @property
    def serialize(self):
        #Returns object data in easily serializeable format
        return {            
            'name':self.name,
            'id':self.id,
            'description':self.description,
            'price':self.price,
            'course':self.course,
            'restaurant_id':self.restaurant_id,
            'restaurant':str(self.restaurant)
        }
    

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant, backref="images")

class Waiter(Base):
    __tablename__ = 'waiters'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    image = Column(String(80), nullable=False)
    experience = Column(String(80))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant, backref="waiters")



class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    comment= Column(String(100))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant, backref="ratings")


class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    item_id = Column(Integer, ForeignKey('menu_items.id'))
    item = relationship(MenuItem)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('ownerDetails.id'))
    user = relationship(Owner, backref="cart_items")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    item_id = Column(Integer, ForeignKey('menu_items.id'))
    item = relationship(MenuItem)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('ownerDetails.id'))
    user = relationship(Owner, backref="orders")
        

class ReserveTable(Base):
    __tablename__ = 'reservation'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('ownerDetails.id'))
    user = relationship(Owner, backref="reserved_tables")
    reserved_table_name = Column(String(10),nullable=False)
    date_time = Column(String(30),nullable=False)
    restaurant_id = Column(Integer,ForeignKey('restaurants.id'))
    restaurant = relationship(Restaurant, backref="reserved_tables")

engine = create_engine('sqlite:///restaurantmenu.db')


Base.metadata.create_all(engine)
