from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

from config import get_settings

settings = get_settings()

def build_database_url() -> URL:
    return URL.create(
        drivername="postgresql+asyncpg", # Or "postgresql" for synchronous
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD.get_secret_value(), # Securely extract string
        host=settings.POSTGRES_SERVER,
        database=settings.POSTGRES_DB,
            )

# 1. Create the engine
# Modern Production Engine Configuration
def create_database_engine() -> AsyncEngine:
    """
    Creates and configures the global production-ready AsyncEngine.
    """
    return create_async_engine(
        build_database_url(),
        echo=settings.DEBUG,          # Set to False in production for performance

        # --- POOL SIZING & OVERFLOW ---
        pool_size=settings.POOL_SIZE,  # Base pool size per application worker
        max_overflow=settings.MAX_OVERFLOW,  # Temporary extra connections allowed during traffic spikes

        # --- CONNECTION HEALTH & RESILIENCY ---
        pool_pre_ping=True,           # Ensures stale connections are recycled, Self-healing: tests connections before giving them to the app
        pool_recycle=1800,            # Highly recommended: recycles connections, Prevents stale/dropped connections by recycling them every 30 mins

        # --- TIMEOUT & FAIL-SAFE PROTECTION ---
        pool_timeout=30,         # Maximum seconds to wait for a free connection before throwing an error
    
        # --- PERFORMANCE OPTIMIZATION ---
        future=True,              # Ensures total compatibility with strict SQLAlchemy 2.0+ architecture

        connect_args={

            # Sets a server-side timeout: cancels any query taking longer than 10 seconds
            "server_settings": {
                "statement_timeout": "10000"  # 10,000 milliseconds
            },

            # Minimizes network overhead by tweaking TCP settings
            "command_timeout": 11, 

            # Enforces SSL encryption (required for Neon)
            "ssl": "require",
        }
    )

# Instantiate it once at the module level or inside a dependency injection container
engine = create_database_engine()

# 2. Create the session maker (Industry Standard Configuration)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# FastAPI Dependency / Context Manager pattern
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        # No explicit commit or rollback needed here. 
        # SQLAlchemy handles errors, rollbacks, and closure automatically.