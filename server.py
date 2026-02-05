import logging
from typing import List, Optional

from google_play_scraper import GooglePlayClient, Collection, Category, Age, Sort
from google_play_scraper.models import AppOverview, AppDetails
from mcp.server import FastMCP

from constants.google_play_constants import (
    GOOGLE_PLAY_COUNTRIES,
    GOOGLE_PLAY_LANGUAGES,
    GOOGLE_PLAY_COUNTRIES_WITH_LANGUAGES,
    MAX_GOOGLE_PLAY_TITLE_LENGTH,
    MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH,
    MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH,
)
from constants.mcp_constants import MCP_SERVER_INSTRUCTIONS
from models.google_play import GooglePlayCountryWithLanguages, ReviewsResponse
from models.metadata import MetadataValidationResult, MetadataValidationError
from proxy import proxy_manager

mcp = FastMCP(
    name="aso",
    instructions=MCP_SERVER_INSTRUCTIONS,
    json_response=True,
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logging.getLogger('asyncio').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@mcp.tool(
    name="get-google-play-languages",
    description="Get list of language codes supported by Google Play",
    structured_output=True,
)
async def get_google_play_languages() -> List[str]:
    return GOOGLE_PLAY_LANGUAGES


@mcp.tool(
    name="get-google-play-countries",
    description="Get list of country codes supported by Google Play",
    structured_output=True,
)
async def get_google_play_countries() -> List[str]:
    """
    Get a list of country codes supported by Google Play
    :return:
    """
    return GOOGLE_PLAY_COUNTRIES


@mcp.tool(
    name="get-google-play-countries-with-languages",
    description="Get list of country codes mapped with a list of languages in these countries supported by Google Play",
    structured_output=True,
)
async def get_google_play_countries_with_languages() -> List[GooglePlayCountryWithLanguages]:
    """
    Get a list of country codes mapped with a list of languages in these countries supported by Google Play
    :return: A list of country codes with languages codes
    """
    return GOOGLE_PLAY_COUNTRIES_WITH_LANGUAGES


@mcp.tool(
    name="get-google-play-collections",
    description="Get list of collection types for browsing Google Play Store (TOP_FREE, TOP_PAID, GROSSING)",
    structured_output=True,
)
async def get_google_play_collections() -> List[str]:
    """Get list of available collection types for browsing"""
    return [c.name for c in Collection]


@mcp.tool(
    name="get-google-play-categories",
    description="Get list of app categories in Google Play Store",
    structured_output=True,
)
async def get_google_play_categories() -> List[str]:
    """Get list of available app categories"""
    return [c.name for c in Category]


@mcp.tool(
    name="get-google-play-sort-orders",
    description="Get list of sort orders for reviews (NEWEST, RATING, HELPFULNESS)",
    structured_output=True,
)
async def get_google_play_sort_orders() -> List[str]:
    """Get list of available sort orders for reviews"""
    return [s.name for s in Sort]


@mcp.tool(
    name="get-google-play-age-filters",
    description="Get list of age filters for browsing (FIVE_UNDER, SIX_EIGHT, NINE_UP)",
    structured_output=True,
)
async def get_google_play_age_filters() -> List[str]:
    """Get list of available age filters for browsing"""
    return [a.name for a in Age]


@mcp.tool(
    name="get-google-play-rating-filters",
    description="Get list of valid rating filters for reviews (1-5)",
    structured_output=True,
)
async def get_google_play_rating_filters() -> List[int]:
    """Get list of valid rating filters for reviews"""
    return [1, 2, 3, 4, 5]


@mcp.tool(
    name="google-play-suggest",
    description="Get keywords suggestions for the given keyword in Google Play Store",
    structured_output=True
)
async def google_play_suggest(country: str, language: str, keyword: str) -> List[str]:
    """
    Get keywords suggestions for the given keyword in Google Play Store.
    :param country: Country code
    :param language: Language code
    :param keyword: Keyword to get suggestions for
    :return: A list of keywords suggestions
    """
    max_retries = max(len(proxy_manager.available_proxies), 1) if proxy_manager.has_proxies else 1
    last_error = None

    for attempt in range(max_retries):
        proxy = proxy_manager.get_random_proxy()

        try:
            client = GooglePlayClient(
                country=country,
                lang=language,
                proxies=proxy,
            )
            result = await client.asuggest(term=keyword, lang=language, country=country)
            if proxy:
                proxy_manager.reset_failed()
            return result

        except Exception as e:
            last_error = e
            if proxy:
                proxy_manager.mark_failed(proxy)
                logger.warning(f"Request failed with proxy (attempt {attempt + 1}/{max_retries}): {e}")
            else:
                raise

    logger.error(f"All proxy attempts failed. Last error: {last_error}")
    raise last_error


@mcp.tool(
    name="google-play-search",
    description="Search for apps in Google Play Store",
    structured_output=True
)
async def google_play_search(
        country: str,
        language: str,
        term: str,
        num: int = 20,
        price: str = "all"
) -> List[AppOverview]:
    """
    Search for apps in Google Play Store.
    :param country: Country code
    :param language: Language code
    :param term: Search term
    :param num: Number of results to return (default: 20)
    :param price: Price filter - "all", "free", or "paid" (default: "all")
    :return: A list of app overviews
    """
    valid_prices = ["all", "free", "paid"]
    if price not in valid_prices:
        raise ValueError(f"Invalid price filter: {price}. Must be one of: {', '.join(valid_prices)}")

    max_retries = max(len(proxy_manager.available_proxies), 1) if proxy_manager.has_proxies else 1
    last_error = None

    for attempt in range(max_retries):
        proxy = proxy_manager.get_random_proxy()

        try:
            client = GooglePlayClient(
                country=country,
                lang=language,
                proxies=proxy,
            )
            result = await client.asearch(term=term, num=num, price=price, lang=language, country=country)
            if proxy:
                proxy_manager.reset_failed()
            return result

        except Exception as e:
            last_error = e
            if proxy:
                proxy_manager.mark_failed(proxy)
                logger.warning(f"Request failed with proxy (attempt {attempt + 1}/{max_retries}): {e}")
            else:
                raise

    logger.error(f"All proxy attempts failed. Last error: {last_error}")
    raise last_error


@mcp.tool(
    name="google-play-list",
    description="Browse Google Play Store collections (top free, top paid, grossing) by category",
    structured_output=True
)
async def google_play_list(
        country: str,
        language: str,
        collection: Collection,
        category: Category,
        num: int = 50,
        age: Optional[Age] = None
) -> List[AppOverview]:
    """
    Browse Google Play Store collections by category.
    :param country: Country code
    :param language: Language code
    :param collection: Collection type (TOP_FREE, TOP_PAID, GROSSING)
    :param category: Category (e.g., APPLICATION, GAME_ACTION, PRODUCTIVITY)
    :param num: Number of results to return (default: 50)
    :param age: Optional age filter (FIVE_UNDER, SIX_EIGHT, NINE_UP)
    :return: A list of app overviews
    """
    max_retries = max(len(proxy_manager.available_proxies), 1) if proxy_manager.has_proxies else 1
    last_error = None

    for attempt in range(max_retries):
        proxy = proxy_manager.get_random_proxy()

        try:
            client = GooglePlayClient(
                country=country,
                lang=language,
                proxies=proxy,
            )
            result = await client.alist(
                collection=collection,
                category=category,
                age=age,
                num=num,
                lang=language,
                country=country
            )
            if proxy:
                proxy_manager.reset_failed()
            return result

        except Exception as e:
            last_error = e
            if proxy:
                proxy_manager.mark_failed(proxy)
                logger.warning(f"Request failed with proxy (attempt {attempt + 1}/{max_retries}): {e}")
            else:
                raise

    logger.error(f"All proxy attempts failed. Last error: {last_error}")
    raise last_error


@mcp.tool(
    name="google-play-app",
    description="Get detailed information about a specific app",
    structured_output=True
)
async def google_play_app(
        country: str,
        language: str,
        app_id: str
) -> AppDetails:
    """
    Get detailed information about a specific app.
    :param country: Country code
    :param language: Language code
    :param app_id: App package ID (e.g., "com.spotify.music")
    :return: Detailed app information
    """
    max_retries = max(len(proxy_manager.available_proxies), 1) if proxy_manager.has_proxies else 1
    last_error = None

    for attempt in range(max_retries):
        proxy = proxy_manager.get_random_proxy()

        try:
            client = GooglePlayClient(
                country=country,
                lang=language,
                proxies=proxy,
            )
            result = await client.aapp(app_id=app_id, lang=language, country=country)
            if proxy:
                proxy_manager.reset_failed()
            return result

        except Exception as e:
            last_error = e
            if proxy:
                proxy_manager.mark_failed(proxy)
                logger.warning(f"Request failed with proxy (attempt {attempt + 1}/{max_retries}): {e}")
            else:
                raise

    logger.error(f"All proxy attempts failed. Last error: {last_error}")
    raise last_error


@mcp.tool(
    name="google-play-reviews",
    description="Get user reviews for a specific app with pagination support",
    structured_output=True
)
async def google_play_reviews(
        country: str,
        language: str,
        app_id: str,
        sort: Sort = Sort.NEWEST,
        num: int = 100,
        filter_rating: Optional[int] = None,
        continuation_token: Optional[str] = None
) -> ReviewsResponse:
    """
    Get user reviews for a specific app.
    :param country: Country code
    :param language: Language code
    :param app_id: App package ID (e.g., "com.spotify.music")
    :param sort: Sort order (NEWEST, RATING, HELPFULNESS)
    :param num: Number of reviews to return (default: 100)
    :param filter_rating: Optional filter by rating (1-5)
    :param continuation_token: Optional token for pagination
    :return: Reviews and pagination token
    """
    if filter_rating is not None and (filter_rating < 1 or filter_rating > 5):
        raise ValueError(f"Invalid filter_rating: {filter_rating}. Must be between 1 and 5")

    max_retries = max(len(proxy_manager.available_proxies), 1) if proxy_manager.has_proxies else 1
    last_error = None

    for attempt in range(max_retries):
        proxy = proxy_manager.get_random_proxy()

        try:
            client = GooglePlayClient(
                country=country,
                lang=language,
                proxies=proxy,
            )
            reviews_list, next_token = await client.areviews(
                app_id=app_id,
                lang=language,
                country=country,
                sort=sort,
                num=num,
                filter_rating_num=filter_rating,
                continuation_token=continuation_token
            )
            if proxy:
                proxy_manager.reset_failed()
            return ReviewsResponse(reviews=reviews_list, continuation_token=next_token)

        except Exception as e:
            last_error = e
            if proxy:
                proxy_manager.mark_failed(proxy)
                logger.warning(f"Request failed with proxy (attempt {attempt + 1}/{max_retries}): {e}")
            else:
                raise

    logger.error(f"All proxy attempts failed. Last error: {last_error}")
    raise last_error


@mcp.tool(
    name="google-play-validate-title",
    description="Validate title for Google Play Store",
    structured_output=True
)
async def google_play_validate_title(title: str) -> MetadataValidationResult:
    """
    Validate title for Google Play Store.
    :param title: Title to validate
    :return: A validation result
    """
    length = len(title)
    errors = []

    if length > MAX_GOOGLE_PLAY_TITLE_LENGTH:
        errors.append(
            MetadataValidationError(
                message=f"Title length should be no more than {MAX_GOOGLE_PLAY_TITLE_LENGTH} characters. Current length: {length} characters"
            )
        )

    return MetadataValidationResult(length=length, is_valid=len(errors) == 0, errors=errors)


@mcp.tool(
    name="google-play-validate-short-description",
    description="Validate short description for Google Play Store",
    structured_output=True
)
async def google_play_validate_short_description(short_description: str) -> MetadataValidationResult:
    """
    Validate a short description for Google Play Store.
    :param short_description: Short description to validate
    :return: A validation result
    """
    length = len(short_description)
    errors = []

    if length > MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH:
        errors.append(
            MetadataValidationError(
                message=f"Short description length should be no more than {MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH} characters. Current length: {length} characters"
            )
        )

    return MetadataValidationResult(length=length, is_valid=len(errors) == 0, errors=errors)


@mcp.tool(
    name="google-play-validate-full-description",
    description="Validate full description for Google Play Store",
    structured_output=True
)
async def google_play_validate_full_description(full_description: str) -> MetadataValidationResult:
    """
    Validate a full description for Google Play Store.
    :param full_description: Full description to validate
    :return: A validation result
    """
    length = len(full_description)
    errors = []

    if length > MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH:
        errors.append(
            MetadataValidationError(
                message=f"Full description length should be no more than {MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH} characters. Current length: {length} characters"
            )
        )

    return MetadataValidationResult(length=length, is_valid=len(errors) == 0, errors=errors)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
