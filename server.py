import logging
from typing import List

from google_play_scraper import GooglePlayClient
from mcp.server import FastMCP

from constants.google_play_constants import GOOGLE_PLAY_COUNTRIES, GOOGLE_PLAY_LANGUAGES, \
    GOOGLE_PLAY_COUNTRIES_WITH_LANGUAGES, MAX_GOOGLE_PLAY_TITLE_LENGTH, MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH, \
    MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH
from constants.mcp_constants import MCP_SERVER_INSTRUCTIONS
from models.google_play import GooglePlayCountryWithLanguages
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
            # Success - reset failed proxies for future requests
            if proxy:
                proxy_manager.reset_failed()
            return result

        except Exception as e:
            last_error = e
            if proxy:
                proxy_manager.mark_failed(proxy)
                logger.warning(f"Request failed with proxy (attempt {attempt + 1}/{max_retries}): {e}")
            else:
                # No proxy configured, don't retry
                raise

    # All proxies failed
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
