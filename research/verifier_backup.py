import re
from difflib import SequenceMatcher


class ResearchVerifier:

    def __init__(self):

        self.stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "has",
            "have",
            "had",
            "and",
            "or",
            "of",
            "to",
            "in",
            "on",
            "for",
            "with",
            "from",
            "by",
            "as",
            "at",
            "this",
            "that",
            "today",
            "latest",
            "news"
        }


    # =================================
    # NORMALIZE TEXT
    # =================================

    def normalize(self, text):

        if text is None:
            return ""

        text = str(text).lower()

        text = re.sub(
            r"https?://\S+",
            " ",
            text
        )

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        words = text.split()

        cleaned = []

        for word in words:

            if word not in self.stop_words:

                cleaned.append(
                    word
                )

        return " ".join(
            cleaned
        )


    # =================================
    # GET TITLE
    # =================================

    def get_title(self, result):

        return str(
            result.get(
                "title",
                ""
            )
        ).strip()


    # =================================
    # GET CONTENT
    # =================================

    def get_content(self, result):

        content = str(
            result.get(
                "content",
                ""
            )
        ).strip()

        if not content:

            content = str(
                result.get(
                    "snippet",
                    ""
                )
            ).strip()

        return content


    # =================================
    # GET URL
    # =================================

    def get_url(self, result):

        return str(
            result.get(
                "url",
                ""
            )
        ).strip()


    # =================================
    # GET DOMAIN
    # =================================

    def get_domain(self, result):

        url = self.get_url(
            result
        ).lower()

        match = re.search(
            r"https?://([^/]+)",
            url
        )

        if not match:

            return ""

        domain = match.group(
            1
        )

        if domain.startswith(
            "www."
        ):

            domain = domain[4:]

        return domain


    # =================================
    # TEXT SIMILARITY
    # =================================

    def similarity(
        self,
        text1,
        text2
    ):

        first = self.normalize(
            text1
        )

        second = self.normalize(
            text2
        )

        if not first or not second:

            return 0.0

        return SequenceMatcher(
            None,
            first,
            second
        ).ratio()


    # =================================
    # SAME STORY
    # =================================

    def same_story(
        self,
        result1,
        result2
    ):

        title1 = self.get_title(
            result1
        )

        title2 = self.get_title(
            result2
        )

        similarity = self.similarity(
            title1,
            title2
        )

        if similarity >= 0.72:

            return True


        words1 = set(
            self.normalize(
                title1
            ).split()
        )

        words2 = set(
            self.normalize(
                title2
            ).split()
        )

        if not words1 or not words2:

            return False


        common = words1.intersection(
            words2
        )

        smaller = min(
            len(words1),
            len(words2)
        )

        if smaller == 0:

            return False


        overlap = (
            len(common)
            / smaller
        )

        if overlap >= 0.70:

            return True

        return False


    # =================================
    # GROUP SOURCES
    # =================================

    def group_sources(
        self,
        results
    ):

        groups = []


        for result in results:

            placed = False


            for group in groups:

                if self.same_story(
                    result,
                    group[0]
                ):

                    group.append(
                        result
                    )

                    placed = True

                    break


            if not placed:

                groups.append(
                    [result]
                )


        return groups


    # =================================
    # AGREEMENT COUNT
    # =================================

    def agreement_count(
        self,
        result,
        group
    ):

        count = 0


        for other in group:

            if other is result:

                continue


            if self.same_story(
                result,
                other
            ):

                count += 1


        return count


    # =================================
    # VERIFY RESULT
    # =================================

    def verify_result(
        self,
        result,
        group
    ):

        source_count = len(
            group
        )

        agreement = self.agreement_count(
            result,
            group
        )


        # ---------------------------------
        # STATUS
        # ---------------------------------

        if source_count >= 2:

            status = "CONFIRMED"

        else:

            status = "REPORTED"


        # ---------------------------------
        # SAVE VERIFICATION DATA
        # ---------------------------------

        result["source_count"] = (
            source_count
        )

        result["agreement_count"] = (
            agreement
        )

        result["cross_checked"] = (
            source_count >= 2
        )

        result["verification_method"] = (
            "cross_source"
        )

        result["status"] = status


        return result


    # =================================
    # VERIFY
    # =================================

    def verify(
        self,
        results
    ):

        if not results:

            return []


        groups = self.group_sources(
            results
        )


        verified = []


        for group in groups:

            for result in group:

                item = dict(
                    result
                )

                item = self.verify_result(
                    item,
                    group
                )

                verified.append(
                    item
                )


        return verified


    # =================================
    # CONFIRMED RESULTS
    # =================================

    def confirmed_results(
        self,
        results
    ):

        output = []


        for result in results:

            status = str(
                result.get(
                    "status",
                    ""
                )
            ).upper()


            if status == "CONFIRMED":

                output.append(
                    result
                )


        return output


    # =================================
    # REPORTED RESULTS
    # =================================

    def reported_results(
        self,
        results
    ):

        output = []


        for result in results:

            status = str(
                result.get(
                    "status",
                    ""
                )
            ).upper()


            if status == "REPORTED":

                output.append(
                    result
                )


        return output


    # =================================
    # UNCERTAIN RESULTS
    # =================================

    def uncertain_results(
        self,
        results
    ):

        output = []


        for result in results:

            status = str(
                result.get(
                    "status",
                    ""
                )
            ).upper()


            if status == "UNCERTAIN":

                output.append(
                    result
                )


        return output


    # =================================
    # SUMMARY
    # =================================

    def summary(
        self,
        results
    ):

        confirmed = 0

        reported = 0

        uncertain = 0


        for result in results:

            status = str(
                result.get(
                    "status",
                    "UNCERTAIN"
                )
            ).upper()


            if status == "CONFIRMED":

                confirmed += 1


            elif status == "REPORTED":

                reported += 1


            else:

                uncertain += 1


        return {
            "confirmed": confirmed,
            "reported": reported,
            "uncertain": uncertain,
            "total": len(results)
        }