from json import dumps as json_dumps

from golemgpt.settings import Settings
from golemgpt.utils.http import http_request

BRAVE_SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"


def search_text_via_brave_action(query: str, **kwargs) -> str:
    """Search online via Brave Search API, text only."""
    settings: Settings = kwargs["golem"].settings
    api_key = settings.BRAVE_SEARCH_API_KEY
    assert api_key, "Error: no BRAVE_SEARCH_API_KEY environment variable"
    client = BraveSearchClient(api_key)
    results = client.search(query)
    return json_dumps(results)


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
            "X-Subscription-Token": self.api_key
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
        raw_results = http_request(
            "GET",
            self.endpoint,
            headers=headers,
            fields=params,
            json_result=True,
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
            formatted_results.append({
                "title": item["title"],
                "url": item["url"],
                "description": item["description"]
            })

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
