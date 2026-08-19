from datetime import date, datetime, timezone, timedelta
import re


class ResearchFreshness:
    """
    AKHIM AI Research Freshness Engine

    Features:
        - Dynamic current date
        - Multiple date formats
        - Published / updated date support
        - Relative date detection
        - Year-only date detection
        - Future-date protection
        - Freshness confidence
        - Configurable freshness windows
        - Current/recent filtering
        - Freshness-aware sorting
        - Source-aware freshness hints
        - Safe handling of malformed results
        - Preserves original result data
    """

    VERSION = "3.0"

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(
        self,
        today=None,
        recent_days=7,
        current_days=30,
        old_days=365
    ):
        """
        today:
            Optional fixed date for testing.

        recent_days:
            Number of days considered RECENT.

        current_days:
            Number of days accepted by filter_current().

        old_days:
            Beyond this the source is considered OLD.
        """

        self.today = (
            today
            if isinstance(today, date)
            else date.today()
        )

        self.recent_days = max(
            1,
            int(recent_days)
        )

        self.current_days = max(
            self.recent_days,
            int(current_days)
        )

        self.old_days = max(
            self.current_days,
            int(old_days)
        )

    # =========================================================
    # SAFE TEXT
    # =========================================================

    def safe_text(self, value):

        if value is None:
            return ""

        try:
            return str(value).strip()
        except Exception:
            return ""

    # =========================================================
    # DATE VALIDATION
    # =========================================================

    def valid_date(
        self,
        year,
        month,
        day
    ):

        try:

            return date(
                int(year),
                int(month),
                int(day)
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    # =========================================================
    # PARSE DATE
    # =========================================================

    def parse_date(self, value):

        if not value:
            return None

        text = self.safe_text(
            value
        )

        if not text:
            return None

        # -----------------------------------------------------
        # YYYY-MM-DD
        # -----------------------------------------------------

        match = re.search(
            r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b",
            text
        )

        if match:

            parsed = self.valid_date(
                match.group(1),
                match.group(2),
                match.group(3)
            )

            if parsed:
                return parsed

        # -----------------------------------------------------
        # YYYY/MM/DD
        # -----------------------------------------------------

        match = re.search(
            r"\b(20\d{2})/(\d{1,2})/(\d{1,2})\b",
            text
        )

        if match:

            parsed = self.valid_date(
                match.group(1),
                match.group(2),
                match.group(3)
            )

            if parsed:
                return parsed

        # -----------------------------------------------------
        # YYYY.MM.DD
        # -----------------------------------------------------

        match = re.search(
            r"\b(20\d{2})\.(\d{1,2})\.(\d{1,2})\b",
            text
        )

        if match:

            parsed = self.valid_date(
                match.group(1),
                match.group(2),
                match.group(3)
            )

            if parsed:
                return parsed

        # -----------------------------------------------------
        # DD-MM-YYYY
        # -----------------------------------------------------

        match = re.search(
            r"\b(\d{1,2})-(\d{1,2})-(20\d{2})\b",
            text
        )

        if match:

            parsed = self.valid_date(
                match.group(3),
                match.group(2),
                match.group(1)
            )

            if parsed:
                return parsed

        # -----------------------------------------------------
        # DD/MM/YYYY
        # -----------------------------------------------------

        match = re.search(
            r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b",
            text
        )

        if match:

            parsed = self.valid_date(
                match.group(3),
                match.group(2),
                match.group(1)
            )

            if parsed:
                return parsed

        # -----------------------------------------------------
        # Month DD, YYYY
        # Example:
        # August 19, 2026
        # Aug 19, 2026
        # -----------------------------------------------------

        months = (
            "January|February|March|April|May|June|"
            "July|August|September|October|November|December"
        )

        short_months = (
            "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|"
            "Sep|Sept|Oct|Nov|Dec"
        )

        month_pattern = (
            months
            + "|"
            + short_months
        )

        match = re.search(
            r"\b("
            + month_pattern
            + r")\s+(\d{1,2}),?\s+(20\d{2})\b",
            text,
            re.IGNORECASE
        )

        if match:

            month_text = match.group(1)
            day_text = match.group(2)
            year_text = match.group(3)

            for fmt in (
                "%B %d %Y",
                "%b %d %Y"
            ):

                try:

                    return datetime.strptime(
                        f"{month_text} "
                        f"{day_text} "
                        f"{year_text}",
                        fmt
                    ).date()

                except ValueError:
                    continue

        # -----------------------------------------------------
        # DD Month YYYY
        # -----------------------------------------------------

        match = re.search(
            r"\b(\d{1,2})\s+("
            + month_pattern
            + r")\s+(20\d{2})\b",
            text,
            re.IGNORECASE
        )

        if match:

            day_text = match.group(1)
            month_text = match.group(2)
            year_text = match.group(3)

            for fmt in (
                "%d %B %Y",
                "%d %b %Y"
            ):

                try:

                    return datetime.strptime(
                        f"{day_text} "
                        f"{month_text} "
                        f"{year_text}",
                        fmt
                    ).date()

                except ValueError:
                    continue

        # -----------------------------------------------------
        # ISO datetime
        # Example:
        # 2026-08-19T14:30:00
        # -----------------------------------------------------

        iso_match = re.search(
            r"\b20\d{2}-\d{2}-\d{2}"
            r"(?:[T\s]\d{2}:\d{2}"
            r"(?::\d{2})?"
            r"(?:Z|[+-]\d{2}:?\d{2})?)?\b",
            text
        )

        if iso_match:

            iso_text = iso_match.group(0)

            try:

                return datetime.fromisoformat(
                    iso_text.replace(
                        "Z",
                        "+00:00"
                    )
                ).date()

            except ValueError:
                pass

        # -----------------------------------------------------
        # Year-only
        # -----------------------------------------------------

        match = re.search(
            r"\b(20\d{2})\b",
            text
        )

        if match:

            try:

                return date(
                    int(match.group(1)),
                    1,
                    1
                )

            except ValueError:
                pass

        return None

    # =========================================================
    # RELATIVE DATE
    # =========================================================

    def parse_relative_date(
        self,
        value
    ):

        text = self.safe_text(
            value
        ).lower()

        if not text:
            return None, None

        # -----------------------------------------------------
        # Today
        # -----------------------------------------------------

        if re.search(
            r"\b(today|just now)\b",
            text
        ):

            return self.today, "today"

        # -----------------------------------------------------
        # Yesterday
        # -----------------------------------------------------

        if re.search(
            r"\byesterday\b",
            text
        ):

            return (
                self.today - timedelta(days=1),
                "yesterday"
            )

        # -----------------------------------------------------
        # N days ago
        # -----------------------------------------------------

        match = re.search(
            r"\b(\d+)\s+days?\s+ago\b",
            text
        )

        if match:

            days = int(
                match.group(1)
            )

            return (
                self.today
                - timedelta(days=days),
                "relative-days"
            )

        # -----------------------------------------------------
        # N weeks ago
        # -----------------------------------------------------

        match = re.search(
            r"\b(\d+)\s+weeks?\s+ago\b",
            text
        )

        if match:

            weeks = int(
                match.group(1)
            )

            return (
                self.today
                - timedelta(
                    days=weeks * 7
                ),
                "relative-weeks"
            )

        # -----------------------------------------------------
        # N months ago
        # Approximate 30 days.
        # -----------------------------------------------------

        match = re.search(
            r"\b(\d+)\s+months?\s+ago\b",
            text
        )

        if match:

            months = int(
                match.group(1)
            )

            return (
                self.today
                - timedelta(
                    days=months * 30
                ),
                "relative-months"
            )

        return None, None

    # =========================================================
    # RESULT DATE
    # =========================================================

    def get_result_date(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return None, "invalid"

        # -----------------------------------------------------
        # Highest priority: explicit structured dates
        # -----------------------------------------------------

        date_fields = (
            "updated",
            "updated_at",
            "modified",
            "modified_at",
            "published",
            "published_at",
            "date",
            "created_at"
        )

        for field in date_fields:

            value = result.get(
                field
            )

            if not value:
                continue

            parsed = self.parse_date(
                value
            )

            if parsed:

                return (
                    parsed,
                    field
                )

            relative, source = (
                self.parse_relative_date(
                    value
                )
            )

            if relative:

                return (
                    relative,
                    field + ":" + source
                )

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        title = self.safe_text(
            result.get("title")
        )

        parsed = self.parse_date(
            title
        )

        if parsed:

            return (
                parsed,
                "title"
            )

        relative, source = (
            self.parse_relative_date(
                title
            )
        )

        if relative:

            return (
                relative,
                "title:" + source
            )

        # -----------------------------------------------------
        # Snippet
        # -----------------------------------------------------

        snippet = self.safe_text(
            result.get("snippet")
        )

        parsed = self.parse_date(
            snippet
        )

        if parsed:

            return (
                parsed,
                "snippet"
            )

        relative, source = (
            self.parse_relative_date(
                snippet
            )
        )

        if relative:

            return (
                relative,
                "snippet:" + source
            )

        # -----------------------------------------------------
        # Content
        # -----------------------------------------------------

        content = self.safe_text(
            result.get("content")
        )

        if content:

            parsed = self.parse_date(
                content[:5000]
            )

            if parsed:

                return (
                    parsed,
                    "content"
                )

        # -----------------------------------------------------
        # Combined signal
        # -----------------------------------------------------

        combined = (
            title
            + " "
            + snippet
        )

        relative, source = (
            self.parse_relative_date(
                combined
            )
        )

        if relative:

            return (
                relative,
                "text:" + source
            )

        return None, "unknown"

    # =========================================================
    # AGE
    # =========================================================

    def days_old(
        self,
        result
    ):

        parsed, source = (
            self.get_result_date(
                result
            )
        )

        if not parsed:
            return None

        age = (
            self.today - parsed
        ).days

        # Future dates are not negative age.
        if age < 0:
            return None

        return age

    # =========================================================
    # FRESHNESS CATEGORY
    # =========================================================

    def freshness_label(
        self,
        age
    ):

        if age is None:
            return "UNKNOWN"

        if age == 0:
            return "TODAY"

        if age == 1:
            return "YESTERDAY"

        if age <= 3:
            return "VERY_RECENT"

        if age <= self.recent_days:
            return "RECENT"

        if age <= self.current_days:
            return "CURRENT"

        if age <= self.old_days:
            return "AGING"

        return "OLD"

    # =========================================================
    # FRESHNESS SCORE
    # =========================================================

    def freshness_score(
        self,
        result
    ):

        age = self.days_old(
            result
        )

        if age is None:
            return 0

        if age == 0:
            return 10

        if age == 1:
            return 9

        if age <= 3:
            return 8

        if age <= 7:
            return 7

        if age <= 14:
            return 6

        if age <= 30:
            return 5

        if age <= 90:
            return 3

        if age <= 180:
            return 2

        if age <= 365:
            return 1

        return 0

    # =========================================================
    # DATE CONFIDENCE
    # =========================================================

    def date_confidence(
        self,
        source
    ):

        if not source:
            return 0

        source = str(
            source
        ).lower()

        if source in {
            "updated",
            "updated_at",
            "published",
            "published_at",
            "date",
            "created_at",
            "modified",
            "modified_at"
        }:

            return 1.0

        if "relative" in source:
            return 0.95

        if source == "today-signal":
            return 0.85

        if source in {
            "title",
            "snippet"
        }:

            return 0.70

        if source == "content":
            return 0.60

        if source == "unknown":
            return 0.0

        return 0.50

    # =========================================================
    # FUTURE DATE CHECK
    # =========================================================

    def is_future(
        self,
        result
    ):

        parsed, source = (
            self.get_result_date(
                result
            )
        )

        if not parsed:
            return False

        return parsed > self.today

    # =========================================================
    # ENRICH ONE
    # =========================================================

    def enrich_one(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):
            return None

        item = dict(
            result
        )

        parsed, source = (
            self.get_result_date(
                item
            )
        )

        item["date_source"] = source

        if parsed:

            item["detected_date"] = (
                parsed.strftime(
                    "%Y-%m-%d"
                )
            )

            age = (
                self.today - parsed
            ).days

            # Future date protection
            if age < 0:

                item["days_old"] = None
                item["freshness"] = "FUTURE"
                item["freshness_score"] = 0
                item["freshness_confidence"] = 0.0

                return item

            item["days_old"] = age

            item["freshness"] = (
                self.freshness_label(
                    age
                )
            )

            item["freshness_score"] = (
                self.freshness_score(
                    item
                )
            )

            item["freshness_confidence"] = (
                self.date_confidence(
                    source
                )
            )

            # Keep normalized date separately.
            # Do not overwrite original date field.
            if not item.get("date"):

                item["date"] = (
                    parsed.strftime(
                        "%Y-%m-%d"
                    )
                )

        else:

            item["detected_date"] = None
            item["days_old"] = None
            item["freshness"] = "UNKNOWN"
            item["freshness_score"] = 0
            item["freshness_confidence"] = 0.0

        return item

  # =========================================================
    # ENRICH ALL
    # =========================================================

    def enrich(
        self,
        results
    ):

        if not results:
            return []

        output = []

        for result in results:

            item = self.enrich_one(
                result
            )

            if item is not None:

                output.append(
                    item
                )

        return output

    # =========================================================
    # CURRENT FILTER
    # =========================================================

    def filter_current(
        self,
        results,
        include_unknown=True
    ):

        if not results:
            return []

        enriched = self.enrich(
            results
        )

        output = []

        for item in enriched:

            freshness = item.get(
                "freshness",
                "UNKNOWN"
            )

            if freshness == "FUTURE":
                continue

            if freshness == "UNKNOWN":

                if include_unknown:
                    output.append(
                        item
                    )

                continue

            age = item.get(
                "days_old"
            )

            if (
                age is not None
                and age <= self.current_days
            ):

                output.append(
                    item
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
                item.get(
                    "freshness_score",
                    0
                ),
                item.get(
                    "freshness_confidence",
                    0
                ),
                -(
                    item.get(
                        "days_old"
                    )
                    if item.get(
                        "days_old"
                    ) is not None
                    else 999999
                ),
                item.get(
                    "source_count",
                    1
                )
            ),
            reverse=True
        )

    # =========================================================
    # REMOVE FUTURE RESULTS
    # =========================================================

    def remove_future(
        self,
        results
    ):

        if not results:
            return []

        return [
            item
            for item in results
            if item.get(
                "freshness"
            ) != "FUTURE"
        ]

    # =========================================================
    # PROCESS
    # =========================================================

    def process(
        self,
        results,
        current_only=False,
        include_unknown=True
    ):

        if not results:
            return []

        results = self.enrich(
            results
        )

        results = self.remove_future(
            results
        )

        if current_only:

            results = self.filter_current(
                results,
                include_unknown=include_unknown
            )

        results = self.sort(
            results
        )

        return results

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
                "today": 0,
                "yesterday": 0,
                "very_recent": 0,
                "recent": 0,
                "current": 0,
                "aging": 0,
                "old": 0,
                "unknown": 0,
                "future": 0
            }

        summary = {
            "total": len(results),
            "today": 0,
            "yesterday": 0,
            "very_recent": 0,
            "recent": 0,
            "current": 0,
            "aging": 0,
            "old": 0,
            "unknown": 0,
            "future": 0
        }

        for item in results:

            label = str(
                item.get(
                    "freshness",
                    "UNKNOWN"
                )
            ).lower()

            if label in summary:

                summary[label] += 1

        return summary