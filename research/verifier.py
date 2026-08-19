import re
from datetime import datetime, timezone
from urllib.parse import urlparse


class ResearchVerifier:
    """
    AKHIM AI Research Verification Engine

    Responsibilities:
        - Evaluate source reliability
        - Evaluate content quality
        - Measure question relevance
        - Measure cross-source agreement
        - Detect conflicting evidence
        - Detect duplicate sources
        - Evaluate freshness
        - Evaluate source diversity
        - Produce verification confidence
        - Prevent weak evidence from being treated as confirmed
    """

    VERSION = "3.0"

    # =========================================================
    # SCORE LIMITS
    # =========================================================

    MAX_TRUST_SCORE = 40
    MAX_CONTENT_SCORE = 20
    MAX_RELEVANCE_SCORE = 20
    MAX_AGREEMENT_SCORE = 25
    MAX_FRESHNESS_SCORE = 10
    MAX_QUALITY_BONUS = 10
    MAX_PENALTY = 30

    # =========================================================
    # DOMAIN DATABASE
    # =========================================================

    HIGH_TRUST_DOMAINS = {
        "gov.in",
        "nic.in",
        "india.gov.in",
        "pib.gov.in",
        "mygov.in",

        "who.int",
        "un.org",
        "unesco.org",
        "worldbank.org",
        "imf.org",

        "nature.com",
        "science.org",
        "sciencedirect.com",
        "springer.com",
        "ieee.org",
        "acm.org",
        "nih.gov",
        "ncbi.nlm.nih.gov",

        "reuters.com",
        "apnews.com",
        "bbc.com",

        "openai.com",
        "google.com",
        "microsoft.com",
        "apple.com",
        "github.com"
    }

    ACADEMIC_DOMAINS = {
        "nature.com",
        "science.org",
        "sciencedirect.com",
        "springer.com",
        "ieee.org",
        "acm.org",
        "nih.gov",
        "ncbi.nlm.nih.gov",
        "pubmed.ncbi.nlm.nih.gov"
    }

    GOVERNMENT_SUFFIXES = {
        "gov.in",
        "nic.in"
    }

    NEWS_DOMAINS = {
        "reuters.com",
        "apnews.com",
        "bbc.com",
        "nytimes.com",
        "theguardian.com",
        "aljazeera.com"
    }

    OFFICIAL_DOMAINS = {
        "openai.com",
        "google.com",
        "microsoft.com",
        "apple.com",
        "github.com"
    }

    WEAK_DOMAINS = {
        "blogspot.com",
        "wordpress.com",
        "medium.com",
        "facebook.com",
        "instagram.com",
        "x.com",
        "twitter.com",
        "pinterest.com",
        "quora.com"
    }

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(self, now=None):

        self.now = now or datetime.now(
            timezone.utc
        )

    # =========================================================
    # BASIC TEXT HELPERS
    # =========================================================

    def safe_text(self, value):

        if value is None:
            return ""

        try:
            return str(value).strip()
        except Exception:
            return ""

    def normalize(self, text):

        text = self.safe_text(text)

        if not text:
            return ""

        text = text.lower()

        text = re.sub(
            r"https?://\S+",
            " ",
            text
        )

        # Preserve Unicode letters.
        text = re.sub(
            r"[^\w\s]",
            " ",
            text,
            flags=re.UNICODE
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def word_set(self, text):

        normalized = self.normalize(
            text
        )

        if not normalized:
            return set()

        return set(
            normalized.split()
        )

    # =========================================================
    # URL / DOMAIN
    # =========================================================

    def get_domain(self, result):

        if not isinstance(
            result,
            dict
        ):
            return ""

        url = self.safe_text(
            result.get("url")
        )

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            domain = (
                parsed.netloc
                or parsed.path.split("/")[0]
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

        except Exception:

            return ""

    def get_url(self, result):

        if not isinstance(
            result,
            dict
        ):
            return ""

        return self.safe_text(
            result.get("url")
        )

    def is_https(self, result):

        url = self.get_url(
            result
        )

        return url.lower().startswith(
            "https://"
        )

    def domain_matches(
        self,
        domain,
        trusted_domain
    ):

        if not domain:
            return False

        if not trusted_domain:
            return False

        return (
            domain == trusted_domain
            or domain.endswith(
                "." + trusted_domain
            )
        )

    # =========================================================
    # SOURCE CLASSIFICATION
    # =========================================================

    def source_type(self, result):

        domain = self.get_domain(
            result
        )

        if not domain:
            return "UNKNOWN"

        for item in self.GOVERNMENT_SUFFIXES:

            if self.domain_matches(
                domain,
                item
            ):
                return "GOVERNMENT"

        for item in self.ACADEMIC_DOMAINS:

            if self.domain_matches(
                domain,
                item
            ):
                return "ACADEMIC"

        for item in self.NEWS_DOMAINS:

            if self.domain_matches(
                domain,
                item
            ):
                return "NEWS"

        for item in self.OFFICIAL_DOMAINS:

            if self.domain_matches(
                domain,
                item
            ):
                return "OFFICIAL"

        for item in self.WEAK_DOMAINS:

            if self.domain_matches(
                domain,
                item
            ):
                return "SOCIAL_OR_BLOG"

        return "GENERAL"

    # =========================================================
    # DOMAIN TRUST
    # =========================================================

    def trust_score(self, result):

        domain = self.get_domain(
            result
        )

        if not domain:
            return 0

        source_type = self.source_type(
            result
        )

        if source_type == "GOVERNMENT":
            return 40

        if source_type == "ACADEMIC":
            return 40

        if source_type == "NEWS":
            return 34

        if source_type == "OFFICIAL":
            return 38

        if source_type == "SOCIAL_OR_BLOG":
            return 5

        for trusted in self.HIGH_TRUST_DOMAINS:

            if self.domain_matches(
                domain,
                trusted
            ):
                return 35

        return 15

    # =========================================================
    # URL QUALITY
    # =========================================================

    def url_quality_score(self, result):

        url = self.get_url(
            result
        )

        if not url:
            return 0

        score = 0

        if self.is_https(result):
            score += 4

        try:

            parsed = urlparse(
                url
            )

            if parsed.scheme:
                score += 2

            if parsed.netloc:
                score += 2

            if parsed.path:
                score += 1

            if len(url) < 300:
                score += 1

        except Exception:

            return 0

        return min(
            score,
            10
        )

    # =========================================================
    # CONTENT EXTRACTION
    # =========================================================

    def get_text(self, result):

        if not isinstance(
            result,
            dict
        ):
            return ""

        parts = []

        for key in (
            "title",
            "content",
            "snippet",
            "description",
            "summary"
        ):

            value = self.safe_text(
                result.get(key)
            )

            if value:
                parts.append(
                    value
                )

        return " ".join(
            parts
        )

    # =========================================================
    # CONTENT QUALITY
    # =========================================================

    def content_quality(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):
            return 0

        score = 0

        title = self.safe_text(
            result.get("title")
        )

        content = self.safe_text(
            result.get("content")
        )

        snippet = self.safe_text(
            result.get("snippet")
        )

        description = self.safe_text(
            result.get("description")
        )

        if title:
            score += 5

        if content:

            length = len(
                content
            )

            if length >= 1000:
                score += 10

            elif length >= 500:
                score += 8

            elif length >= 200:
                score += 6

            else:
                score += 3

        elif snippet:

            length = len(
                snippet
            )

            if length >= 200:
                score += 6

            else:
                score += 3

        if description:
            score += 2

        return min(
            score,
            self.MAX_CONTENT_SCORE
        )

    # =========================================================
    # QUESTION RELEVANCE
    # =========================================================

    def relevance_score(
        self,
        question,
        result
    ):

        question_words = self.word_set(
            question
        )

        result_words = self.word_set(
            self.get_text(result)
        )

        if not question_words:
            return 0

        if not result_words:
            return 0

        intersection = (
            question_words
            & result_words
        )

        ratio = (
            len(intersection)
            / len(question_words)
        )

        score = int(
            ratio
            * self.MAX_RELEVANCE_SCORE
        )

        return min(
            score,
            self.MAX_RELEVANCE_SCORE
        )

    # =========================================================
    # TEXT SIMILARITY
    # =========================================================

    def similarity(
        self,
        text1,
        text2
    ):

        words1 = self.word_set(
            text1
        )

        words2 = self.word_set(
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
    # SOURCE IDENTITY
    # =========================================================

    def source_key(self, result):

        domain = self.get_domain(
            result
        )

        if domain:
            return domain

        return self.normalize(
            result.get(
                "source",
                ""
            )
        )

    # =========================================================
    # DUPLICATE DETECTION
    # =========================================================

    def is_duplicate(
        self,
        result,
        results
    ):

        current_url = self.get_url(
            result
        ).rstrip(
            "/"
        ).lower()

        current_text = self.get_text(
            result
        )

        for other in results:

            if other is result:
                continue

            other_url = self.get_url(
                other
            ).rstrip(
                "/"
            ).lower()

            if (
                current_url
                and other_url
                and current_url == other_url
            ):
                return True

            similarity = self.similarity(
                current_text,
                self.get_text(other)
            )

            if similarity >= 0.85:
                return True

        return False

    # =========================================================
    # AGREEMENT
    # =========================================================

    def agreement_score(
        self,
        result,
        results
    ):

        current_text = self.get_text(
            result
        )

        if not current_text:
            return 0

        current_source = self.source_key(
            result
        )

        score = 0
        agreements = 0

        for other in results:

            if other is result:
                continue

            other_source = self.source_key(
                other
            )

            # Same source should not count
            # as independent confirmation.
            if (
                current_source
                and other_source
                and current_source == other_source
            ):
                continue

            similarity = self.similarity(
                current_text,
                self.get_text(other)
            )

            if similarity >= 0.50:

                score += 10
                agreements += 1

            elif similarity >= 0.35:

                score += 7
                agreements += 1

            elif similarity >= 0.22:

                score += 4
                agreements += 1

        return min(
            score,
            self.MAX_AGREEMENT_SCORE
        )

    # =========================================================
    # CONFLICT DETECTION
    # =========================================================

    def detect_conflicts(
        self,
        result,
        results
    ):

        current_text = self.get_text(
            result
        )

        if not current_text:
            return []

        conflicts = []

        current_source = self.source_key(
            result
        )

        for other in results:

            if other is result:
                continue

            other_source = self.source_key(
                other
            )

            if (
                current_source
                and other_source
                and current_source == other_source
            ):
                continue

            similarity = self.similarity(
                current_text,
                self.get_text(other)
            )

            # Low similarity does NOT automatically
            # mean contradiction.
            #
            # We mark it as potential conflict only
            # when both sources contain substantial text.
            if (
                similarity < 0.10
                and len(current_text) >= 150
                and len(self.get_text(other)) >= 150
            ):

                conflicts.append(
                    other_source
                )

        return list(
            dict.fromkeys(
                conflicts
            )
        )

    # =========================================================
    # FRESHNESS
    # =========================================================

    def parse_date(self, value):

        if not value:
            return None

        text = self.safe_text(
            value
        )

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y"
        ]

        for fmt in formats:

            try:

                return datetime.strptime(
                    text,
                    fmt
                ).replace(
                    tzinfo=timezone.utc
                )

            except ValueError:
                continue

        match = re.search(
            r"\b(20\d{2})\b",
            text
        )

        if match:

            try:

                return datetime(
                    int(
                        match.group(1)
                    ),
                    1,
                    1,
                    tzinfo=timezone.utc
                )

            except Exception:

                pass

        return None

    def freshness_score(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):
            return 0

        date_value = (
            result.get("date")
            or result.get("published")
            or result.get("published_at")
            or result.get("updated")
        )

        parsed = self.parse_date(
            date_value
        )

        if parsed is None:
            return 0

        age_days = (
            self.now - parsed
        ).days

        if age_days < 0:
            return 2

        if age_days <= 7:
            return 10

        if age_days <= 30:
            return 8

        if age_days <= 90:
            return 6

        if age_days <= 365:
            return 4

        if age_days <= 730:
            return 2

        return 0

    # =========================================================
    # QUALITY BONUS
    # =========================================================

    def quality_bonus(
        self,
        result
    ):

        score = 0

        source_type = self.source_type(
            result
        )

        if source_type in (
            "GOVERNMENT",
            "ACADEMIC"
        ):
            score += 4

        elif source_type in (
            "NEWS",
            "OFFICIAL"
        ):
            score += 3

        if self.is_https(result):
            score += 2

        if self.safe_text(
            result.get("author")
        ):
            score += 1

        if self.safe_text(
            result.get("date")
        ):
            score += 1

        if self.safe_text(
            result.get("content")
        ):
            score += 1

        return min(
            score,
            self.MAX_QUALITY_BONUS
        )

    # =========================================================
    # SUSPICIOUS CONTENT
    # =========================================================

    def suspicious_penalty(
        self,
        result
    ):

        text = self.get_text(
            result
        ).lower()

        if not text:
            return 10

        penalty = 0

        suspicious_patterns = [
            r"\bclick here\b",
            r"\bbuy now\b",
            r"\bsubscribe now\b",
            r"\b100% guaranteed\b",
            r"\bguaranteed result\b",
            r"\byou won't believe\b",
            r"\bshocking\b"
        ]

        for pattern in suspicious_patterns:

            if re.search(
                pattern,
                text
            ):

                penalty += 3

        return min(
            penalty,
            self.MAX_PENALTY
        )

    # =========================================================
    # SOURCE DIVERSITY
    # =========================================================

    def source_diversity(
        self,
        results
    ):

        sources = set()

        for result in results:

            source = self.source_key(
                result
            )

            if source:
                sources.add(
                    source
                )

        return len(
            sources
        )

    # =========================================================
    # VERIFY ONE
    # =========================================================

    def verify_one(
        self,
        result,
        results,
        question=""
    ):

        if not isinstance(
            result,
            dict
        ):
            return result

        trust = self.trust_score(
            result
        )

        content = self.content_quality(
            result
        )

        relevance = self.relevance_score(
            question,
            result
        )

        agreement = self.agreement_score(
            result,
            results
        )

        freshness = self.freshness_score(
            result
        )

        url_quality = self.url_quality_score(
            result
        )

        quality_bonus = self.quality_bonus(
            result
        )

        penalty = self.suspicious_penalty(
            result
        )

        conflicts = self.detect_conflicts(
            result,
            results
        )

        duplicate = self.is_duplicate(
            result,
            results
        )

        total = (
            trust
            + content
            + relevance
            + agreement
            + freshness
            + url_quality
            + quality_bonus
            - penalty
        )

        # Duplicate evidence must not
        # increase confidence.
        if duplicate:
            total -= 15

        # Potential conflict reduces confidence.
        if conflicts:
            total -= min(
                len(conflicts) * 5,
                15
            )

        total = max(
            0,
            min(
                100,
                total
            )
        )

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        if conflicts and total >= 60:

            status = "CONFLICTING"

        elif (
            trust >= 35
            and agreement >= 7
            and relevance >= 8
        ):

            status = "CONFIRMED"

        elif (
            trust >= 30
            and relevance >= 8
        ):

            status = "SUPPORTED"

        elif (
            trust >= 15
            and content >= 8
            and relevance >= 5
        ):

            status = "REPORTED"

        else:

            status = "UNCERTAIN"

        # -----------------------------------------------------
        # Confidence
        # -----------------------------------------------------

        if total >= 80:
            confidence = "VERY_HIGH"

        elif total >= 65:
            confidence = "HIGH"

        elif total >= 50:
            confidence = "MEDIUM"

        elif total >= 30:
            confidence = "LOW"

        else:
            confidence = "VERY_LOW"

        # -----------------------------------------------------
        # Store metadata
        # -----------------------------------------------------

        result["domain"] = self.get_domain(
            result
        )

        result["source_type"] = self.source_type(
            result
        )

        result["trust_score"] = trust

        result["content_quality_score"] = content

        result["relevance_score"] = relevance

        result["agreement_score"] = agreement

        result["freshness_score"] = freshness

        result["url_quality_score"] = url_quality

        result["quality_bonus"] = quality_bonus

        result["suspicious_penalty"] = penalty

        result["duplicate_source"] = duplicate

        result["conflicting_sources"] = conflicts

        result["verification_score"] = total

        result["verification_confidence"] = confidence

        result["status"] = status

        return result
# =========================================================
    # VERIFY ALL
    # =========================================================

    def verify(
        self,
        results,
        question=""
    ):

        if not results:
            return []

        valid = [
            result
            for result in results
            if isinstance(
                result,
                dict
            )
        ]

        if not valid:
            return []

        # -----------------------------------------------------
        # First pass
        # -----------------------------------------------------

        for result in valid:

            self.verify_one(
                result,
                valid,
                question
            )

        # -----------------------------------------------------
        # Source diversity
        # -----------------------------------------------------

        diversity = self.source_diversity(
            valid
        )

        for result in valid:

            result[
                "source_diversity"
            ] = diversity

        # -----------------------------------------------------
        # Sort by verification score
        # -----------------------------------------------------

        valid.sort(
            key=lambda item: float(
                item.get(
                    "verification_score",
                    0
                )
            ),
            reverse=True
        )

        return valid

    # =========================================================
    # SUMMARY
    # =========================================================

    def summary(
        self,
        results
    ):

        if not results:

            return {
                "total": 0,
                "confirmed": 0,
                "supported": 0,
                "reported": 0,
                "conflicting": 0,
                "uncertain": 0,
                "sources": 0
            }

        summary = {
            "total": len(results),
            "confirmed": 0,
            "supported": 0,
            "reported": 0,
            "conflicting": 0,
            "uncertain": 0,
            "sources": self.source_diversity(
                results
            )
        }

        for result in results:

            status = result.get(
                "status",
                "UNCERTAIN"
            )

            key = status.lower()

            if key in summary:

                summary[key] += 1

        return summary