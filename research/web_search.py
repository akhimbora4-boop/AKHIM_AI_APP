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

    def search(
        self,
        query,
        max_results=5
    ):

        url = (
            "https://html.duckduckgo.com/html/"
        )

        try:

            today = datetime.now()

            current_year = today.year

            q_lower = query.lower()

            current_words = [

                "current",
                "latest",
                "recent",
                "today",
                "now",
                "currently",
                "news",
                "বৰ্তমান",
                "আজিৰ",
                "শেহতীয়া",
                "সাম্প্ৰতিক",
                "খবৰ"

            ]

            is_current = any(
                word in q_lower
                for word in current_words
            )

            if is_current:

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
                return []


            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )


            results = []

            seen_urls = set()

            seen_sources = set()


            blocked_domains = {

                "duckduckgo.com",
                "news.google.com"

            }


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


                source = self.get_source(
                    url_text
                )


                if not source:
                    continue


                if source in blocked_domains:
                    continue

                if source.endswith(
                    "news.google.com"
                ):
                    continue

                if "duckduckgo.com" in source:
                    continue

                if "Ad Viewing ads" in title_text:
                    continue

                if url_text in seen_urls:
                    continue

                if self.is_homepage(
                    url_text
                ):
                    continue

                if source in seen_sources:
                    continue


                seen_urls.add(
                    url_text
                )

                seen_sources.add(
                    source
                )


                snippet_text = ""

                if snippet:

                    snippet_text = snippet.get_text(
                        " ",
                        strip=True
                    )


                results.append({

                    "title": title_text,

                    "url": url_text,

                    "snippet": snippet_text,

                    "source": source,

                    "date": "",

                    "page_title": "",

                    "content": ""

                })


                if len(results) >= max_results:

                    break


            return results


        except Exception:

            return []

    def extract_date(self, soup):

        meta_names = [

            "article:published_time",
            "article:modified_time",
            "datePublished",
            "date",
            "pubdate",
            "publishdate",
            "timestamp"

        ]

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


        return ""

    def fetch_page(self, url):

        try:

            response = requests.get(

                url,

                headers=self.headers,

                timeout=20

            )


            if response.status_code != 200:
                return {
                    "content": "",
                    "date": "",
                    "page_title": ""
                }


            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )


            page_title = ""

            if soup.title:

                page_title = soup.title.get_text(
                    " ",
                    strip=True
                )


            date = self.extract_date(
                soup
            )


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

            text = text[:12000]


            return {

                "content": text,

                "date": date,

                "page_title": page_title

            }


        except Exception:

            return {

                "content": "",

                "date": "",

                "page_title": ""

            }

    def research(
        self,
        query,
        max_results=5
    ):

        results = self.search(
            query,
            max_results
        )


        valid_results = []


        for result in results:

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

                valid_results.append(
                    result
                )


        return valid_results
