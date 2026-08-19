from urllib.parse import urlparse


class ResearchRanker:
    """
    AKHIM AI Research Ranking Engine

    Ranks research sources using:

        - Verification status
        - Domain trust
        - Verification score
        - Cross-source agreement
        - Freshness
        - Relevance
        - Content quality
        - URL quality
        - Source diversity
        - Duplicate detection
        - Conflict detection
        - Evidence completeness

    Output:
        rank_score
        rank_confidence
        rank_reason
        source_number
    """

    VERSION = "3.0"

    # =========================================================
    # SCORE WEIGHTS
    # =========================================================

    WEIGHTS = {
        "status": 0.20,
        "trust": 0.18,
        "verification": 0.16,
        "agreement": 0.12,
        "relevance": 0.14,
        "freshness": 0.07,
        "content": 0.06,
        "url_quality": 0.03,
        "quality_bonus": 0.04
    }

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(
        self,
        default_max_results=7,
        min_score=0,
        diversify_sources=True
    ):

        self.default_max_results = max(
            1,
            int(default_max_results)
        )

        self.min_score = max(
            0,
            float(min_score)
        )

        self.diversify_sources = bool(
            diversify_sources
        )

    # =========================================================
    # NUMBER
    # =========================================================

    def number(
        self,
        value,
        default=0.0
    ):

        try:

            if value is None:
                return float(default)

            if isinstance(
                value,
                bool
            ):

                return float(
                    int(value)
                )

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return float(default)

    # =========================================================
    # NORMALIZE
    # =========================================================

    def normalize(
        self,
        value
    ):

        return self.number(
            value,
            0
        )

    # =========================================================
    # STATUS
    # =========================================================

    def get_status(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return "UNCERTAIN"

        return str(
            result.get(
                "status",
                "UNCERTAIN"
            )
        ).strip().upper()

    # =========================================================
    # STATUS SCORE
    # =========================================================

    def status_score(
        self,
        result
    ):

        status = self.get_status(
            result
        )

        values = {
            "CONFIRMED": 100,
            "SUPPORTED": 88,
            "REPORTED": 65,
            "CONFLICTING": 40,
            "UNCERTAIN": 25
        }

        return values.get(
            status,
            25
        )

    # =========================================================
    # TRUST SCORE
    # =========================================================

    def trust_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "trust_score",
                0
            )
        )

        # Verifier normally uses 0-40.
        return min(
            100,
            max(
                0,
                (value / 40.0) * 100
            )
        )

    # =========================================================
    # VERIFICATION SCORE
    # =========================================================

    def verification_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "verification_score",
                0
            )
        )

        # Verifier final score is capped around 100.
        return min(
            100,
            max(
                0,
                value
            )
        )

    # =========================================================
    # AGREEMENT SCORE
    # =========================================================

    def agreement_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "agreement_score",
                0
            )
        )

        # ResearchVerifier maximum agreement is 25.
        return min(
            100,
            max(
                0,
                (value / 25.0) * 100
            )
        )

    # =========================================================
    # RELEVANCE SCORE
    # =========================================================

    def relevance_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "relevance_score",
                0
            )
        )

        # ResearchVerifier maximum relevance = 20.
        return min(
            100,
            max(
                0,
                (value / 20.0) * 100
            )
        )

    # =========================================================
    # FRESHNESS SCORE
    # =========================================================

    def freshness_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "freshness_score",
                0
            )
        )

        # ResearchFreshness maximum = 10.
        return min(
            100,
            max(
                0,
                (value / 10.0) * 100
            )
        )

    # =========================================================
    # CONTENT QUALITY
    # =========================================================

    def content_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "content_quality_score",
                result.get(
                    "content_score",
                    0
                )
            )
        )

        # ResearchVerifier maximum content = 20.
        return min(
            100,
            max(
                0,
                (value / 20.0) * 100
            )
        )

    # =========================================================
    # URL QUALITY
    # =========================================================

    def url_quality_score(
        self,
        result
    ):

        value = self.number(
            result.get(
                "url_quality_score",
                0
            )
        )

        # Maximum = 10.
        return min(
            100,
            max(
                0,
                (value / 10.0) * 100
            )
        )

    # =========================================================
    # QUALITY BONUS
    # =========================================================

    def quality_bonus(
        self,
        result
    ):

        value = self.number(
            result.get(
                "quality_bonus",
                0
            )
        )

        # Maximum = 10.
        return min(
            100,
            max(
                0,
                (value / 10.0) * 100
            )
        )

    # =========================================================
    # DOMAIN
    # =========================================================

    def get_domain(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):
            return ""

        domain = str(
            result.get(
                "domain",
                ""
            )
        ).strip().lower()

        if domain:
            return domain

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

            domain = parsed.netloc.lower()

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
# =========================================================
    # SOURCE TYPE
    # =========================================================

    def get_source_type(
        self,
        result
    ):

        return str(
            result.get(
                "source_type",
                "UNKNOWN"
            )
        ).upper()

    # =========================================================
    # DUPLICATE PENALTY
    # =========================================================

    def duplicate_penalty(
        self,
        result
    ):

        duplicate = result.get(
            "duplicate_source",
            False
        )

        if duplicate:
            return 20

        return 0

    # =========================================================
    # CONFLICT PENALTY
    # =========================================================

    def conflict_penalty(
        self,
        result
    ):

        conflicts = result.get(
            "conflicting_sources",
            []
        )

        if not isinstance(
            conflicts,
            (list, tuple, set)
        ):

            return 0

        count = len(
            conflicts
        )

        if count <= 0:
            return 0

        return min(
            25,
            count * 7
        )

    # =========================================================
    # MISSING DATA PENALTY
    # =========================================================

    def missing_data_penalty(
        self,
        result
    ):

        penalty = 0

        title = str(
            result.get(
                "title",
                ""
            )
        ).strip()

        url = str(
            result.get(
                "url",
                ""
            )
        ).strip()

        snippet = str(
            result.get(
                "snippet",
                ""
            )
        ).strip()

        content = str(
            result.get(
                "content",
                ""
            )
        ).strip()

        if not title:
            penalty += 4

        if not url:
            penalty += 6

        if not snippet and not content:
            penalty += 6

        return min(
            15,
            penalty
        )
# =========================================================
    # SOURCE QUALITY
    # =========================================================

    def source_quality(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return 0.0

        status = (
            self.status_score(
                result
            )
        )

        trust = (
            self.trust_score(
                result
            )
        )

        verification = (
            self.verification_score(
                result
            )
        )

        agreement = (
            self.agreement_score(
                result
            )
        )

        relevance = (
            self.relevance_score(
                result
            )
        )

        freshness = (
            self.freshness_score(
                result
            )
        )

        content = (
            self.content_score(
                result
            )
        )

        url_quality = (
            self.url_quality_score(
                result
            )
        )

        quality_bonus = (
            self.quality_bonus(
                result
            )
        )

        score = (
            status
            * self.WEIGHTS["status"]
            +
            trust
            * self.WEIGHTS["trust"]
            +
            verification
            * self.WEIGHTS["verification"]
            +
            agreement
            * self.WEIGHTS["agreement"]
            +
            relevance
            * self.WEIGHTS["relevance"]
            +
            freshness
            * self.WEIGHTS["freshness"]
            +
            content
            * self.WEIGHTS["content"]
            +
            url_quality
            * self.WEIGHTS["url_quality"]
            +
            quality_bonus
            * self.WEIGHTS["quality_bonus"]
        )

        # -----------------------------------------------------
        # Penalties
        # -----------------------------------------------------

        score -= self.duplicate_penalty(
            result
        )

        score -= self.conflict_penalty(
            result
        )

        score -= self.missing_data_penalty(
            result
        )

        # -----------------------------------------------------
        # Status safety rules
        # -----------------------------------------------------

        if status == "UNCERTAIN":

            score = min(
                score,
                55
            )

        elif status == "CONFLICTING":

            score = min(
                score,
                65
            )

        score = max(
            0,
            min(
                100,
                score
            )
        )

        return round(
            score,
            2
        )

    # =========================================================
    # CONFIDENCE
    # =========================================================

    def rank_confidence(
        self,
        score
    ):

        score = self.number(
            score
        )

        if score >= 85:
            return "VERY_HIGH"

        if score >= 70:
            return "HIGH"

        if score >= 55:
            return "MEDIUM"

        if score >= 35:
            return "LOW"

        return "VERY_LOW"

    # =========================================================
    # RANK REASON
    # =========================================================

    def rank_reason(
        self,
        result
    ):

        reasons = []

        status = self.get_status(
            result
        )

        source_type = self.get_source_type(
            result
        )

        trust = self.number(
            result.get(
                "trust_score",
                0
            )
        )

        agreement = self.number(
            result.get(
                "agreement_score",
                0
            )
        )

        freshness = self.number(
            result.get(
                "freshness_score",
                0
            )
        )

        relevance = self.number(
            result.get(
                "relevance_score",
                0
            )
        )

        if status == "CONFIRMED":

            reasons.append(
                "independently supported"
            )

        elif status == "SUPPORTED":

            reasons.append(
                "well supported"
            )

        elif status == "REPORTED":

            reasons.append(
                "reported evidence"
            )

        elif status == "CONFLICTING":

            reasons.append(
                "conflicting evidence"
            )

        else:

            reasons.append(
                "uncertain evidence"
            )

        if trust >= 30:

            reasons.append(
                "high-trust source"
            )

        if source_type in (
            "GOVERNMENT",
            "ACADEMIC"
        ):

            reasons.append(
                source_type.lower()
            )

        if agreement >= 10:

            reasons.append(
                "strong cross-source agreement"
            )

        elif agreement >= 5:

            reasons.append(
                "some source agreement"
            )

        if relevance >= 12:

            reasons.append(
                "high relevance"
            )

        if freshness >= 7:

            reasons.append(
                "fresh evidence"
            )

        if result.get(
            "duplicate_source",
            False
        ):

            reasons.append(
                "duplicate evidence penalty"
            )

        if result.get(
            "conflicting_sources"
        ):

            reasons.append(
                "conflict penalty"
            )

        return "; ".join(
            reasons
        )
# =========================================================
    # RANK ONE
    # =========================================================

    def rank_one(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return result

        score = self.source_quality(
            result
        )

        result["rank_score"] = (
            round(
                score,
                2
            )
        )

        result["rank_confidence"] = (
            self.rank_confidence(
                score
            )
        )

        result["rank_reason"] = (
            self.rank_reason(
                result
            )
        )

        result["rank_domain"] = (
            self.get_domain(
                result
            )
        )

        result["rank_source_type"] = (
            self.get_source_type(
                result
            )
        )

        return result

    # =========================================================
    # SOURCE DIVERSITY
    # =========================================================

    def diversify(
        self,
        results,
        max_results
    ):

        if not results:
            return []

        selected = []
        used_domains = set()

        # -----------------------------------------------------
        # First pass:
        # Prefer different domains.
        # -----------------------------------------------------

        for result in results:

            domain = self.get_domain(
                result
            )

            if (
                domain
                and domain in used_domains
            ):
                continue

            selected.append(
                result
            )

            if domain:
                used_domains.add(
                    domain
                )

            if len(selected) >= max_results:
                break

        # -----------------------------------------------------
        # Second pass:
        # Fill remaining slots.
        # -----------------------------------------------------

        if len(selected) < max_results:

            selected_ids = {
                id(item)
                for item in selected
            }

            for result in results:

                if id(result) in selected_ids:
                    continue

                selected.append(
                    result
                )

                if len(selected) >= max_results:
                    break

        return selected

    # =========================================================
    # RANK ALL
    # =========================================================

    def rank(
        self,
        results,
        max_results=None
    ):

        if not results:
            return []

        if max_results is None:

            max_results = (
                self.default_max_results
            )

        try:

            max_results = int(
                max_results
            )

        except (
            TypeError,
            ValueError
        ):

            max_results = (
                self.default_max_results
            )

        max_results = max(
            1,
            max_results
        )

        valid = []

        for result in results:

            if not isinstance(
                result,
                dict
            ):
                continue

            self.rank_one(
                result
            )

            score = self.number(
                result.get(
                    "rank_score",
                    0
                )
            )

            if score < self.min_score:
                continue

            valid.append(
                result
            )

        if not valid:
            return []

        # -----------------------------------------------------
        # Sort
        # -----------------------------------------------------

        valid.sort(
            key=lambda item: (
                self.number(
                    item.get(
                        "rank_score",
                        0
                    )
                ),
                self.number(
                    item.get(
                        "verification_score",
                        0
                    )
                ),
                self.number(
                    item.get(
                        "relevance_score",
                        0
                    )
                ),
                self.number(
                    item.get(
                        "freshness_score",
                        0
                    )
                )
            ),
            reverse=True
        )

        # -----------------------------------------------------
        # Diversity
        # -----------------------------------------------------

        if self.diversify_sources:

            selected = self.diversify(
                valid,
                max_results
            )

        else:

            selected = valid[
                :max_results
            ]

        # -----------------------------------------------------
        # Number selected sources
        # -----------------------------------------------------

        for index, result in enumerate(
            selected,
            start=1
        ):

            result[
                "source_number"
            ] = index

        return selected

    # =========================================================
    # PROCESS
    # =========================================================

    def process(
        self,
        results,
        max_results=None
    ):

        return self.rank(
            results,
            max_results
        )

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
                "very_high": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "very_low": 0,
                "domains": 0
            }

        summary = {
            "total": len(results),
            "very_high": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "very_low": 0,
            "domains": 0
        }

        domains = set()

        for result in results:

            confidence = str(
                result.get(
                    "rank_confidence",
                    "VERY_LOW"
                )
            ).lower()

            if confidence in summary:

                summary[
                    confidence
                ] += 1

            domain = self.get_domain(
                result
            )

            if domain:
                domains.add(
                    domain
                )

        summary["domains"] = len(
            domains
        )

        return summary