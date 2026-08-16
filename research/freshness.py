from datetime import date, datetime
import re


class ResearchFreshness:

    def __init__(self):

        self.today = date(2026, 8, 15)


    def parse_date(self, value):

        if not value:
            return None

        text = str(value).strip()

        # YYYY-MM-DD
        m = re.search(
            r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b",
            text
        )

        if m:
            try:
                return date(
                    int(m.group(1)),
                    int(m.group(2)),
                    int(m.group(3))
                )
            except ValueError:
                pass


        # YYYY/MM/DD
        m = re.search(
            r"\b(20\d{2})/(\d{1,2})/(\d{1,2})\b",
            text
        )

        if m:
            try:
                return date(
                    int(m.group(1)),
                    int(m.group(2)),
                    int(m.group(3))
                )
            except ValueError:
                pass


        months = (
            "January|February|March|April|May|June|"
            "July|August|September|October|November|December"
        )


        # August 15, 2026
        m = re.search(
            r"\b("
            + months +
            r")\s+(\d{1,2}),?\s+(20\d{2})\b",
            text,
            re.IGNORECASE
        )

        if m:
            try:
                return datetime.strptime(
                    f"{m.group(1)} {m.group(2)} {m.group(3)}",
                    "%B %d %Y"
                ).date()
            except ValueError:
                pass


        # 15 August 2026
        m = re.search(
            r"\b(\d{1,2})\s+("
            + months +
            r")\s+(20\d{2})\b",
            text,
            re.IGNORECASE
        )

        if m:
            try:
                return datetime.strptime(
                    f"{m.group(1)} {m.group(2)} {m.group(3)}",
                    "%d %B %Y"
                ).date()
            except ValueError:
                pass


        return None


    def get_result_date(self, result):

        # Existing date
        value = result.get("date", "")

        parsed = self.parse_date(value)

        if parsed:
            return parsed, "date"


        # Title
        title = result.get("title", "")

        parsed = self.parse_date(title)

        if parsed:
            return parsed, "title"


        # Snippet
        snippet = result.get("snippet", "")

        parsed = self.parse_date(snippet)

        if parsed:
            return parsed, "snippet"


        # Content
        content = result.get("content", "")

        parsed = self.parse_date(
            content[:5000]
        )

        if parsed:
            return parsed, "content"


        # Explicit TODAY signal
        combined = (
            str(title) + " " +
            str(snippet)
        ).lower()

        today_words = [
            "today",
            "breaking today",
            "latest today",
            "august 15",
            "15 august",
            "aug 15"
        ]

        for word in today_words:

            if word in combined:

                return self.today, "today-signal"


        return None, "unknown"


    def days_old(self, result):

        parsed, source = (
            self.get_result_date(result)
        )

        if not parsed:
            return None

        return (
            self.today - parsed
        ).days


    def freshness_score(self, result):

        age = self.days_old(result)

        if age is None:
            return 0

        if age < 0:
            return 0

        if age == 0:
            return 5

        if age == 1:
            return 4

        if age <= 3:
            return 3

        if age <= 7:
            return 2

        if age <= 30:
            return 1

        return 0


    def enrich(self, results):

        output = []

        for result in results:

            item = dict(result)

            parsed, source = (
                self.get_result_date(item)
            )

            item["date_source"] = source

            if parsed:

                item["date"] = parsed.strftime(
                    "%Y-%m-%d"
                )

                item["days_old"] = (
                    self.today - parsed
                ).days

            else:

                item["days_old"] = None


            item["freshness_score"] = (
                self.freshness_score(item)
            )


            if item["days_old"] == 0:
                item["freshness"] = "TODAY"

            elif item["days_old"] == 1:
                item["freshness"] = "YESTERDAY"

            elif (
                item["days_old"] is not None
                and item["days_old"] <= 3
            ):
                item["freshness"] = "RECENT"

            elif item["days_old"] is None:
                item["freshness"] = "UNKNOWN"

            else:
                item["freshness"] = "OLD"


            output.append(item)

        return output


    def filter_current(self, results):

        if not results:
            return []

        enriched = self.enrich(results)

        output = []

        for item in enriched:

            freshness = item.get(
                "freshness",
                "UNKNOWN"
            )

            # Keep TODAY, RECENT and UNKNOWN.
            # OLD sources are removed.

            if freshness in [
                "TODAY",
                "YESTERDAY",
                "RECENT",
                "UNKNOWN"
            ]:
                output.append(item)

        return output


    def sort(self, results):

        return sorted(
            results,
            key=lambda x: (
                x.get(
                    "freshness_score",
                    0
                ),
                x.get(
                    "source_count",
                    1
                )
            ),
            reverse=True
        )


    def process(self, results):

        results = self.enrich(results)

        results = self.filter_current(
            results
        )

        results = self.sort(
            results
        )

        return results