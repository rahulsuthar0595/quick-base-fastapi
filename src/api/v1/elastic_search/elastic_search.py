from elasticsearch import AsyncElasticsearch

from config.config import settings
from logger.logger import logger


class ElasticSearchClient:

    def __init__(self, index_name):
        self.client = AsyncElasticsearch(hosts=[settings.ELASTIC_SEARCH_HOST])
        self.index_name = index_name

    async def index_document(self, doc_id: int, document: dict):
        res = await self.client.index(index=self.index_name, id=str(doc_id), document=document)
        logger.info(f"Index created for user id {doc_id} with response - {res}")

    async def create_index(self, schema):
        is_indices_exists = await self.client.indices.exists(index=self.index_name)
        if not is_indices_exists:
            res = await self.client.indices.create(index=self.index_name, body=schema)
            logger.info(f"{self.index_name} index created successfully - {res}.")
            return res
        else:
            logger.warning(f"{self.index_name} index already exists.")

    async def fetch_all_users(self, limit: int):
        response = await self.client.search(index=self.index_name, body={
            "query": {"match_all": {}},
            "size": limit
        })
        users = [hit["_source"] for hit in response["hits"]["hits"]]
        return users

    async def delete_indices(self):
        await self.client.indices.delete(index=self.index_name, ignore=[400, 404], ignore_unavailable=True)
