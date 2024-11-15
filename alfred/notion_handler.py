from typing import Any, List

from asgiref.sync import async_to_sync
from notion_client import Client, helpers
from notion_client.typing import SyncAsync

from alfred.utils import read_env_var


class NotionHandler:
    def __init__(self, database_id):
        self._database_id = database_id
        notion_secret = read_env_var("NOTION_SECRET")
        self._client = Client(auth=notion_secret)

    def get_database_data(self) -> List[Any]:
        return helpers.collect_paginated_api(
            self._client.databases.query, database_id=self._database_id
        )

    async def add_page_async(self, properties: dict) -> SyncAsync:
        return self._client.pages.create(
            parent={"database_id": self._database_id}, properties=properties
        )

    add_page = async_to_sync(add_page_async)

    def update_page(self, page_id: str, properties: dict) -> SyncAsync:
        return self._client.pages.update(page_id=page_id, properties=properties)
