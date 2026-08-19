"""
AKHIM AI - Research Evidence Engine

Purpose:
    Evaluate, clean, enrich and filter research evidence.

Designed to work with:
    WebSearch
    ResearchVerifier
    ResearchFreshness
    ResearchRanker
    ResearchAnalyzer

Important:
    This module does NOT decide whether a claim is true.
    It estimates how useful and trustworthy a source is
    as research evidence.
"""

import re
from urllib.parse import urlparse, unquote


class ResearchEvidence:

    VERSION = "3.0"

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        # -----------------------------------------------------
        # Words that usually indicate navigation/category pages.
        # -----------------------------------------------------

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
            "topics",
            "topic",
            "page",
            "feed",
            "login",
            "signup",
            "register"
        }

        # -----------------------------------------------------
        # Domains that are usually weak as primary evidence.
        # -----------------------------------------------------

        self.weak_domains = {
            "pinterest.com",
            "facebook.com",
            "instagram.com",
            "tiktok.com",
            "x.com",
            "twitter.com"
        }

        # -----------------------------------------------------
        # Domains that can provide stronger first-party evidence.
        # -----------------------------------------------------

        self.high_trust_domains = {
            "gov.in",
            "nic.in",
            "india.gov.in",
            "pib.gov.in",
            "who.int",
            "un.org",
            "nature.com",
            "science.org",
            "reuters.com",
            "apnews.com",
            "bbc.com"
        }

        # -----------------------------------------------------
        # URL extensions that are generally not useful
        # for article evidence.
        # -----------------------------------------------------

        self.bad_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".mp4",
            ".mp3",
            ".zip",
            ".rar",
            ".exe"
        }

        # -----------------------------------------------------
        # Common tracking parameters.
        # -----------------------------------------------------

        self.tracking_parameters = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid"
        }

        # -----------------------------------------------------
        # Date patterns.
        # -----------------------------------------------------

        self.date_patterns = [

            r"\b20\d{2}-\d{1,2}-\d{1,2}\b",

            r"\b20\d{2}/\d{1,2}/\d{1,2}\b",

            r"\b\d{1,2}/\d{1,2}/20\d{2}\b",

            r"\b\d{1,2}-\d{1,2}-20\d{2}\b",

            r"\b(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+\d{1,2},?\s+20\d{2}\b",

            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
            r"Oct|Nov|Dec)\.?\s+\d{1,2},?\s+20\d{2}\b",

            r"\b\d{1,2}\s+(?:January|February|March|April|"
            r"May|June|July|August|September|October|"
            r"November|December)\s+20\d{2}\b"
        ]

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    def normalize(self, text):

        if text is None:
            return ""

        try:
            text = str(text)
        except Exception:
            return ""

        text = text.replace(
            "\u00a0",
            " "
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip().lower()

    # =========================================================
    # NORMALIZE DOMAIN
    # =========================================================

    def normalize_domain(self, domain):

        domain = self.normalize(
            domain
        )

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
    # GET DOMAIN
    # =========================================================

    def get_domain(self, result):

        if not isinstance(
            result,
            dict
        ):
            return ""

        url = str(
            result.get(
                "url",
                ""
            )
        ).strip()

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
    # DOMAIN MATCH
    # =========================================================

    def domain_matches(
        self,
        domain,
        trusted_domain
    ):

        domain = self.normalize_domain(
            domain
        )

        trusted_domain = self.normalize_domain(
            trusted_domain
        )

        if not domain or not trusted_domain:
            return False

        return (
            domain == trusted_domain
            or domain.endswith(
                "." + trusted_domain
            )
        )

    # =========================================================
    # CANONICAL URL
    # =========================================================

    def canonical_url(
        self,
        url
    ):

        if not url:
            return ""

        try:

            parsed = urlparse(
                str(url).strip()
            )

            scheme = (
                parsed.scheme.lower()
            )

            domain = self.normalize_domain(
                parsed.netloc
            )

            path = unquote(
                parsed.path
            )

            path = re.sub(
                r"/+",
                "/",
                path
            )

            path = path.rstrip(
                "/"
            )

            # -------------------------------------------------
            # Remove obvious tracking query parameters.
            # -------------------------------------------------

            query_parts = []

            if parsed.query:

                for pair in parsed.query.split(
                    "&"
                ):

                    if not pair:
                        continue

                    if "=" in pair:

                        key = pair.split(
                            "=",
                            1
                        )[0].lower()

                    else:

                        key = pair.lower()

                    if key in self.tracking_parameters:
                        continue

                    query_parts.append(
                        pair
                    )

            query = "&".join(
                query_parts
            )

            result = (
                f"{scheme}://{domain}"
                f"{path}"
            )

            if query:
                result += "?" + query

            return result

        except Exception:

            return self.normalize(
                url
            )

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
                str(url).strip()
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
    # BAD URL
    # =========================================================

    def is_bad_url(
        self,
        url
    ):

        if not self.is_valid_url(
            url
        ):
            return True

        text = self.normalize(
            url
        )

        # -----------------------------------------------------
        # Bad file types.
        # -----------------------------------------------------

        lower_url = text.split(
            "?",
            1
        )[0]

        for extension in self.bad_extensions:

            if lower_url.endswith(
                extension
            ):
                return True

        # -----------------------------------------------------
        # Navigation-like path segments.
        # -----------------------------------------------------

        try:

            parsed = urlparse(
                text
            )

            path_parts = [
                part
                for part in parsed.path.split("/")
                if part
            ]

            for part in path_parts:

                clean_part = re.sub(
                    r"[^a-z0-9_-]",
                    "",
                    part.lower()
                )

                if clean_part in self.blocked_words:

                    # Search/category URLs are bad
                    # only when they appear as a path segment.
                    return True

        except Exception:

            return True

        return False

    # =========================================================
    # URL QUALITY
    # =========================================================

    def url_quality(
        self,
        result
    ):

        url = str(
            result.get(
                "url",
                ""
            )
        ).strip()

        if not self.is_valid_url(
            url
        ):
            return 0

        if self.is_bad_url(
            url
        ):
            return 0

        score = 0

        try:

            parsed = urlparse(
                url
            )

            # HTTPS
            if parsed.scheme.lower() == "https":
                score += 3

            # Domain
            if parsed.netloc:
                score += 2

            # Meaningful path
            path = parsed.path.strip(
                "/"
            )

            if path:
                score += 2

            # Article-like URL
            if len(path.split("/")) >= 2:
                score += 1

            # Avoid excessive query parameters.
            if len(
                parsed.query
            ) > 150:
                score -= 1

        except Exception:

            return 0

        return max(
            0,
            min(score, 8)
        )

    # =========================================================
    # TITLE QUALITY
    # =========================================================

    def is_weak_title(
        self,
        title
    ):

        if not title:
            return True

        text = self.normalize(
            title
        )

        if len(text) < 10:
            return True

        # Very short titles are usually poor evidence.
        if len(text.split()) < 3:
            return True

        # Navigation titles.
        for word in self.blocked_words:

            if (
                text == word
                or text.startswith(
                    word + " "
                )
            ):

                return True

        return False

    # =========================================================
    # TITLE QUALITY SCORE
    # =========================================================

    def title_quality(
        self,
        result
    ):

        title = self.normalize(
            result.get(
                "title",
                ""
            )
        )

        if not title:
            return 0

        if self.is_weak_title(
            title
        ):
            return 0

        score = 0

        words = title.split()

        length = len(
            title
        )

        if length >= 20:
            score += 2

        if length >= 40:
            score += 1

        if len(words) >= 5:
            score += 2

        if len(words) >= 8:
            score += 1

        # Excessively long titles can be SEO spam.
        if length > 220:
            score -= 1

        return max(
            0,
            min(score, 6)
        )

    # =========================================================
    # CONTENT EXTRACTION
    # =========================================================

    def get_content(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):
            return ""

        content = str(
            result.get(
                "content",
                ""
            )
        ).strip()

        return content

    # =========================================================
    # SNIPPET
    # =========================================================

    def get_snippet(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):
            return ""

        return str(
            result.get(
                "snippet",
                ""
            )
        ).strip()

    # =========================================================
    # REAL CONTENT
    # =========================================================

    def has_real_content(
        self,
        result
    ):

        content = self.get_content(
            result
        )

        snippet = self.get_snippet(
            result
        )

        if len(content) >= 300:
            return True

        if len(snippet) >= 100:
            return True

        if (
            len(content) >= 150
            and len(snippet) >= 50
        ):
            return True

        return False

    # =========================================================
    # CONTENT QUALITY SCORE
    # =========================================================

    def content_quality(
        self,
        result
    ):

        content = self.get_content(
            result
        )

        snippet = self.get_snippet(
            result
        )

        score = 0

        content_length = len(
            content
        )

        snippet_length = len(
            snippet
        )

        if content_length >= 1000:
            score += 6

        elif content_length >= 600:
            score += 5

        elif content_length >= 300:
            score += 4

        elif content_length >= 150:
            score += 2

        elif content_length > 0:
            score += 1

        if snippet_length >= 200:
            score += 2

        elif snippet_length >= 100:
            score += 1

        # -----------------------------------------------------
        # Content richness.
        # -----------------------------------------------------

        text = self.normalize(
            content
        )

        if text:

            sentence_count = len(
                re.findall(
                    r"[.!?।]",
                    text
                )
            )

            if sentence_count >= 5:
                score += 2

            elif sentence_count >= 2:
                score += 1

        return max(
            0,
            min(score, 10)
        )

    # =========================================================
    # DATE SIGNAL
    # =========================================================

    def has_date_signal(
        self,
        result
    ):

        date_value = str(
            result.get(
                "date",
                ""
            )
        ).strip()

        if date_value:
            return True

        text = " ".join(
            [
                str(
                    result.get(
                        "title",
                        ""
                    )
                ),
                str(
                    result.get(
                        "content",
                        ""
                    )
                ),
                str(
                    result.get(
                        "snippet",
                        ""
                    )
                )
            ]
        )

        for pattern in self.date_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False

    # =========================================================
    # DATE QUALITY
    # =========================================================

    def date_quality(
        self,
        result
    ):

        if result.get(
            "date"
        ):

            return 3

        if result.get(
            "date_source"
        ):

            return 3

        if self.has_date_signal(
            result
        ):

            return 2

        return 0

    # =========================================================
    # SOURCE QUALITY
    # =========================================================

    def source_quality(
        self,
        result
    ):

        domain = self.get_domain(
            result
        )

        if not domain:
            return 0

        score = 0

        # -----------------------------------------------------
        # Strong known domains.
        # -----------------------------------------------------

        for trusted in self.high_trust_domains:

            if self.domain_matches(
                domain,
                trusted
            ):

                score += 8
                break

        # -----------------------------------------------------
        # Weak domains.
        # -----------------------------------------------------

        for weak in self.weak_domains:

            if self.domain_matches(
                domain,
                weak
            ):

                score -= 5
                break

        # -----------------------------------------------------
        # Government domains.
        # -----------------------------------------------------

        if (
            domain.endswith(
                ".gov.in"
            )
            or domain == "gov.in"
        ):

            score += 10

        # -----------------------------------------------------
        # Academic domains.
        # -----------------------------------------------------

        if (
            domain.endswith(
                ".edu"
            )
            or domain.endswith(
                ".ac.in"
            )
        ):

            score += 5

        # -----------------------------------------------------
        # Organization domains.
        # -----------------------------------------------------

        if domain.endswith(
            ".org"
        ):

            score += 2

        return max(
            0,
            min(score, 15)
        )

    # =========================================================
    # SOURCE TYPE
    # =========================================================

    def source_type(
        self,
        result
    ):

        domain = self.get_domain(
            result
        )

        if not domain:
            return "UNKNOWN"

        if (
            domain.endswith(
                ".gov.in"
            )
            or domain == "gov.in"
        ):

            return "GOVERNMENT"

        if (
            domain.endswith(".edu")
            or domain.endswith(".ac.in")
        ):

            return "ACADEMIC"

        for domain_name in self.high_trust_domains:

            if self.domain_matches(
                domain,
                domain_name
            ):

                return "ESTABLISHED"

        for weak in self.weak_domains:

            if self.domain_matches(
                domain,
                weak
            ):

                return "SOCIAL"

        if domain.endswith(
            ".org"
        ):

            return "ORGANIZATION"

        return "GENERAL"

    # =========================================================
    # SOURCE SIGNAL
    # =========================================================

    def source_signal(
        self,
        result
    ):

        source_type = self.source_type(
            result
        )

        if source_type == "GOVERNMENT":
            return 5

        if source_type == "ACADEMIC":
            return 5

        if source_type == "ESTABLISHED":
            return 4

        if source_type == "ORGANIZATION":
            return 3

        if source_type == "GENERAL":
            return 2

        if source_type == "SOCIAL":
            return 0

        return 1

    # =========================================================
    # QUERY RELEVANCE
    # =========================================================

    def query_relevance(
        self,
        result,
        query=""
    ):

        if not query:
            return 0

        query_words = self.tokenize(
            query
        )

        if not query_words:
            return 0

        text = " ".join(
            [
                str(
                    result.get(
                        "title",
                        ""
                    )
                ),
                str(
                    result.get(
                        "snippet",
                        ""
                    )
                ),
                str(
                    result.get(
                        "content",
                        ""
                    )[:4000]
                )
            ]
        )

        result_words = self.tokenize(
            text
        )

        if not result_words:
            return 0

        matched = (
            query_words
            & result_words
        )

        ratio = (
            len(matched)
            / len(query_words)
        )

        if ratio >= 0.8:
            return 8

        if ratio >= 0.6:
            return 6

        if ratio >= 0.4:
            return 4

        if ratio >= 0.2:
            return 2

        return 0

    # =========================================================
    # TOKENIZER
    # =========================================================

    def tokenize(
        self,
        text
    ):

        text = self.normalize(
            text
        )

        if not text:
            return set()

        # -----------------------------------------------------
        # Keep English + Assamese Unicode characters.
        # -----------------------------------------------------

        tokens = re.findall(
            r"[^\W_]+",
            text,
            flags=re.UNICODE
        )

        # Remove extremely short tokens.
        return {
            token
            for token in tokens
            if len(token) >= 2
        }

    # =========================================================
    # DUPLICATE SIGNATURE
    # =========================================================

    def content_signature(
        self,
        result
    ):

        text = " ".join(
            [
                str(
                    result.get(
                        "title",
                        ""
                    )
                ),
                str(
                    result.get(
                        "content",
                        ""
                    )
                )
            ]
        )

        words = self.tokenize(
            text
        )

        if not words:
            return ""

        return " ".join(
            sorted(
                words
            )
        )

    # =========================================================
    # DUPLICATE DETECTION
    # =========================================================

    def similarity(
        self,
        text1,
        text2
    ):

        words1 = self.tokenize(
            text1
        )

        words2 = self.tokenize(
            text2
        )

        if not words1 or not words2:
            return 0.0

        intersection = (
            words1 & words2
        )

        union = (
            words1 | words2
        )

        if not union:
            return 0.0

        return (
            len(intersection)
            / len(union)
        )

    # =========================================================
    # FIND DUPLICATES
    # =========================================================

    def remove_duplicates(
        self,
        results
    ):

        if not results:
            return []

        output = []

        seen_urls = set()

        seen_domains_titles = set()

        for result in results:

            if not isinstance(
                result,
                dict
            ):
                continue

            url = self.canonical_url(
                result.get(
                    "url",
                    ""
                )
            )

            if url and url in seen_urls:
                continue

            domain = self.get_domain(
                result
            )

            title = self.normalize(
                result.get(
                    "title",
                    ""
                )
            )

            domain_title_key = (
                domain,
                title
            )

            if (
                title
                and domain_title_key
                in seen_domains_titles
            ):
                continue

            # -------------------------------------------------
            # Near-duplicate content detection.
            # -------------------------------------------------

            duplicate = False

            current_text = (
                str(
                    result.get(
                        "title",
                        ""
                    )
                )
                + " "
                + str(
                    result.get(
                        "snippet",
                        ""
                    )
                )
            )

            for existing in output:

                existing_text = (
                    str(
                        existing.get(
                            "title",
                            ""
                        )
                    )
                    + " "
                    + str(
                        existing.get(
                            "snippet",
                            ""
                        )
                    )
                )

                sim = self.similarity(
                    current_text,
                    existing_text
                )

                if sim >= 0.82:

                    duplicate = True
                    break

            if duplicate:
                continue

            if url:
                seen_urls.add(
                    url
                )

            if title:
                seen_domains_titles.add(
                    domain_title_key
                )

            output.append(
                result
            )

        return output

    # =========================================================
    # SOURCE DIVERSITY
    # =========================================================

    def source_diversity_bonus(
        self,
        result,
        results
    ):

        domain = self.get_domain(
            result
        )

        if not domain:
            return 0

        count = 0

        for item in results:

            if (
                self.get_domain(
                    item
                )
                == domain
            ):

                count += 1

        if count <= 1:
            return 4

        if count == 2:
            return 2

        return 0

    # =========================================================
    # MAIN SCORE
    # =========================================================

    def score(
        self,
        result,
        query=""
    ):

        if not isinstance(
            result,
            dict
        ):
            return 0

        score = 0

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        score += self.title_quality(
            result
        )

        # -----------------------------------------------------
        # URL
        # -----------------------------------------------------

        score += self.url_quality(
            result
        )

        # -----------------------------------------------------
        # Content
        # -----------------------------------------------------

        score += self.content_quality(
            result
        )

        # -----------------------------------------------------
        # Date
        # -----------------------------------------------------

        score += self.date_quality(
            result
        )

        # -----------------------------------------------------
        # Domain
        # -----------------------------------------------------

        score += self.source_quality(
            result
        )

        # -----------------------------------------------------
        # Source type
        # -----------------------------------------------------

        score += self.source_signal(
            result
        )

        # -----------------------------------------------------
        # Query relevance
        # -----------------------------------------------------

        if query:

            score += self.query_relevance(
                result,
                query
            )

        # -----------------------------------------------------
        # Existing verification information.
        # -----------------------------------------------------

        verification = result.get(
            "verification_score",
            0
        )

        try:
            verification = float(
                verification or 0
            )
        except Exception:
            verification = 0

        if verification >= 70:
            score += 5

        elif verification >= 50:
            score += 3

        elif verification >= 30:
            score += 1

        # -----------------------------------------------------
        # Existing freshness information.
        # -----------------------------------------------------

        freshness = result.get(
            "freshness_score",
            0
        )

        try:
            freshness = float(
                freshness or 0
            )
        except Exception:
            freshness = 0

        if freshness >= 4:
            score += 4

        elif freshness >= 2:
            score += 2

        elif freshness >= 1:
            score += 1

        # -----------------------------------------------------
        # Existing agreement information.
        # -----------------------------------------------------

        agreement = result.get(
            "agreement_score",
            0
        )

        try:
            agreement = float(
                agreement or 0
            )
        except Exception:
            agreement = 0

        if agreement >= 30:
            score += 4

        elif agreement >= 15:
            score += 2

        elif agreement >= 5:
            score += 1

        return max(
            0,
            round(score, 2)
        )

    # =========================================================
    # EVIDENCE LEVEL
    # =========================================================

    def evidence_level(
        self,
        score
    ):

        try:
            score = float(
                score
            )
        except Exception:
            score = 0

        if score >= 45:
            return "STRONG"

        if score >= 30:
            return "GOOD"

        if score >= 18:
            return "MODERATE"

        if score >= 10:
            return "WEAK"

        return "VERY_WEAK"

    # =========================================================
    # ENRICH ONE
    # =========================================================

    def enrich_one(
        self,
        result,
        query="",
        results=None
    ):

        item = dict(
            result
        )

        evidence_score = self.score(
            item,
            query=query
        )

        item["evidence_score"] = (
            evidence_score
        )

        item["evidence_level"] = (
            self.evidence_level(
                evidence_score
            )
        )

        item["source_type"] = (
            self.source_type(
                item
            )
        )

        item["domain"] = (
            self.get_domain(
                item
            )
        )

        item["canonical_url"] = (
            self.canonical_url(
                item.get(
                    "url",
                    ""
                )
            )
        )

        item["content_length"] = len(
            self.get_content(
                item
            )
        )

        item["has_content"] = (
            self.has_real_content(
                item
            )
        )

        item["has_date"] = (
            self.has_date_signal(
                item
            )
        )

        if results is not None:

            item["source_diversity_bonus"] = (
                self.source_diversity_bonus(
                    item,
                    results
                )
            )

        else:

            item["source_diversity_bonus"] = 0

        return item

    # =========================================================
    # ENRICH ALL
    # =========================================================

    def enrich(
        self,
        results,
        query=""
    ):

        if not results:
            return []

        valid = [
            item
            for item in results
            if isinstance(
                item,
                dict
            )
        ]

        valid = self.remove_duplicates(
            valid
        )

        output = []

        for result in valid:

            item = self.enrich_one(
                result,
                query=query,
                results=valid
            )

            output.append(
                item
            )

        return output

    # =========================================================
    # FILTER
    # =========================================================

    def filter(
        self,
        results,
        minimum_score=10
    ):

        if not results:
            return []

        output = []

        try:

            minimum_score = float(
                minimum_score
            )

        except Exception:

            minimum_score = 10

        for result in results:

            if not isinstance(
                result,
                dict
            ):
                continue

            url = result.get(
                "url",
                ""
            )

            title = result.get(
                "title",
                ""
            )

            if self.is_bad_url(
                url
            ):
                continue

            if self.is_weak_title(
                title
            ):
                continue

            if not self.has_real_content(
                result
            ):
                continue

            score = result.get(
                "evidence_score",
                0
            )

            try:
                score = float(
                    score or 0
                )
            except Exception:
                score = 0

            if score < minimum_score:
                continue

            output.append(
                result
            )

        return output

    # =========================================================
    # SORT
    # =========================================================

    def sort(
        self,
        results
    ):

        if not results:
            return []

        return sorted(

            results,

            key=lambda item: (

                float(
                    item.get(
                        "evidence_score",
                        0
                    ) or 0
                ),

                float(
                    item.get(
                        "verification_score",
                        0
                    ) or 0
                ),

                float(
                    item.get(
                        "freshness_score",
                        0
                    ) or 0
                ),

                float(
                    item.get(
                        "agreement_score",
                        0
                    ) or 0
                ),

                float(
                    item.get(
                        "content_length",
                        0
                    ) or 0
                )

            ),

            reverse=True
        )

    # =========================================================
    # PROCESS
    # =========================================================

    def process(
        self,
        results,
        query="",
        minimum_score=10
    ):

        if not results:
            return []

        # -----------------------------------------------------
        # Step 1: Enrich
        # -----------------------------------------------------

        results = self.enrich(
            results,
            query=query
        )

        # -----------------------------------------------------
        # Step 2: Filter
        # -----------------------------------------------------

        results = self.filter(
            results,
            minimum_score=minimum_score
        )

        if not results:
            return []

        # -----------------------------------------------------
        # Step 3: Recalculate after filtering.
        # -----------------------------------------------------

        results = self.enrich(
            results,
            query=query
        )

        # -----------------------------------------------------
        # Step 4: Sort
        # -----------------------------------------------------

        results = self.sort(
            results
        )

        return results

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    def evidence_score(
        self,
        result,
        query=""
    ):

        return self.score(
            result,
            query=query
        )