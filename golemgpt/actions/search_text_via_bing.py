from json import dumps as json_dumps

from golemgpt.settings import Settings
from golemgpt.utils.http import http_request

BING_SEARCH_API_URL = "https://api.bing.microsoft.com/v7.0/search"


def search_text_via_bing_action(query: str, **kwargs) -> str:
    """Search online via Bing Search API, text only."""
    settings: Settings = kwargs["golem"].settings
    api_key = settings.BING_SEARCH_API_KEY
    assert api_key, "Error: no BING_SEARCH_API_KEY environment variable"
    client = BingSearchClient(api_key)
    results = client.search(query)
    return json_dumps(results)


class BingSearchClient:
    def __init__(
        self,
        api_key: str,
        endpoint: str = BING_SEARCH_API_URL,
    ) -> None:
        self.api_key = api_key
        self.endpoint = endpoint

    def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        market="en-US",
    ) -> dict:
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        params = {
            "q": query,
            "count": count,
            "offset": offset,
            "mkt": market
        }
        raw_results = http_request(
            "GET",
            self.endpoint,
            headers=headers,
            fields=params,
            json_result=True,
        )
        formatted_results = []
        for item in raw_results.get('webPages', {}).get('value', []):
            formatted_results.append({
                'name': item['name'],
                'url': item['url'],
                'snippet': item['snippet']
            })
        return formatted_results

        formatted_results = []
        for item in raw_results.get("value", []):
            formatted_results.append(
                {
                    "name": item["name"],
                    "content_url": item["contentUrl"],
                    "thumbnail_url": item["thumbnailUrl"],
                    "host_page_url": item["hostPageUrl"],
                }
            )
        return formatted_results


if __name__ == "__main__":
    import os

    api_key = os.environ.get("BING_SEARCH_API_KEY")
    assert api_key, "Error: no BING_SEARCH_API_KEY environment variable"

    client = BingSearchClient(api_key)
    query = "Python API client example"
    results = client.search(query)

    for idx, result in enumerate(results):
        print(
            f"{idx + 1}. {result['name']}\n"
            f"URL: {result['url']}\n"
            f"Snippet: {result['snippet']}\n"
        )
