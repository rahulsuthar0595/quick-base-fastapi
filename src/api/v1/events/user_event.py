import asyncio
from typing import Annotated

from fastapi import Depends
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Session

from database.db_connection import get_db
from logger.logger import logger
from src.api.v1.elastic_search.elastic_search import ElasticSearchClient
from src.api.v1.models.user_models.user import User

from faker import Faker


fake = Faker()

elastic_search_client = ElasticSearchClient(index_name="users_idx")

CommonDB = Annotated[Session, Depends(get_db)]


@listens_for(User, "after_insert")
def create_elastic_search_index_for_user(mapper, connection, target):
    asyncio.create_task(
        elastic_search_client.index_document(
            doc_id=target.id,
            document={
                "id": target.id,
                "full_name": target.full_name,
                "email": target.email,
                "is_active": target.is_active,
                "created_at": target.created_at,
                "updated_at": target.updated_at,
            }
        )
    )


async def create_index():
    """Create a new Elasticsearch index with the required schema."""
    schema = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "full_name": {"type": "text"},
                "email": {"type": "text"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
    }
    await elastic_search_client.create_index(schema)


asyncio.create_task(create_index())


async def generate_bulk_users(count: int = 1000, db: Session = Depends(get_db)):
    try:
        for _ in range(count):
            name = fake.name()
            email = fake.email()
            is_email_exists = True
            while is_email_exists:
                if db.query(User).filter(User.email.ilike(f"%{email}%")).first():
                    email = fake.email()
                    continue
                is_email_exists = False

            user = User(
                full_name=name,
                email=email,
                password=name,
                is_active=True
            )
            db.add(user)
            db.flush()
        db.commit()
        logger.info(f"{count} users created in the database.")
    except Exception as err:
        logger.error(f"Exception while bulk generate user: {str(err)}")
    finally:
        db.close()
