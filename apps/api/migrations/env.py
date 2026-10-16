from alembic import context
from sqlalchemy import create_engine, event

from app.storage import Base, epoch_microseconds

engine = create_engine(
    context.config.get_main_option("sqlalchemy.url"), connect_args={"timeout": 15}
)


@event.listens_for(engine, "connect")
def configure_sqlite(connection, _):
    # pysqlite skips BEGIN before DDL; take manual control so each revision is atomic.
    connection.isolation_level = None
    connection.create_function("spatial_epoch_us", 1, epoch_microseconds, deterministic=True)
    connection.execute("PRAGMA busy_timeout=15000")


@event.listens_for(engine, "begin")
def begin_immediate(connection):
    connection.exec_driver_sql("BEGIN IMMEDIATE")


try:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            transactional_ddl=True,
            transaction_per_migration=True,
        )
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
