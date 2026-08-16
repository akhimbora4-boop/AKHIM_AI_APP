import re
from urllib.parse import urlparse


class ResearchEvidence:

    def __init__(self):
        self.blocked_words = {
            "category",
            "categories",
            "tag",
            "tags",
            "archive",
            "archives",
            "search",
            "homepage",
            "home",
            "daily-ai-news",
        }

        self.weak_domains = {
            "pinterest.com",
            "facebook.com",
            "instagram.com",
            "tiktok.com",
        }


    def normalize(self, text):
        if text is None:
            return ""

        return " ".join(
            str(text).strip().lower().split()
        )


    def get_domain(self, result):
        url = str(
            result.get("url", "")
        ).strip()

        if not url:
            return ""

        try:
            domain = urlparse(url).netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            return domain

        except Exception:
            return ""


    def is_bad_url(self, url):
        if not url:
            return True

        text = self.normalize(url)

        for word in self.blocked_words:
            if word in text:
                return True

        return False


    def is_weak_title(self, title):
        if not title:
            return True

        text = self.normalize(title)

        if len(text) < 10:
            return True

        for word in self.blocked_words:
            if word in text:
                return True

        return False


    def has_real_content(self, result):
        content = str(
            result.get("content", "")
        ).strip()

        snippet = str(
            result.get("snippet", "")
        ).strip()

        if len(content) >= 250:
            return True

        if len(snippet) >= 80:
            return True

        return False


    def has_date_signal(self, result):
        date_value = str(
            result.get("date", "")
        ).strip()

        if date_value:
            return True

        text = (
            str(result.get("content", ""))
            + " "
            + str(result.get("snippet", ""))
        )

        patterns = [
            r"\b20\d{2}-\d{1,2}-\d{1,2}\b",
            r"\b\d{1,2}/\d{1,2}/20\d{2}\b",
            r"\b(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{1,2},\s+20\d{2}\b",
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
            r"Oct|Nov|Dec)\.?\s+\d{1,2},\s+20\d{2}\b",
        ]

        for pattern in patterns:
            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False


    def score(self, result):
        score = 0

        title = result.get(
            "title",
            ""
        )

        if title and not self.is_weak_title(title):
            score += 2

        url = result.get(
            "url",
            ""
        )

        if url and not self.is_bad_url(url):
            score += 2

        if self.has_real_content(result):
            score += 3

        if self.has_date_signal(result):
            score += 2

        domain = self.get_domain(result)

        if domain:
            score += 1

        for weak in self.weak_domains:
            if (
                domain == weak
                or domain.endswith("." + weak)
            ):
                score -= 2

        if score < 0:
            score = 0

        return score


    def enrich(self, results):
        output = []

        for result in results:
            item = dict(result)

            item["evidence_score"] = self.score(
                item
            )

            output.append(item)

        return output


    def filter(self, results):
        if not results:
            return []

        output = []

        for result in results:

            if self.is_bad_url(
                result.get("url", "")
            ):
                continue

            if self.is_weak_title(
                result.get("title", "")
            ):
                continue

            if not self.has_real_content(result):
                continue

            output.append(result)

        return output


    def sort(self, results):
        return sorted(
            results,
            key=lambda item: (
                item.get("evidence_score", 0),
                item.get("freshness_score", 0)
            ),
            reverse=True
        )


    def process(self, results):
        if not results:
            return []

        results = self.enrich(results)

        results = self.filter(results)

        results = self.enrich(results)

        results = self.sort(results)

        return results


    def evidence_score(self, result):
        return self.score(result)