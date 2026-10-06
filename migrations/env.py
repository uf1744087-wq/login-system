import asyncio
from logging.config import fileConfig
import ssl

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

# 1. Load config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from database import build_database_url

# Ensure ALL your models are imported somewhere here so Base.metadata knows they exist
from models import Base
import models 

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = build_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Synchronous sync-runner context wrapper."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with adaptive SSL."""
    db_url = str(build_database_url())
    connect_args = {}

    # UNIVERSAL CHANGE: Apply your strict Neon/Prod SSL settings only if requested or in prod
    # You can change this condition to check an env var like: settings.ENV == "production"
    if "sslmode=require" in db_url or "neon" in db_url:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        if hasattr(ssl_context, 'set_channel_binding_cb'):
            ssl_context.set_channel_binding_cb(lambda: 'tls-unique')
            
        connect_args = {
            "ssl": ssl_context,
            "server_settings": {
                "channel_binding": "require"
            }
        }

    connectable = create_async_engine(
        build_database_url(),
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # UNIVERSAL CHANGE: Safe event loop execution (fixes test/runtime environment crashes)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If a loop is already running (e.g. in tests), schedule it
        loop.create_task(run_migrations_online())
    else:
        asyncio.run(run_migrations_online())

