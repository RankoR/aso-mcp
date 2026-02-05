from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google_play_scraper import Collection, Category, Sort
from google_play_scraper.models import AppOverview, AppDetails, Review

from constants.google_play_constants import (
    MAX_GOOGLE_PLAY_TITLE_LENGTH,
    MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH,
    MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH,
)
from server import (
    google_play_suggest,
    google_play_search,
    google_play_list,
    google_play_app,
    google_play_reviews,
    get_google_play_languages,
    get_google_play_countries,
    get_google_play_countries_with_languages,
    get_google_play_collections,
    get_google_play_categories,
    get_google_play_sort_orders,
    get_google_play_age_filters,
    get_google_play_rating_filters,
    google_play_validate_title,
    google_play_validate_short_description,
    google_play_validate_full_description,
)


@pytest.fixture
def mock_proxy_manager():
    """Mock the proxy manager"""
    with patch('server.proxy_manager') as mock:
        mock.has_proxies = False
        mock.get_random_proxy.return_value = None
        yield mock


@pytest.fixture
def mock_app_overview():
    """Create a mock AppOverview"""
    return AppOverview(
        app_id="com.example.app",
        title="Example App",
        icon="https://example.com/icon.png",
        developer="Example Dev",
        developer_id="example_dev",
        score=4.5,
        score_text="4.5",
        price_text="Free",
        free=True,
        summary="An example app"
    )


@pytest.fixture
def mock_app_details():
    """Create a mock AppDetails"""
    return AppDetails(
        app_id="com.spotify.music",
        title="Spotify",
        developer="Spotify Ltd.",
        developer_id="spotify_ltd",
        summary="Music streaming app",
        description="Stream millions of songs",
        description_html="<p>Stream millions of songs</p>",
        recent_changes="Bug fixes",
        score=4.5,
        score_text="4.5",
        ratings=1000000,
        reviews=500000,
        histogram={"5": 600000, "4": 200000, "3": 100000, "2": 50000, "1": 50000},
        price=0.0,
        price_text="Free",
        currency="USD",
        free=True,
        offers_iap=True,
        installs="100,000,000+",
        min_installs=100000000,
        max_installs=500000000,
        icon="https://example.com/icon.png",
        header_image="https://example.com/header.png",
        screenshots=["https://example.com/1.png"],
        video="https://example.com/video.mp4",
        content_rating="Everyone",
        privacy_policy="https://example.com/privacy",
        android_version="5.0",
        version="8.7.0",
        released="2020-01-01",
        developer_email="support@spotify.com",
        developer_website="https://spotify.com",
        developer_address="123 Music St",
        genre="Music & Audio",
        genre_id="MUSIC_AND_AUDIO",
        available=True,
        comments=[]
    )


@pytest.fixture
def mock_review():
    """Create a mock Review"""
    return Review(
        id="review123",
        user_name="John Doe",
        user_image="https://example.com/avatar.png",
        score=5,
        title="Great app",
        text="Love this app!",
        reply_date=None,
        reply_text=None,
        version="1.0.0",
        thumbs_up=10
    )


class TestSuggest:
    @pytest.mark.asyncio
    async def test_google_play_suggest_success(self, mock_proxy_manager):
        """Test successful keyword suggestions"""
        expected_suggestions = ["photo editor", "photo editing app", "photography"]

        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.asuggest = AsyncMock(return_value=expected_suggestions)

            result = await google_play_suggest(
                country="us",
                language="en",
                keyword="photo"
            )

            assert result == expected_suggestions
            mock_instance.asuggest.assert_called_once()

    @pytest.mark.asyncio
    async def test_google_play_suggest_with_proxy(self):
        """Test suggestions with proxy rotation"""
        expected_suggestions = ["game", "gaming"]
        mock_proxy = {"https": "http://proxy:8080"}

        with patch('server.proxy_manager') as mock_pm, \
                patch('server.GooglePlayClient') as MockClient:
            mock_pm.has_proxies = True
            mock_pm.available_proxies = [mock_proxy]
            mock_pm.get_random_proxy.return_value = mock_proxy
            mock_pm.reset_failed = MagicMock()

            mock_instance = MockClient.return_value
            mock_instance.asuggest = AsyncMock(return_value=expected_suggestions)

            result = await google_play_suggest(
                country="us",
                language="en",
                keyword="game"
            )

            assert result == expected_suggestions
            mock_pm.reset_failed.assert_called_once()

    @pytest.mark.asyncio
    async def test_google_play_suggest_proxy_failure(self):
        """Test handling of proxy failures"""
        mock_proxy = {"https": "http://proxy:8080"}

        with patch('server.proxy_manager') as mock_pm, \
                patch('server.GooglePlayClient') as MockClient:
            mock_pm.has_proxies = True
            mock_pm.available_proxies = [mock_proxy]
            mock_pm.get_random_proxy.return_value = mock_proxy
            mock_pm.mark_failed = MagicMock()

            mock_instance = MockClient.return_value
            mock_instance.asuggest = AsyncMock(side_effect=Exception("Proxy error"))

            with pytest.raises(Exception, match="Proxy error"):
                await google_play_suggest(
                    country="us",
                    language="en",
                    keyword="test"
                )

            mock_pm.mark_failed.assert_called_once()


class TestSearch:
    @pytest.mark.asyncio
    async def test_google_play_search_success(self, mock_proxy_manager, mock_app_overview):
        """Test successful app search"""
        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.asearch = AsyncMock(return_value=[mock_app_overview])

            result = await google_play_search(
                country="us",
                language="en",
                term="example",
                num=10,
                price="free"
            )

            assert len(result) == 1
            assert result[0].app_id == "com.example.app"
            assert result[0].title == "Example App"

    @pytest.mark.asyncio
    async def test_google_play_search_invalid_price(self, mock_proxy_manager):
        """Test search with invalid price filter"""
        with pytest.raises(ValueError, match="Invalid price filter"):
            await google_play_search(
                country="us",
                language="en",
                term="test",
                price="invalid"
            )


class TestList:
    @pytest.mark.asyncio
    async def test_google_play_list_success(self, mock_proxy_manager, mock_app_overview):
        """Test successful app listing"""
        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.alist = AsyncMock(return_value=[mock_app_overview])

            result = await google_play_list(
                country="us",
                language="en",
                collection=Collection.TOP_FREE,
                category=Category.GAME_ACTION,
                num=20
            )

            assert len(result) == 1
            assert result[0].app_id == "com.example.app"

    @pytest.mark.asyncio
    async def test_google_play_list_with_age_filter(self, mock_proxy_manager):
        """Test listing with age filter"""
        from google_play_scraper import Age

        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.alist = AsyncMock(return_value=[])

            result = await google_play_list(
                country="us",
                language="en",
                collection=Collection.TOP_FREE,
                category=Category.GAME,
                age=Age.FIVE_UNDER
            )

            assert result == []
            mock_instance.alist.assert_called_once()


class TestApp:
    @pytest.mark.asyncio
    async def test_google_play_app_success(self, mock_proxy_manager, mock_app_details):
        """Test successful app details retrieval"""
        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.aapp = AsyncMock(return_value=mock_app_details)

            result = await google_play_app(
                country="us",
                language="en",
                app_id="com.spotify.music"
            )

            assert result.app_id == "com.spotify.music"
            assert result.title == "Spotify"
            assert result.score == 4.5


class TestReviews:
    @pytest.mark.asyncio
    async def test_google_play_reviews_success(self, mock_proxy_manager, mock_review):
        """Test successful reviews retrieval"""
        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.areviews = AsyncMock(return_value=([mock_review], "next_token"))

            result = await google_play_reviews(
                country="us",
                language="en",
                app_id="com.example.app",
                sort=Sort.NEWEST,
                num=100
            )

            assert len(result.reviews) == 1
            assert result.reviews[0].user_name == "John Doe"
            assert result.continuation_token == "next_token"

    @pytest.mark.asyncio
    async def test_google_play_reviews_with_filter(self, mock_proxy_manager):
        """Test reviews with rating filter"""
        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.areviews = AsyncMock(return_value=([], None))

            result = await google_play_reviews(
                country="us",
                language="en",
                app_id="com.example.app",
                filter_rating=5
            )

            assert result.reviews == []
            assert result.continuation_token is None

    @pytest.mark.asyncio
    async def test_google_play_reviews_invalid_rating(self, mock_proxy_manager):
        """Test reviews with invalid rating filter"""
        with pytest.raises(ValueError, match="Invalid filter_rating"):
            await google_play_reviews(
                country="us",
                language="en",
                app_id="com.example.app",
                filter_rating=6
            )

    @pytest.mark.asyncio
    async def test_google_play_reviews_with_pagination(self, mock_proxy_manager, mock_review):
        """Test reviews with pagination token"""
        with patch('server.GooglePlayClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.areviews = AsyncMock(return_value=([mock_review], None))

            result = await google_play_reviews(
                country="us",
                language="en",
                app_id="com.example.app",
                continuation_token="token123"
            )

            assert len(result.reviews) == 1
            assert result.continuation_token is None


class TestReferenceData:
    @pytest.mark.asyncio
    async def test_get_google_play_languages(self):
        """Test getting supported languages"""
        result = await get_google_play_languages()
        assert isinstance(result, list)
        assert len(result) > 0
        assert "en" in result

    @pytest.mark.asyncio
    async def test_get_google_play_countries(self):
        """Test getting supported countries"""
        result = await get_google_play_countries()
        assert isinstance(result, list)
        assert len(result) > 0
        assert "us" in result

    @pytest.mark.asyncio
    async def test_get_google_play_countries_with_languages(self):
        """Test getting countries with languages"""
        result = await get_google_play_countries_with_languages()
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].country_code is not None
        assert len(result[0].language_codes) > 0

    @pytest.mark.asyncio
    async def test_get_google_play_collections(self):
        """Test getting available collections"""
        result = await get_google_play_collections()
        assert isinstance(result, list)
        assert "TOP_FREE" in result
        assert "TOP_PAID" in result
        assert "GROSSING" in result

    @pytest.mark.asyncio
    async def test_get_google_play_categories(self):
        """Test getting available categories"""
        result = await get_google_play_categories()
        assert isinstance(result, list)
        assert len(result) > 0
        assert "GAME" in result
        assert "APPLICATION" in result

    @pytest.mark.asyncio
    async def test_get_google_play_sort_orders(self):
        """Test getting available sort orders"""
        result = await get_google_play_sort_orders()
        assert isinstance(result, list)
        assert "NEWEST" in result
        assert "RATING" in result
        assert "HELPFULNESS" in result

    @pytest.mark.asyncio
    async def test_get_google_play_age_filters(self):
        """Test getting available age filters"""
        result = await get_google_play_age_filters()
        assert isinstance(result, list)
        assert "FIVE_UNDER" in result
        assert "SIX_EIGHT" in result
        assert "NINE_UP" in result

    @pytest.mark.asyncio
    async def test_get_google_play_rating_filters(self):
        """Test getting available rating filters"""
        result = await get_google_play_rating_filters()
        assert result == [1, 2, 3, 4, 5]


class TestValidation:
    @pytest.mark.asyncio
    async def test_validate_title_valid(self):
        """Test title validation with valid input"""
        result = await google_play_validate_title("My App")
        assert result.is_valid is True
        assert result.length == 6
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_title_too_long(self):
        """Test title validation with too long input"""
        long_title = "a" * (MAX_GOOGLE_PLAY_TITLE_LENGTH + 1)
        result = await google_play_validate_title(long_title)
        assert result.is_valid is False
        assert result.length == MAX_GOOGLE_PLAY_TITLE_LENGTH + 1
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_validate_short_description_valid(self):
        """Test short description validation with valid input"""
        result = await google_play_validate_short_description("A great app")
        assert result.is_valid is True
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_short_description_too_long(self):
        """Test short description validation with too long input"""
        long_desc = "a" * (MAX_GOOGLE_PLAY_SHORT_DESCRIPTION_LENGTH + 1)
        result = await google_play_validate_short_description(long_desc)
        assert result.is_valid is False
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_validate_full_description_valid(self):
        """Test full description validation with valid input"""
        desc = "This is a full description of my app."
        result = await google_play_validate_full_description(desc)
        assert result.is_valid is True
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_full_description_too_long(self):
        """Test full description validation with too long input"""
        long_desc = "a" * (MAX_GOOGLE_PLAY_FULL_DESCRIPTION_LENGTH + 1)
        result = await google_play_validate_full_description(long_desc)
        assert result.is_valid is False
        assert len(result.errors) == 1
