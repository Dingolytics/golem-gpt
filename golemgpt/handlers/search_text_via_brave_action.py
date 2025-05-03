from json import dumps as json_dumps

from golemgpt.handlers.base import BaseHandler, BaseOutput, BaseParams
# from golemgpt.utils.http import get_content_type, is_http_url
# from golemgpt.utils.misc import workpath
from golemgpt.utils.http import http_request_as_json

BRAVE_SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"


class SearchTextParams(BaseParams):
    query: str
    page_size: int = 20
    page_offset: int = 0
    # search_lang: str | None = None,
    # country: str | None = None,


class SearchTextHandler(BaseHandler[SearchTextParams]):
    params_cls = SearchTextParams

    description = (
        "Search online via Brave Search API, text only, "
        "with pagination options."
    )

    def __init__(self, api_key: str) -> None:
        super().__init__()
        assert api_key, "Error: no `brave_search_api_key` provided"
        self.api_key = api_key
        self.client = BraveSearchClient(self.api_key)

    def do_action(self, params: SearchTextParams | None) -> BaseOutput:
        assert params
        search_results = self.client.search(
            query=params.query,
            count=params.page_size,
            offset=params.page_offset,
        )
        return BaseOutput(result=json_dumps(search_results))


class BraveSearchClient:
    def __init__(
        self,
        api_key: str,
        endpoint: str = BRAVE_SEARCH_API_URL,
    ) -> None:
        self.api_key = api_key
        self.endpoint = endpoint

    def search(
        self,
        query: str,
        count: int = 20,
        offset: int = 0,
        search_lang: str | None = None,
        country: str | None = None,
    ) -> list:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": count,
            "offset": offset,
        }
        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        raw_results = http_request_as_json(
            "GET",
            self.endpoint,
            headers=headers,
            fields=params,
        )
        formatted_results = []
        # 'query', 'mixed', 'type', 'web'
        # raise Exception(raw_results.keys())

        # print(raw_results["query"])
        # {'original': 'Python API client example',
        # 'show_strict_warning': False, 'is_navigational': False,
        # 'is_news_breaking': False, 'spellcheck_off': True, 'country': 'us',
        # 'bad_results': False, 'should_fallback': False, 'postal_code': '',
        # 'city': '', 'header_country': '', 'more_results_available': True,
        # 'state': ''}

        # ['title', 'url', 'is_source_local', 'is_source_both', 'description',
        # 'page_age', 'profile', 'language', 'family_friendly', 'type', 'subtype',
        # 'is_live', 'meta_url', 'thumbnail', 'age', 'extra_snippets']

        for item in raw_results.get("web", {}).get("results", []):
            formatted_results.append(
                {
                    "title": item["title"],
                    "url": item["url"],
                    "description": item["description"],
                }
            )

        return formatted_results


if __name__ == "__main__":
    import os

    api_key = os.environ.get("BRAVE_SEARCH_API_KEY")
    assert api_key, "Error: no BRAVE_SEARCH_API_KEY environment variable"

    client = BraveSearchClient(api_key)
    query = "Python API client example"
    results = client.search(query)

    for idx, result in enumerate(results):
        print(
            f"{idx + 1}. {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Description: {result['description']}\n"
        )
