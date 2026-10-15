from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy_utils.types import ChoiceType

#criação da conexão com o banco de dados SQLite
db = create_engine("sqlite:///database.db")

#criação da base de dados
Base = declarative_base()

#criação das tabelas/classes do banco de dados
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    admin = Column(Boolean, default=False) 

    def __init__(self, name: str, email: str, password: str, active: bool = True, admin: bool = False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    color = Column(String, nullable=False)
    mileage = Column(Integer, nullable=False)

    def __init__(self, make: str, model: str, year: int, price: float, color: str, mileage: int):
        self.make = make
        self.model = model
        self.year = year
        self.price = price
        self.color = color
        self.mileage = mileage

class Order(Base):
    __tablename__ = "orders"

    """ status_order = [
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('CANCELED', 'CANCELED')
    ] """

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    order_date = Column(DateTime, default=datetime.utcnow)
    car = relationship("Car", backref="orders")   
    client = relationship("Client", backref="orders")

    def __init__(self, user_id: int, car_id: int, client_id: int, total_price: float=0.0, status='PENDING'):
        self.user_id = user_id
        self.car_id = car_id
        self.client_id = client_id
        self.total_price = total_price
        self.status = status
        self.order_date = datetime.utcnow()

    def calculate_price(self, discount: float, car: Car):
        calculated_price = (car.price * (1 - discount / 100))
        self.total_price = calculated_price

    @property    
    def car_price(self):
        return self.car.price

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    document = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)

    def __init__(self, name: str, document: str, email: str, phone: str):
        self.name = name
        self.document = document
        self.email = email
        self.phone = phone


#criar a migração: alembic revision --autogenerate -m "Initial migration"
#executar a migração: alembic upgrade head