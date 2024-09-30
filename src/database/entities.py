import enum
from sqlalchemy import (
    Table,
    Column,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    MetaData,
    create_engine,
    Enum
)

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from sqlalchemy import URL
from datetime import datetime, UTC

from src.domain.models import Permission





metadata = MetaData()

database_url = URL.create(
    drivername='mysql+aiomysql',
    username='root',
    password='I*2021t1201',
    host='localhost',
    database='markit',
)

sync_database_url = URL.create(
    drivername='mysql+pymysql',
    username='root',
    password='I*2021t1201',
    host='localhost',
    database='markit',
)


def default_uuid() -> str:
    import uuid
    return str(uuid.uuid4())

def default_created_at() -> datetime:
    return datetime.now(UTC)


users = Table(
    'users', metadata,
    Column('id', String(100), primary_key=True, default=default_uuid),
    Column('name', String(50), nullable=False),
    Column('email', String(100), nullable=False, unique=True),
    Column('password_hash', String(255), nullable=False),
    Column('created_at', DateTime, default=default_created_at)
)


calendars = Table(
    'calendars', metadata,
    Column('id', String(100), primary_key=True, default=default_uuid),
    Column('user_id', String(100), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('name', String(100), nullable=False),
    Column('created_at', DateTime, default=default_created_at),
    Column('public', Boolean, default=False),
)


events = Table(
    'events', metadata,
    Column('id', String(100), primary_key=True, default=default_uuid),
    Column('calendar_id', String(100), ForeignKey('calendars.id', ondelete='CASCADE'), nullable=False),
    Column('title', String(100), nullable=False),
    Column('description', Text, nullable=True),
    Column('start_time', DateTime, nullable=False),
    Column('end_time', DateTime, nullable=False),
    Column('is_recurring', Boolean, default=False),
    Column('created_at', DateTime, default=default_created_at)
)

sharing = Table(
    'sharing', metadata,
    Column('id', String(100), primary_key=True, default=default_uuid),
    Column('permissions', Enum(Permission), primary_key=True, default=default_uuid),
    Column('calendar_id', String(100), ForeignKey('calendars.id', ondelete='CASCADE')),
    Column('shared_with_id', String(100), ForeignKey('users.id', ondelete='CASCADE')),
    Column('public', Boolean, default=False),
)


engine = create_async_engine(database_url)
sync_engine = create_engine(sync_database_url)


AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
