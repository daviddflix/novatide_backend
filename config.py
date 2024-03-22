# config.py

import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float
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

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gecko_id = Column(String, nullable=False)
    tokenname = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    analysis = Column(String, default=None)
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


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
session = Session()