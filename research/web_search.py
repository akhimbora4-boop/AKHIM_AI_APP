"""
AKHIM AI - Web Search Engine

Version: 3.0

Features:
    - DuckDuckGo HTML search
    - No requests dependency
    - Standard-library HTTP client
    - Retry + timeout handling
    - URL cleaning
    - Redirect URL handling
    - Duplicate filtering
    - Domain filtering
    - Source diversity
    - Homepage filtering
    - Article/page fetching
    - JSON-LD date extraction
    - Meta date extraction
    - OpenGraph support
    - Article/main/content extraction
    - Content cleaning
    - Search result quality filtering
    - Safe error handling
    - Android/Buildozer friendly
"""

import json
import re
import time

from datetime import datetime
from urllib.parse import (
    urlparse,
    parse_qs,
    unquote,
    urlencode
)
from urllib.request import (
    Request,
    urlopen
)
from urllib.error import (
    HTTPError,
    URLError
)

from bs4 import BeautifulSoup


class WebSearch:

    VERSION = "3.0"

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        timeout=15,
        retries=2,
        max_content=12000
    ):

        self.timeout = max(
            5,
            int(timeout)
        )

        self.retries = max(
            0,
            int(retries)
        )

        self.max_content = max(
            1000,
            int(max_content)
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Linux; Android 12; Mobile) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 "
                "Mobile Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": (
                "en-US,en;q=0.9"
            ),
            "Cache-Control": "no-cache"
        }

        # -----------------------------------------------------
        # Domains that should never become research sources.
        # -----------------------------------------------------

        self.blocked_domains = {
            "duckduckgo.com",
            "www.duckduckgo.com",
            "news.google.com",
            "google.com",
            "www.google.com"
        }

        # -----------------------------------------------------
        # Generic/home/category pages.
        # -----------------------------------------------------

        self.generic_paths = {
            "",
            "news",
            "latest",
            "search",
            "topics",
            "category",
            "categories",
            "technology",
            "artificial-intelligence",
            "ai-news",
            "news/technology",
            "technology/artificial-intelligence",
            "category/artificial-intelligence",
            "category/news"
        }

        # -----------------------------------------------------
        # Tags that usually contain navigation/noise.
        # -----------------------------------------------------

        self.noise_tags = [
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
            "iframe",
            "svg",
            "canvas",
            "button"
        ]

    # =========================================================
    # SAFE TEXT
    # =========================================================

    def clean_text(
        self,
        value
    ):

        if value is None:
            return ""

        try:

            text = str(value)

        except Exception:

            return ""

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =========================================================
    # NORMALIZE DOMAIN
    # =========================================================

    def normalize_domain(
        self,
        domain
    ):

        domain = self.clean_text(
            domain
        ).lower()

        if domain.startswith(
            "www."
        ):

            domain = domain[4:]

        if ":" in domain:

            domain = domain.split(
                ":",
                1
            )[0]

        return domain

    # =========================================================
    # GET SOURCE / DOMAIN
    # =========================================================

    def get_source(
        self,
        url
    ):

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            return self.normalize_domain(
                parsed.netloc
            )

        except Exception:

            return ""

    # =========================================================
    # URL VALIDATION
    # =========================================================

    def is_valid_url(
        self,
        url
    ):

        if not url:
            return False

        try:

            parsed = urlparse(
                url
            )

            if parsed.scheme not in {
                "http",
                "https"
            }:

                return False

            if not parsed.netloc:
                return False

            return True

        except Exception:

            return False

    # =========================================================
    # CLEAN URL
    # =========================================================

    def clean_url(
        self,
        url
    ):

        if not url:
            return ""

        url = self.clean_text(
            url
        )

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            # -------------------------------------------------
            # DuckDuckGo redirect
            # -------------------------------------------------

            domain = self.normalize_domain(
                parsed.netloc
            )

            if (
                "duckduckgo.com"
                in domain
            ):

                query = parse_qs(
                    parsed.query
                )

                if "uddg" in query:

                    target = unquote(
                        query["uddg"][0]
                    )

                    if self.is_valid_url(
                        target
                    ):

                        return target

            # -------------------------------------------------
            # Remove fragments
            # -------------------------------------------------

            cleaned = parsed._replace(
                fragment=""
            ).geturl()

            return cleaned

        except Exception:

            return url

    # =========================================================
    # URL KEY
    # =========================================================

    def url_key(
        self,
        url
    ):

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            domain = self.normalize_domain(
                parsed.netloc
            )

            path = parsed.path.rstrip(
                "/"
            )

            return (
                domain
                + path
            ).lower()

        except Exception:

            return url.lower()

    # =========================================================
    # HOMEPAGE / GENERIC PAGE
    # =========================================================

    def is_homepage(
        self,
        url
    ):

        try:

            parsed = urlparse(
                url
            )

            path = (
                parsed.path
                .strip("/")
                .lower()
            )

            if not path:
                return True

            if path in self.generic_paths:
                return True

            return False

        except Exception:

            return False

    # =========================================================
    # REQUEST
    # =========================================================

    def request(
        self,
        url,
        method="GET",
        data=None,
        timeout=None
    ):

        if not self.is_valid_url(
            url
        ):

            return None

        if timeout is None:
            timeout = self.timeout

        encoded_data = None

        if data is not None:

            if isinstance(
                data,
                dict
            ):

                encoded_data = urlencode(
                    data
                ).encode(
                    "utf-8"
                )

            elif isinstance(
                data,
                bytes
            ):

                encoded_data = data

            else:

                encoded_data = str(
                    data
                ).encode(
                    "utf-8"
                )

        for attempt in range(
            self.retries + 1
        ):

            try:

                request = Request(
                    url=url,
                    data=encoded_data,
                    headers=self.headers,
                    method=method.upper()
                )

                response = urlopen(
                    request,
                    timeout=timeout
                )

                status = getattr(
                    response,
                    "status",
                    200
                )

                if status < 200 or status >= 400:
                    return None

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                )

                # -------------------------------------------------
                # Avoid downloading obvious binary files.
                # -------------------------------------------------

                blocked_types = (
                    "image/",
                    "video/",
                    "audio/",
                    "application/pdf",
                    "application/zip",
                    "application/octet-stream"
                )

                if any(
                    content_type.lower().startswith(
                        item
                    )
                    for item in blocked_types
                ):

                    return None

                raw = response.read()

                if not raw:
                    return None

                charset = (
                    response.headers.get_content_charset()
                    or "utf-8"
                )

                try:

                    text = raw.decode(
                        charset,
                        errors="replace"
                    )

                except Exception:

                    text = raw.decode(
                        "utf-8",
                        errors="replace"
                    )

                return {
                    "status": status,
                    "text": text,
                    "content_type": content_type
                }

            except (
                HTTPError,
                URLError,
                TimeoutError,
                OSError
            ):

                if attempt < self.retries:

                    time.sleep(
                        0.5 * (
                            attempt + 1
                        )
                    )

                    continue

                return None

            except Exception:

                return None

        return None

    # =========================================================
    # CURRENT QUERY
    # =========================================================

    def is_current_query(
        self,
        query
    ):

        text = self.clean_text(
            query
        ).lower()

        current_words = [
            "current",
            "latest",
            "recent",
            "today",
            "now",
            "currently",
            "breaking",
            "news",
            "this week",
            "this month",
            "বৰ্তমান",
            "আজিৰ",
            "শেহতীয়া",
            "শেহতীয়া",
            "সাম্প্ৰতিক",
            "খবৰ"
        ]

        return any(
            word in text
            for word in current_words
        )

    # =========================================================
    # BUILD SEARCH QUERY
    # =========================================================

    def build_search_query(
        self,
        query
    ):

        query = self.clean_text(
            query
        )

        if not query:
            return ""

        if not self.is_current_query(
            query
        ):

            return query

        year = datetime.now().year

        # Avoid blindly appending the year
        # when user already supplied one.
        has_year = bool(
            re.search(
                r"\b20\d{2}\b",
                query
            )
        )

        if has_year:

            return (
                f"{query} latest"
            )

        return (
            f"{query} "
            f"{year} latest"
        )

    # =========================================================
    # EXTRACT SEARCH RESULT TEXT
    # =========================================================

    def extract_result_text(
        self,
        element,
        selector
    ):

        tag = element.select_one(
            selector
        )

        if not tag:
            return ""

        return self.clean_text(
            tag.get_text(
                " ",
                strip=True
            )
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        query,
        max_results=5
    ):

        query = self.clean_text(
            query
        )

        if not query:
            return []

        try:

            max_results = max(
                1,
                min(
                    int(max_results),
                    20
                )
            )

        except (
            TypeError,
            ValueError
        ):

            max_results = 5

        search_query = (
            self.build_search_query(
                query
            )
        )

        if not search_query:
            return []

        search_url = (
            "https://html.duckduckgo.com/html/"
        )

        response = self.request(
            search_url,
            method="POST",
            data={
                "q": search_query
            }
        )

        if not response:
            return []

        html = response.get(
            "text",
            ""
        )

        if not html:
            return []

        try:

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

        except Exception:

            return []

        results = []

        seen_urls = set()

        seen_domains = set()

        # -----------------------------------------------------
        # DuckDuckGo result containers
        # -----------------------------------------------------

        items = soup.select(
            ".result"
        )

        for item in items:

            if len(results) >= max_results:
                break

            try:

                title_tag = (
                    item.select_one(
                        ".result__title"
                    )
                    or
                    item.select_one(
                        ".result__a"
                    )
                )

                link_tag = (
                    item.select_one(
                        ".result__a"
                    )
                )

                snippet_tag = (
                    item.select_one(
                        ".result__snippet"
                    )
                )

                if not title_tag or not link_tag:
                    continue

                title = self.clean_text(
                    title_tag.get_text(
                        " ",
                        strip=True
                    )
                )

                raw_url = self.clean_text(
                    link_tag.get(
                        "href",
                        ""
                    )
                )

                snippet = ""

                if snippet_tag:

                    snippet = self.clean_text(
                        snippet_tag.get_text(
                            " ",
                            strip=True
                        )
                    )

                if not title or not raw_url:
                    continue

                url = self.clean_url(
                    raw_url
                )

                if not self.is_valid_url(
                    url
                ):
                    continue

                source = self.get_source(
                    url
                )

                if not source:
                    continue

                # -------------------------------------------------
                # Block search engine/internal sources.
                # -------------------------------------------------

                if source in self.blocked_domains:
                    continue

                if (
                    "duckduckgo.com"
                    in source
                ):
                    continue

                if (
                    "news.google.com"
                    in source
                ):
                    continue

                # -------------------------------------------------
                # Remove ads.
                # -------------------------------------------------

                title_lower = title.lower()

                if (
                    "ad viewing ads"
                    in title_lower
                    or title_lower == "advertisement"
                ):

                    continue

                # -------------------------------------------------
                # Remove generic pages.
                # -------------------------------------------------

                if self.is_homepage(
                    url
                ):

                    continue

                # -------------------------------------------------
                # Duplicate URL.
                # -------------------------------------------------

                key = self.url_key(
                    url
                )

                if not key:
                    continue

                if key in seen_urls:
                    continue

                # -------------------------------------------------
                # Prefer source diversity.
                # -------------------------------------------------

                if source in seen_domains:
                    continue

                seen_urls.add(
                    key
                )

                seen_domains.add(
                    source
                )

                results.append({

                    "title": title,

                    "url": url,

                    "snippet": snippet,

                    "source": source,

                    "domain": source,

                    "date": "",

                    "page_title": "",

                    "content": "",

                    "search_query": query,

                    "search_engine": "duckduckgo",

                    "search_rank": len(
                        results
                    ) + 1
             })

            except Exception:

                continue

        return results

    # =========================================================
    # EXTRACT META DATE
    # =========================================================

    def extract_meta_date(
        self,
        soup
    ):

        candidates = [

            ("property", "article:published_time"),
            ("property", "article:modified_time"),
            ("property", "og:updated_time"),

            ("name", "datePublished"),
            ("name", "dateModified"),
            ("name", "pubdate"),
            ("name", "publishdate"),
            ("name", "published"),
            ("name", "modified"),
            ("name", "timestamp"),
            ("name", "date"),

            ("itemprop", "datePublished"),
            ("itemprop", "dateModified"),
            ("itemprop", "dateCreated")

        ]

        for attribute, value in candidates:

            try:

                tag = soup.find(
                    "meta",
                    attrs={
                        attribute: value
                    }
                )

                if tag:

                    content = self.clean_text(
                        tag.get(
                            "content",
                            ""
                        )
                    )

                    if content:
                        return content

            except Exception:

                continue

        return ""

    # =========================================================
    # EXTRACT JSON-LD DATE
    # =========================================================

    def extract_jsonld_date(
        self,
        soup
    ):

        scripts = soup.find_all(
            "script",
            attrs={
                "type": "application/ld+json"
            }
        )

        date_fields = [
            "datePublished",
            "dateModified",
            "dateCreated"
        ]

        def search_object(
            obj
        ):

            if isinstance(
                obj,
                dict
            ):

                for field in date_fields:

                    value = obj.get(
                        field
                    )

                    if value:

                        return self.clean_text(
                            value
                        )

                # Handle @graph
                graph = obj.get(
                    "@graph"
                )

                if isinstance(
                    graph,
                    list
                ):

                    for entry in graph:

                        result = search_object(
                            entry
                        )

                        if result:
                            return result

            elif isinstance(
                obj,
                list
            ):

                for entry in obj:

                    result = search_object(
                        entry
                    )

                    if result:
                        return result

            return ""

        for script in scripts:

            try:

                raw = script.string

                if not raw:
                    raw = script.get_text()

                raw = raw.strip()

                if not raw:
                    continue

                data = json.loads(
                    raw
                )

                result = search_object(
                    data
                )

                if result:
                    return result

            except Exception:

                continue

        return ""

    # =========================================================
    # EXTRACT DATE
    # =========================================================

    def extract_date(
        self,
        soup
    ):

        # JSON-LD is often more reliable.
        value = self.extract_jsonld_date(
            soup
        )

        if value:
            return value

        return self.extract_meta_date(
            soup
        )

    # =========================================================
    # EXTRACT PAGE TITLE
    # =========================================================

    def extract_page_title(
        self,
        soup
    ):

        # Prefer OpenGraph title.
        try:

            og = soup.find(
                "meta",
                attrs={
                    "property": "og:title"
                }
            )

            if og:

                value = self.clean_text(
                    og.get(
                        "content",
                        ""
                    )
                )

                if value:
                    return value

        except Exception:

            pass

        try:

            if soup.title:

                return self.clean_text(
                    soup.title.get_text(
                        " ",
                        strip=True
                    )
                )

        except Exception:

            pass

        return ""
# =========================================================
    # REMOVE NOISE
    # =========================================================

    def remove_noise(
        self,
        soup
    ):

        for tag_name in self.noise_tags:

            try:

                for tag in soup.find_all(
                    tag_name
                ):

                    tag.decompose()

            except Exception:

                continue

    # =========================================================
    # EXTRACT CONTENT
    # =========================================================

    def extract_content(
        self,
        soup
    ):

        self.remove_noise(
            soup
        )

        # -----------------------------------------------------
        # Prefer article.
        # -----------------------------------------------------

        article = soup.find(
            "article"
        )

        if article:

            text = article.get_text(
                " ",
                strip=True
            )

            if len(text) >= 200:

                return self.clean_content(
                    text
                )

        # -----------------------------------------------------
        # Then main.
        # -----------------------------------------------------

        main = soup.find(
            "main"
        )

        if main:

            text = main.get_text(
                " ",
                strip=True
            )

            if len(text) >= 200:

                return self.clean_content(
                    text
                )

        # -----------------------------------------------------
        # Common content containers.
        # -----------------------------------------------------

        selectors = [
            "[itemprop='articleBody']",
            ".article-body",
            ".article-content",
            ".entry-content",
            ".post-content",
            ".story-body",
            ".story-content",
            ".content-body",
            ".main-content"
        ]

        candidates = []

        for selector in selectors:

            try:

                element = soup.select_one(
                    selector
                )

                if element:

                    text = element.get_text(
                        " ",
                        strip=True
                    )

                    if text:
                        candidates.append(
                            text
                        )

            except Exception:

                continue

        if candidates:

            best = max(
                candidates,
                key=len
            )

            if len(best) >= 200:

                return self.clean_content(
                    best
                )

        # -----------------------------------------------------
        # Fallback: body.
        # -----------------------------------------------------

        body = soup.body

        if body:

            text = body.get_text(
                " ",
                strip=True
            )

            return self.clean_content(
                text
            )

        # -----------------------------------------------------
        # Final fallback.
        # -----------------------------------------------------

        text = soup.get_text(
            " ",
            strip=True
        )

        return self.clean_content(
            text
        )

    # =========================================================
    # CLEAN CONTENT
    # =========================================================

    def clean_content(
        self,
        text
    ):

        text = self.clean_text(
            text
        )

        if not text:
            return ""

        # Remove repeated whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        # Remove obvious repeated boilerplate.
        text = re.sub(
            r"(cookie policy|accept cookies|"
            r"subscribe now|sign up for our newsletter)",
            " ",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text[
            :self.max_content
        ]
# =========================================================
    # FETCH PAGE
    # =========================================================

    def fetch_page(
        self,
        url
    ):

        empty = {
            "content": "",
            "date": "",
            "page_title": "",
            "status": 0,
            "content_length": 0
        }

        if not self.is_valid_url(
            url
        ):

            return empty

        response = self.request(
            url,
            method="GET"
        )

        if not response:
            return empty

        html = response.get(
            "text",
            ""
        )

        if not html:
            return empty

        try:

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

        except Exception:

            return empty

        try:

            page_title = (
                self.extract_page_title(
                    soup
                )
            )

            page_date = (
                self.extract_date(
                    soup
                )
            )

            content = (
                self.extract_content(
                    soup
                )
            )

            return {

                "content": content,

                "date": page_date,

                "page_title": page_title,

                "status": response.get(
                    "status",
                    200
                ),

                "content_length": len(
                    content
                )

            }

        except Exception:

            return empty

    # =========================================================
    # QUALITY CHECK
    # =========================================================

    def is_quality_result(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return False

        title = self.clean_text(
            result.get(
                "title"
            )
        )

        url = self.clean_text(
            result.get(
                "url"
            )
        )

        content = self.clean_text(
            result.get(
                "content"
            )
        )

        snippet = self.clean_text(
            result.get(
                "snippet"
            )
        )

        if not title:
            return False

        if not self.is_valid_url(
            url
        ):

            return False

        # At least one meaningful text field.
        if not content and not snippet:
            return False

        return True

    # =========================================================
    # FETCH RESEARCH SOURCES
    # =========================================================

    def research(
        self,
        query,
        max_results=5,
        fetch_content=True
    ):

        results = self.search(
            query,
            max_results
        )

        if not results:
            return []

        valid_results = []

        for result in results:

            if fetch_content:

                page = self.fetch_page(
                    result.get(
                        "url",
                        ""
                    )
                )

                result["content"] = (
                    page.get(
                        "content",
                        ""
                    )
                )

                result["date"] = (
                    page.get(
                        "date",
                        ""
                    )
                )

                result["page_title"] = (
                    page.get(
                        "page_title",
                        ""
                    )
                )

                result["http_status"] = (
                    page.get(
                        "status",
                        0
                    )
                )

                result["content_length"] = (
                    page.get(
                        "content_length",
                        0
                    )
                )

            # -------------------------------------------------
            # Keep result even if full page fetch failed,
            # provided search snippet exists.
            # -------------------------------------------------

            if self.is_quality_result(
                result
            ):

                valid_results.append(
                    result
                )

        return valid_results

    # =========================================================
    # RESEARCH WITH SOURCE DIVERSITY
    # =========================================================

    def deep_research(
        self,
        query,
        max_results=7
    ):

        """
        Stronger research mode.

        Search more sources than finally requested,
        fetch them,
        then keep the best available sources.
        """

        search_limit = min(
            20,
            max(
                max_results * 3,
                10
            )
        )

        results = self.search(
            query,
            search_limit
        )

        if not results:
            return []

        researched = []

        for result in results:

            page = self.fetch_page(
                result.get(
                    "url",
                    ""
                )
            )

            result["content"] = (
                page.get(
                    "content",
                    ""
                )
            )

            result["date"] = (
                page.get(
                    "date",
                    ""
                )
            )

            result["page_title"] = (
                page.get(
                    "page_title",
                    ""
                )
            )

            result["http_status"] = (
                page.get(
                    "status",
                    0
                )
            )

            result["content_length"] = (
                page.get(
                    "content_length",
                    0
                )
            )

            if self.is_quality_result(
                result
            ):

                researched.append(
                    result
                )

            if len(researched) >= max_results:

                break

        return researched

     