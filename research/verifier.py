import re
from urllib.parse import urlparse


class ResearchVerifier:

    def __init__(self):

        # =================================
        # HIGH TRUST DOMAINS
        # =================================

        self.high_trust_domains = {

            # Government
            "gov.in",
            "nic.in",
            "india.gov.in",
            "pib.gov.in",
            "presidentofindia.nic.in",
            "rashtrapatibhavan.gov.in",

            # International organizations
            "who.int",
            "un.org",
            "worldbank.org",
            "imf.org",
            "nasa.gov",

            # Major institutions
            "nature.com",
            "science.org",
            "nih.gov",
            "nibib.nih.gov",

            # Major technology companies
            "openai.com",
            "google.com",
            "deepmind.google",
            "microsoft.com",
            "nvidia.com",
            "aws.amazon.com",
            "amazon.com",
            "anthropic.com",
            "deepseek.com",
            "meta.com",
            "apple.com",

            # Major news / reference
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "bbc.co.uk",
            "nytimes.com",
            "theguardian.com",
            "techcrunch.com"
        }


        # =================================
        # WEAK DOMAINS
        # =================================

        self.weak_domains = {

            "blogspot.com",
            "wordpress.com",
            "medium.com",
            "facebook.com",
            "instagram.com",
            "x.com",
            "twitter.com",
            "pinterest.com"
        }


    # =================================
    # DOMAIN
    # =================================

    def get_domain(self, result):

        url = str(
            result.get(
                "url",
                ""
            )
        ).strip()


        if not url:

            return ""


        try:

            domain = urlparse(
                url
            ).netloc.lower()


            if domain.startswith(
                "www."
            ):

                domain = domain[4:]


            return domain


        except Exception:

            return ""


    # =================================
    # DOMAIN MATCH
    # =================================

    def domain_matches(
        self,
        domain,
        trusted_domain
    ):

        if not domain:

            return False


        if domain == trusted_domain:

            return True


        return domain.endswith(
            "." + trusted_domain
        )


    # =================================
    # TRUST SCORE
    # =================================

    def trust_score(self, result):

        domain = self.get_domain(
            result
        )


        if not domain:

            return 0


        # Government / official
        for trusted in self.high_trust_domains:

            if self.domain_matches(
                domain,
                trusted
            ):

                # Government sources get highest priority

                if (
                    domain.endswith(
                        ".gov.in"
                    )
                    or domain == "gov.in"
                ):

                    return 50


                if domain.endswith(
                    ".nic.in"
                ):

                    return 50


                return 40


        # Weak sources
        for weak in self.weak_domains:

            if self.domain_matches(
                domain,
                weak
            ):

                return 5


        # Normal source

        return 15


    # =================================
    # NORMALIZE
    # =================================

    def normalize(self, text):

        if text is None:

            return ""


        text = str(
            text
        ).lower()


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


        text = re.sub(
            r"\s+",
            " ",
            text
        )


        return text.strip()


    # =================================
    # WORD SET
    # =================================

    def word_set(self, text):

        text = self.normalize(
            text
        )


        if not text:

            return set()


        return set(
            text.split()
        )


    # =================================
    # SIMILARITY
    # =================================

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
            words1
            & words2
        )


        union = (
            words1
            | words2
        )


        if not union:

            return 0.0


        return (
            len(intersection)
            / len(union)
        )


    # =================================
    # RESULT TEXT
    # =================================

    def get_text(self, result):

        parts = []


        for key in [

            "title",
            "content",
            "snippet",
            "description",
            "summary"

        ]:

            value = result.get(
                key,
                ""
            )


            if value:

                parts.append(
                    str(value)
                )


        return " ".join(
            parts
        )


    # =================================
    # CONTENT QUALITY
    # =================================

    def content_quality(
        self,
        result
    ):

        score = 0


        title = str(
            result.get(
                "title",
                ""
            )
        ).strip()


        content = str(
            result.get(
                "content",
                ""
            )
        ).strip()


        snippet = str(
            result.get(
                "snippet",
                ""
            )
        ).strip()


        if title:

            score += 10


        if len(content) >= 500:

            score += 20

        elif len(content) >= 200:

            score += 15

        elif content:

            score += 8

        elif snippet:

            score += 5


        return score


    # =================================
    # CROSS SOURCE AGREEMENT
    # =================================

    def agreement_score(
        self,
        result,
        results
    ):

        current = self.get_text(
            result
        )


        if not current:

            return 0


        score = 0


        current_domain = self.get_domain(
            result
        )


        for other in results:

            if other is result:

                continue


            other_domain = self.get_domain(
                other
            )


            # Avoid counting same website repeatedly

            if (
                current_domain
                and other_domain
                and current_domain == other_domain
            ):

                continue


            other_text = self.get_text(
                other
            )


            similarity = self.similarity(
                current,
                other_text
            )


            if similarity >= 0.45:

                score += 25

            elif similarity >= 0.30:

                score += 15

            elif similarity >= 0.20:

                score += 8


        if score > 50:

            score = 50


        return score


    # =================================
    # VERIFY ONE RESULT
    # =================================

    def verify_one(
        self,
        result,
        results
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


        agreement = self.agreement_score(
            result,
            results
        )


        total = (
            trust
            + content
            + agreement
        )


        result[
            "trust_score"
        ] = trust


        result[
            "agreement_score"
        ] = agreement


        result[
            "verification_score"
        ] = total


        # =================================
        # STATUS
        # =================================

        # Very strong official source
        if trust >= 40:

            result[
                "status"
            ] = "CONFIRMED"


        # Multiple independent sources agree
        elif agreement >= 25:

            result[
                "status"
            ] = "CONFIRMED"


        # Good source with useful content
        elif (
            trust >= 15
            and content >= 15
        ):

            result[
                "status"
            ] = "REPORTED"


        # Some evidence
        elif content >= 8:

            result[
                "status"
            ] = "REPORTED"


        else:

            result[
                "status"
            ] = "UNCERTAIN"


        return result


    # =================================
    # VERIFY ALL
    # =================================

    def verify(self, results):

        if not results:

            return []


        valid = []


        for result in results:

            if not isinstance(
                result,
                dict
            ):

                continue


            valid.append(
                result
            )


        if not valid:

            return []


        # First pass
        for result in valid:

            self.verify_one(
                result,
                valid
            )


        # =================================
        # SECOND PASS
        # =================================

        # Recalculate agreement after
        # all results have metadata

        for result in valid:

            result[
                "agreement_score"
            ] = self.agreement_score(
                result,
                valid
            )


        # =================================
        # REBUILD STATUS
        # =================================

        for result in valid:

            trust = float(
                result.get(
                    "trust_score",
                    0
                )
            )


            agreement = float(
                result.get(
                    "agreement_score",
                    0
                )
            )


            content = self.content_quality(
                result
            )


            result[
                "verification_score"
            ] = (
                trust
                + agreement
                + content
            )


            if trust >= 40:

                result[
                    "status"
                ] = "CONFIRMED"


            elif agreement >= 25:

                result[
                    "status"
                ] = "CONFIRMED"


            elif (
                trust >= 15
                and content >= 15
            ):

                result[
                    "status"
                ] = "REPORTED"


            elif content >= 8:

                result[
                    "status"
                ] = "REPORTED"


            else:

                result[
                    "status"
                ] = "UNCERTAIN"


        return valid


    # =================================
    # COUNTS
    # =================================

    def counts(self, results):

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

            "confirmed":
                confirmed,

            "reported":
                reported,

            "uncertain":
                uncertain
        }


    # =================================
    # SUPPORTED RESULTS
    # =================================

    def verified_results(
        self,
        results
    ):

        if not results:

            return []


        output = []


        for result in results:

            status = str(
                result.get(
                    "status",
                    "UNCERTAIN"
                )
            ).upper()


            if status in [
                "CONFIRMED",
                "REPORTED"
            ]:

                output.append(
                    result
                )


        return output