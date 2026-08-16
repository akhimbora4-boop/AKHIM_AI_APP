import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import re
from datetime import datetime


class WebSearch:

    def __init__(self):

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Android 12; Mobile) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Mobile Safari/537.36"
            )
        }


    # =================================
    # CLEAN URL
    # =================================

    def clean_url(self, url):

        if not url:
            return ""

        try:

            parsed = urlparse(url)

            if "duckduckgo.com" in parsed.netloc:

                query = parse_qs(
                    parsed.query
                )

                if "uddg" in query:

                    return unquote(
                        query["uddg"][0]
                    )

            return url

        except Exception:

            return url


    # =================================
    # SOURCE / DOMAIN
    # =================================

    def get_source(self, url):

        try:

            domain = urlparse(
                url
            ).netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            return domain

        except Exception:

            return ""


    # =================================
    # HOMEPAGE FILTER
    # =================================

    def is_homepage(self, url):

        try:

            parsed = urlparse(url)

            path = parsed.path.strip(
                "/"
            ).lower()

            if not path:
                return True

            generic_paths = [

                "technology",
                "technology/artificial-intelligence",
                "category/artificial-intelligence",
                "ai-news",
                "latest",
                "news",
                "artificial-intelligence",
                "category/news",
                "category",
                "topics",
                "search"

            ]

            return path in generic_paths

        except Exception:

            return False


    # =================================
    # CURRENT QUERY DETECTION
    # =================================

    def is_current_query(self, query):

        q = query.lower()

        current_words = [

            "current",
            "latest",
            "recent",
            "today",
            "now",
            "currently",
            "news",
            "this week",
            "this month",

            "বৰ্তমান",
            "আজিৰ",
            "শেহতীয়া",
            "সাম্প্ৰতিক",
            "খবৰ",
            "এতিয়া"

        ]

        return any(
            word in q
            for word in current_words
        )


    # =================================
    # EXTRACT YEAR FROM DATE
    # =================================

    def get_date_score(self, date):

        if not date:
            return 0

        try:

            match = re.search(
                r"(20\d{2})",
                date
            )

            if match:

                return int(
                    match.group(1)
                )

        except Exception:
            pass

        return 0


    # =================================
    # SEARCH
    # =================================

    def search(
        self,
        query,
        max_results=5
    ):

        url = (
            "https://html.duckduckgo.com/html/"
        )

        try:

            current_year = datetime.now().year

            current_search = self.is_current_query(
                query
            )

            # ---------------------------------
            # Improve current searches
            # ---------------------------------

            if current_search:

                search_query = (
                    f"{query} "
                    f"{current_year} "
                    f"latest "
                    f"after:{current_year}-01-01"
                )

            else:

                search_query = query


            response = requests.post(

                url,

                data={
                    "q": search_query
                },

                headers=self.headers,

                timeout=20

            )


            if response.status_code != 200:

                print(
                    "Search failed:",
                    response.status_code
                )

                return []


            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )


            candidates = []

            seen_urls = set()


            blocked_domains = {

                "duckduckgo.com",
                "news.google.com"

            }


            # =================================
            # COLLECT SEARCH RESULTS
            # =================================

            for item in soup.select(
                ".result"
            ):

                title = item.select_one(
                    ".result__title"
                )

                link = item.select_one(
                    ".result__a"
                )

                snippet = item.select_one(
                    ".result__snippet"
                )


                if not title or not link:
                    continue


                title_text = title.get_text(
                    " ",
                    strip=True
                )


                raw_url = link.get(
                    "href",
                    ""
                )


                if not raw_url:
                    continue


                url_text = self.clean_url(
                    raw_url
                )


                if not url_text:
                    continue


                parsed = urlparse(
                    url_text
                )


                if parsed.scheme not in (
                    "http",
                    "https"
                ):

                    continue


                source = self.get_source(
                    url_text
                )


                if not source:
                    continue


                # ---------------------------------
                # Block search engines
                # ---------------------------------

                if source in blocked_domains:
                    continue


                if source.endswith(
                    "news.google.com"
                ):

                    continue


                if "duckduckgo.com" in source:
                    continue


                # ---------------------------------
                # Block ads
                # ---------------------------------

                if "Ad Viewing ads" in title_text:
                    continue


                # ---------------------------------
                # Duplicate URL
                # ---------------------------------

                if url_text in seen_urls:
                    continue


                # ---------------------------------
                # Homepage/category
                # ---------------------------------

                if self.is_homepage(
                    url_text
                ):

                    continue


                seen_urls.add(
                    url_text
                )


                snippet_text = ""

                if snippet:

                    snippet_text = (
                        snippet.get_text(
                            " ",
                            strip=True
                        )
                    )


                candidates.append({

                    "title": title_text,

                    "url": url_text,

                    "snippet": snippet_text,

                    "source": source,

                    "date": "",

                    "page_title": "",

                    "content": ""

                })


            # =================================
            # FETCH DATE + CONTENT
            # =================================

            fetched = []


            for result in candidates:

                print(
                    "Reading:",
                    result["title"]
                )


                page = self.fetch_page(
                    result["url"]
                )


                result["content"] = page.get(
                    "content",
                    ""
                )


                result["date"] = page.get(
                    "date",
                    ""
                )


                result["page_title"] = page.get(
                    "page_title",
                    ""
                )


                if result["content"]:

                    fetched.append(
                        result
                    )

                else:

                    print(
                        "Skipped: no page content"
                    )


            # =================================
            # CURRENT SEARCH RANKING
            # =================================

            if current_search:

                fetched.sort(

                    key=lambda x:
                    self.get_date_score(
                        x.get("date", "")
                    ),

                    reverse=True

                )


            # =================================
            # DIFFERENT SOURCES
            # =================================

            final_results = []

            seen_sources = set()


            for result in fetched:

                source = result.get(
                    "source",
                    ""
                )


                if source in seen_sources:

                    continue


                seen_sources.add(
                    source
                )


                final_results.append(
                    result
                )


                if len(final_results) >= max_results:

                    break


            return final_results


        except Exception as e:

            print(
                "Search error:",
                e
            )

            return []


    # =================================
    # DATE EXTRACTION
    # =================================

    def extract_date(self, soup):

        meta_names = [

            "article:published_time",
            "article:modified_time",
            "datePublished",
            "date",
            "pubdate",
            "publishdate",
            "timestamp",
            "DC.date",
            "dc.date"

        ]


        # ---------------------------------
        # META TAGS
        # ---------------------------------

        for name in meta_names:

            tag = soup.find(

                "meta",

                attrs={
                    "property": name
                }

            )


            if not tag:

                tag = soup.find(

                    "meta",

                    attrs={
                        "name": name
                    }

                )


            if tag:

                value = tag.get(
                    "content",
                    ""
                )


                if value:

                    return value.strip()


        # ---------------------------------
        # JSON-LD
        # ---------------------------------

        scripts = soup.find_all(

            "script",

            type="application/ld+json"

        )


        for script in scripts:

            text = script.get_text(
                strip=True
            )


            if "datePublished" not in text:
                continue


            try:

                match = re.search(

                    r'"datePublished"\s*:\s*"([^"]+)"',

                    text

                )


                if match:

                    return match.group(
                        1
                    )


            except Exception:

                pass


        # ---------------------------------
        # TIME TAG
        # ---------------------------------

        time_tag = soup.find(
            "time"
        )


        if time_tag:

            value = time_tag.get(
                "datetime",
                ""
            )


            if value:

                return value.strip()


            text = time_tag.get_text(

                " ",

                strip=True

            )


            if text:

                return text


        return ""


    # =================================
    # FETCH PAGE
    # =================================

    def fetch_page(self, url):

        try:

            response = requests.get(

                url,

                headers=self.headers,

                timeout=20

            )


            if response.status_code != 200:

                print(
                    "Page status:",
                    response.status_code
                )

                return {

                    "content": "",
                    "date": "",
                    "page_title": ""

                }


            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )


            # ---------------------------------
            # PAGE TITLE
            # ---------------------------------

            page_title = ""

            if soup.title:

                page_title = (
                    soup.title.get_text(
                        " ",
                        strip=True
                    )
                )


            # ---------------------------------
            # DATE
            # ---------------------------------

            date = self.extract_date(
                soup
            )


            # ---------------------------------
            # REMOVE UNWANTED ELEMENTS
            # ---------------------------------

            for tag in soup.find_all([

                "script",
                "style",
                "noscript",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "iframe"

            ]):

                tag.decompose()


            # ---------------------------------
            # ARTICLE
            # ---------------------------------

            article = soup.find(
                "article"
            )


            if article:

                text = article.get_text(

                    " ",

                    strip=True

                )


            else:

                main = soup.find(
                    "main"
                )


                if main:

                    text = main.get_text(

                        " ",

                        strip=True

                    )

                else:

                    text = soup.get_text(

                        " ",

                        strip=True

                    )


            text = " ".join(
                text.split()
            )


            # ---------------------------------
            # CONTENT LIMIT
            # ---------------------------------

            text = text[:12000]


            return {

                "content": text,

                "date": date,

                "page_title": page_title

            }


        except Exception as e:

            print(
                "Page fetch error:",
                e
            )

            return {

                "content": "",
                "date": "",
                "page_title": ""

            }


    # =================================
    # RESEARCH
    # =================================

    def research(

        self,
        query,
        max_results=5

    ):

        return self.search(

            query,
            max_results

        )
