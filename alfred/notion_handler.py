from notion_client import Client

from alfred.utils import (
    read_env_var,
)


class NotionHandler:
    def __init__(self):
        notion_secret = read_env_var("NOTION_SECRET")
        self._database_id = read_env_var("NOTION_DB_ID")
        self._client = Client(auth=notion_secret)

    def get_database_data(self):
        return self._client.databases.query(database_id=self._database_id)  # type: ignore


notion_handler = NotionHandler()
