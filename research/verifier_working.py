from urllib.parse import urlparse


class ResearchVerifier:

    def __init__(self):
        pass

    # =================================
    # NORMALIZE
    # =================================

    def normalize(self, value):

        if value is None:
            return ""

        return " ".join(
            str(value)
            .strip()
            .lower()
            .split()
        )


    # =================================
    # URL
    # =================================

    def get_url(self, result):

        return str(
            result.get(
                "url",
                ""
            )
        ).strip()


    # =================================
    # TITLE
    # =================================

    def get_title(self, result):

        return str(
            result.get(
                "title",
                ""
            )
        ).strip()


    # =================================
    # CONTENT
    # =================================

    def get_content(self, result):

        content = result.get(
            "content",
            ""
        )

        if not content:

            content = result.get(
                "text",
                ""
            )

        if not content:

            content = result.get(
                "description",
                ""
            )

        return str(
            content or ""
        ).strip()


    # =================================
    # DOMAIN
    # =================================

    def get_domain(self, result):

        url = self.get_url(
            result
        )

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            domain = (
                parsed.netloc
                or parsed.path
            )

            domain = domain.lower()

            if domain.startswith(
                "www."
            ):

                domain = domain[4:]

            return domain

        except Exception:

            return ""


    # =================================
    # OFFICIAL / TRUSTED DOMAINS
    # =================================

    def is_trusted_domain(
        self,
        domain
    ):

        if not domain:
            return False

        trusted_domains = [

            # India Government
            "gov.in",
            "nic.in",
            "india.gov.in",

            # President of India
            "presidentofindia.nic.in",
            "rashtrapatibhavan.gov.in",

            # International organisations
            "un.org",
            "who.int",

            # Science / space
            "nasa.gov",

            # AI / technology official
            "openai.com",
            "anthropic.com",
            "deepmind.google",
            "blog.google",

            "microsoft.com",
            "apple.com",

            "nvidia.com",
            "ibm.com",
            "intel.com",

            "amazon.com",
            "aws.amazon.com",

            "meta.com",

            "huggingface.co",

            "deepseek.com",

            "tsmc.com"
        ]

        for trusted in trusted_domains:

            if (
                domain == trusted
                or domain.endswith(
                    "." + trusted
                )
            ):

                return True

        return False


    # =================================
    # GOVERNMENT DOMAIN
    # =================================

    def is_government_domain(
        self,
        domain
    ):

        if not domain:
            return False

        government_domains = [

            "gov.in",
            "nic.in",
            "india.gov.in",

            "presidentofindia.nic.in",
            "rashtrapatibhavan.gov.in"
        ]

        for item in government_domains:

            if (
                domain == item
                or domain.endswith(
                    "." + item
                )
            ):

                return True

        return False


    # =================================
    # OFFICIAL COMPANY DOMAIN
    # =================================

    def is_official_company(
        self,
        domain
    ):

        if not domain:
            return False

        official = [

            "openai.com",
            "anthropic.com",
            "deepmind.google",
            "blog.google",

            "microsoft.com",
            "nvidia.com",

            "amazon.com",
            "aws.amazon.com",

            "meta.com",

            "deepseek.com",
            "huggingface.co",

            "tsmc.com"
        ]

        for item in official:

            if (
                domain == item
                or domain.endswith(
                    "." + item
                )
            ):

                return True

        return False


    # =================================
    # WEAK DOMAINS
    # =================================

    def is_weak_domain(
        self,
        domain
    ):

        if not domain:
            return True

        weak = [

            "facebook.com",
            "instagram.com",
            "tiktok.com",

            "pinterest.com",

            "quora.com",

            "reddit.com"
        ]

        for item in weak:

            if (
                domain == item
                or domain.endswith(
                    "." + item
                )
            ):

                return True

        return False


    # =================================
    # CONTENT CHECK
    # =================================

    def has_real_content(
        self,
        result
    ):

        content = self.get_content(
            result
        )

        if not content:
            return False

        content = self.normalize(
            content
        )

        if len(content) < 80:
            return False

        bad_phrases = [

            "enable javascript",
            "javascript is required",
            "access denied",
            "page not found",
            "404 not found",
            "captcha",
            "robot check",
            "checking your browser"
        ]

        for phrase in bad_phrases:

            if phrase in content:
                return False

        return True


    # =================================
    # TITLE CHECK
    # =================================

    def valid_title(
        self,
        result
    ):

        title = self.get_title(
            result
        )

        if not title:
            return False

        if len(title) < 8:
            return False

        title = self.normalize(
            title
        )

        bad_titles = [

            "home",
            "homepage",
            "category",
            "categories",
            "archive",
            "archives",
            "search",
            "search results"
        ]

        if title in bad_titles:
            return False

        return True


    # =================================
    # BASE SCORE
    # =================================

    def calculate_score(
        self,
        result
    ):

        score = 0

        url = self.get_url(
            result
        )

        title = self.get_title(
            result
        )

        domain = self.get_domain(
            result
        )

        content = self.get_content(
            result
        )


        if url:
            score += 1

        if title:
            score += 1

        if len(content) >= 100:
            score += 1

        if len(content) >= 500:
            score += 1

        if self.is_trusted_domain(
            domain
        ):

            score += 3

        if self.is_government_domain(
            domain
        ):

            score += 3

        return score


    # =================================
    # VERIFY ONE
    # =================================

    def verify_one(
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

        domain = self.get_domain(
            item
        )

        has_content = (
            self.has_real_content(
                item
            )
        )

        valid_title = (
            self.valid_title(
                item
            )
        )

        trusted = (
            self.is_trusted_domain(
                domain
            )
        )

        government = (
            self.is_government_domain(
                domain
            )
        )

        official_company = (
            self.is_official_company(
                domain
            )
        )

        weak = (
            self.is_weak_domain(
                domain
            )
        )

        score = (
            self.calculate_score(
                item
            )
        )


        # =================================
        # STATUS
        # =================================

        if government and has_content:

            status = "CONFIRMED"

        elif (
            trusted
            and has_content
            and valid_title
        ):

            status = "CONFIRMED"

        elif (
            official_company
            and has_content
        ):

            status = "CONFIRMED"

        elif (
            has_content
            and not weak
        ):

            status = "REPORTED"

        else:

            status = "UNCERTAIN"


        # =================================
        # SAVE DATA
        # =================================

        item[
            "domain"
        ] = domain

        item[
            "verification_score"
        ] = score

        item[
            "verification_status"
        ] = status

        item[
            "status"
        ] = status

        item[
            "verified"
        ] = (
            status == "CONFIRMED"
        )

        item[
            "official_source"
        ] = (
            trusted
        )

        item[
            "government_source"
        ] = (
            government
        )

        return item


    # =================================
    # VERIFY ALL
    # =================================

    def verify(
        self,
        results
    ):

        if not results:
            return []

        output = []

        for result in results:

            try:

                verified = (
                    self.verify_one(
                        result
                    )
                )

                if verified:

                    output.append(
                        verified
                    )

            except Exception as error:

                item = dict(
                    result
                )

                item[
                    "status"
                ] = "UNCERTAIN"

                item[
                    "verified"
                ] = False

                item[
                    "verification_error"
                ] = str(error)

                output.append(
                    item
                )


        # =================================
        # SORT
        # =================================

        output.sort(

            key=lambda x: (

                1
                if x.get(
                    "status"
                ) == "CONFIRMED"
                else 0,

                x.get(
                    "verification_score",
                    0
                )

            ),

            reverse=True
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

        for result in results or []:

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

            "total": (
                confirmed
                + reported
                + uncertain
            )
        }


    # =================================
    # CONFIRMED RESULTS
    # =================================

    def confirmed_results(
        self,
        results
    ):

        return [

            result

            for result in (
                results or []
            )

            if str(
                result.get(
                    "status",
                    ""
                )
            ).upper()
            == "CONFIRMED"

        ]


    # =================================
    # REPORTED RESULTS
    # =================================

    def reported_results(
        self,
        results
    ):

        return [

            result

            for result in (
                results or []
            )

            if str(
                result.get(
                    "status",
                    ""
                )
            ).upper()
            == "REPORTED"

        ]


    # =================================
    # UNCERTAIN RESULTS
    # =================================

    def uncertain_results(
        self,
        results
    ):

        return [

            result

            for result in (
                results or []
            )

            if str(
                result.get(
                    "status",
                    ""
                )
            ).upper()
            == "UNCERTAIN"

        ]


    # =================================
    # SUPPORTED
    # =================================

    def is_supported(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return False

        status = str(
            result.get(
                "status",
                ""
            )
        ).upper()

        return status in [
            "CONFIRMED",
            "REPORTED"
        ]


    # =================================
    # VERIFIED RESULTS
    # =================================

    def verified_results(
        self,
        results
    ):

        if not results:
            return []

        output = []

        for result in results:

            if self.is_supported(
                result
            ):

                output.append(
                    result
                )

        return output