from json import dumps as json_dumps

from golemgpt.settings import Settings
from golemgpt.utils.http import http_request

BING_IMAGES_API_URL = "https://api.bing.microsoft.com/v7.0/images/search"


def search_images_via_bing_action(query: str, **kwargs) -> str:
    """Search images online via Bing Search API."""
    settings: Settings = kwargs["golem"].settings
    api_key = settings.BING_SEARCH_API_KEY
    assert api_key, "Error: no BING_SEARCH_API_KEY environment variable"
    client = BingImageSearchClient(api_key)
    results = client.search_images(query)
    return json_dumps(results)


class BingImageSearchClient:
    def __init__(self, api_key: str, endpoint: str = BING_IMAGES_API_URL):
        self.api_key = api_key
        self.endpoint = endpoint

    def search_images(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        market="en-US",
        safe_search="Moderate",
    ) -> dict:
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": count,
            "offset": offset,
            "mkt": market,
            "safeSearch": safe_search,
        }
        raw_results = http_request(
            "GET",
            self.endpoint,
            headers=headers,
            fields=params,
            json_result=True,
        )
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
    client = BingImageSearchClient(api_key)
    query = "Modern trains"

    results = client.search_images(query)

    for idx, result in enumerate(results):
        print(
            f"{idx + 1}. {result['name']}\n"
            f"Content URL: {result['content_url']}\n"
            f"Thumbnail URL: {result['thumbnail_url']}\n"
            f"Host Page URL: {result['host_page_url']}\n"
        )
