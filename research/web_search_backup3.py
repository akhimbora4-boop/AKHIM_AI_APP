import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote


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

    # --------------------------------
    # Clean DuckDuckGo URL
    # --------------------------------

    def clean_url(self, url):

        if not url:
            return ""

        try:

            parsed = urlparse(url)

            if "duckduckgo.com" in parsed.netloc:

                query = parse_qs(parsed.query)

                if "uddg" in query:

                    return unquote(
                        query["uddg"][0]
                    )

            return url

        except Exception:

            return url

    # --------------------------------
    # Get source/domain
    # --------------------------------

    def get_source(self, url):

        try:

            domain = urlparse(url).netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            return domain

        except Exception:

            return ""

    # --------------------------------
    # Check if URL is useful
    # --------------------------------

    def is_homepage(self, url):

        try:

            parsed = urlparse(url)

            path = parsed.path.strip("/")

            if not path:
                return True

            homepage_paths = [
                "technology/artificial-intelligence",
                "technology/artificial-intelligence/",
                "ai-news",
                "latest",
                "news",
                "technology",
                "artificial-intelligence"
            ]

            if path in homepage_paths:
                return True

            return False

        except Exception:

            return False

    # --------------------------------
    # Search DuckDuckGo
    # --------------------------------

    def search(
        self,
        query,
        max_results=5
    ):

        url = (
            "https://html.duckduckgo.com/html/"
        )

        try:

            response = requests.post(
                url,
                data={"q": query},
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

            results = []

            seen_urls = set()

            for item in soup.select(".result"):

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

                # Ignore DuckDuckGo internal links
                if "duckduckgo.com" in source:
                    continue

                # Ignore advertisements
                if "Ad Viewing ads" in title_text:
                    continue

                # Ignore duplicate URLs
                if url_text in seen_urls:
                    continue

                # Ignore generic homepages
                if self.is_homepage(url_text):
                    continue

                seen_urls.add(url_text)

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

        except Exception as e:

            print(
                "Search error:",
                e
            )

            return []

    # --------------------------------
    # Extract date
    # --------------------------------

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

        # JSON-LD

        scripts = soup.find_all(
            "script",
            type="application/ld+json"
        )

        for script in scripts:

            text = script.get_text(
                strip=True
            )

            if "datePublished" in text:

                try:

                    import re

                    match = re.search(
                        r'"datePublished"\s*:\s*"([^"]+)"',
                        text
                    )

                    if match:

                        return match.group(1)

                except Exception:

                    pass

        # HTML time tag

        time_tag = soup.find("time")

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

    # --------------------------------
    # Fetch webpage
    # --------------------------------

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

            # Page title

            page_title = ""

            if soup.title:

                page_title = soup.title.get_text(
                    " ",
                    strip=True
                )

            # Date

            date = self.extract_date(
                soup
            )

            # Remove unwanted elements

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

            # Prefer article

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

            # Limit content

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

    # --------------------------------
    # Research
    # --------------------------------

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

            # Only keep pages with content

            if result["content"]:

                valid_results.append(
                    result
                )

            else:

                print(
                    "Skipped: no page content"
                )

        return valid_results
