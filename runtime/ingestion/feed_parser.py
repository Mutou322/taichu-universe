# runtime/ingestion/feed_parser.py


class FeedParser:

    async def parse(self, raw_data):

        if isinstance(raw_data, bytes):
            return raw_data.decode("utf-8", errors="replace")

        if isinstance(raw_data, str):
            return raw_data

        return str(raw_data)
