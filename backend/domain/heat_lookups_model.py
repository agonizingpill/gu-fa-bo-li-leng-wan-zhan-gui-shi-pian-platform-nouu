from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


heat_lookups = Table('heat_lookups', metadata,
    Column('code', String(64), primary_key=True),
    Column('profile', String(160), ForeignKey('profiles.code'), nullable=False),
    Column('thick', Float, nullable=False),
    Column('target', Float, nullable=False),
    Column('measured', Float, nullable=False),
    # 无解时炉温留空：不给炉温
    Column('heat', Float, nullable=True),
    Column('candidates', JSON, nullable=False),
    Column('usual_heat', Float, nullable=False),
    Column('state', String(160), nullable=False),
    Column('reason', String(320), nullable=True),
    CheckConstraint('thick > 0'),
    CheckConstraint('target > 0'),
    CheckConstraint('measured >= 0'),
)
