# config.py

import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, Float, TIMESTAMP, ForeignKey, Table, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url, pool_size=30, max_overflow=20)

Base = declarative_base()

# Association table for the many-to-many relationship
watchlist_token_association = Table('watchlist_token_association', Base.metadata,
    Column('watchlist_id', Integer, ForeignKey('watchlist.id'), primary_key=True),
    Column('token_id', Integer, ForeignKey('tokens.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    is_authenticated = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    role = Column(Enum('admin', 'user', name='user_roles'), nullable=False)  # Restrict input to 'admin' or 'user'
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now)

    def as_dict(self):
        exclude_columns = ['password_hash']
        return {column.name: getattr(self, column.name) for column in self.__table__.columns if column.name not in exclude_columns}
    
    def get_id(self):
        return str(self.id)
    

class Watchlist(Base):
    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, default=None)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now)

    # Relationship to Token class
    tokens = relationship('Token', secondary=watchlist_token_association, back_populates='watchlists')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gecko_id = Column(String, nullable=False)
    logo = Column(String, default=None)
    tokenname = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    analysis_1 = Column(String, default=None)
    analysis_2 = Column(String, default=None)
    tvl = Column(Float, default=None)
    reward_rate = Column(Float, default=None)
    inflation_rate = Column(Float, default=None)
    annualized_revenue_fee = Column(Float, default=None)
    whitepaper = Column(String, default=None)
    ath = Column(Float, default=None)
    ath_change_percentage = Column(Float, default=None)
    categories = Column(String, default=None)
    chains = Column(String, default=None)
    coingecko_link = Column(String, default=None)
    contracts = Column(String, default=None)
    current_price = Column(Float, default=None)
    fully_diluted_valuation = Column(Float, default=None)
    market_cap_usd = Column(Float, default=None)
    max_supply = Column(Float, default=None)
    circulating_supply = Column(Float, default=None)
    percentage_circulating_supply = Column(Float, default=None)
    price_a_year_ago = Column(Float, default=None)
    price_change_percentage_1y = Column(Float, default=None)
    success = Column(String, default=None)
    supply_model = Column(String, default=None)
    total_supply = Column(Float, default=None)
    total_volume = Column(Float, default=None)
    website = Column(String, default=None)
    description = Column(String, default=None)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now)

    # Relationship to Watchlist class
    watchlists = relationship('Watchlist', secondary=watchlist_token_association, back_populates='tokens')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
session = Session()


# Creates a default watchlist
def create_default_watchlist(name, description=None):
    existing_watchlist = session.query(Watchlist).filter(Watchlist.name == name).first()
    if existing_watchlist:
        return existing_watchlist.as_dict()

    watchlist = Watchlist(name=name, description=description)
    session.add(watchlist)
    session.commit()
    print('---Default watchlist created---')
    return watchlist


# Creates a default admin user
def create_default_admin(username, email, role, password):
    existing_default_admin = session.query(User).filter(User.username == username).first()
    if existing_default_admin:
        return existing_default_admin.as_dict()

    new_admin = User(username=username,
                     email=email,
                     role=role,
                     password_hash=password
                     )
    session.add(new_admin)
    session.commit()
    print('---Default admin user created---')
    return 'Default admin user created'


# Executes default records
create_default_watchlist(name="standard", description="This watchlist contains tokens with no specific category")
