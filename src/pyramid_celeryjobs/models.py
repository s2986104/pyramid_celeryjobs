from sqlalchemy import Column, ForeignKey, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import MetaData


# Recommended naming convention used by Alembic, as various different database
# providers will auto-generate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


class Job(Base):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    job_id = Column(Text, unique=True)  # TODO: wants index

    args = Column(JSON)

    state = Column(Text)  # TODO: enum or int?
    msg = Column(JSON)

    # timestamps ... started, finished etc...
    # job type?

    # TODO: non null
    owner = Column(Text)

    # celery task ids
    task_ids = Column(JSON)


# Index('my_index', MyModel.name, unique=True, mysql_length=255)

configure_mappers()
