class ResearchRanker:

    def __init__(self):
        pass

    # =================================
    # SAFE NUMBER
    # =================================

    def number(self, value):

        try:
            return float(value or 0)

        except Exception:
            return 0.0

    # =================================
    # GET STATUS
    # =================================

    def get_status(self, result):

        return str(
            result.get(
                "status",
                "UNCERTAIN"
            )
        ).upper()

    # =================================
    # SOURCE QUALITY
    # =================================

    def source_quality(self, result):

        status = self.get_status(result)

        trust = self.number(
            result.get(
                "trust_score",
                0
            )
        )

        verification = self.number(
            result.get(
                "verification_score",
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

        score = 0.0

        # Status
        if status == "CONFIRMED":
            score += 50

        elif status == "REPORTED":
            score += 30

        else:
            score += 10

        # Trust
        score += min(trust, 30)

        # Agreement
        score += min(agreement, 30)

        # Verification
        score += min(
            verification / 5,
            20
        )

        # Freshness
        score += min(
            freshness / 5,
            20
        )

        return score

    # =================================
    # RANK ONE
    # =================================

    def rank_one(self, result):

        if not isinstance(result, dict):
            return result

        score = self.source_quality(
            result
        )

        result[
            "rank_score"
        ] = round(
            score,
            2
        )

        return result

    # =================================
    # RANK ALL
    # =================================

    def rank(
        self,
        results,
        max_results=7
    ):

        if not results:
            return []

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

            valid.append(
                result
            )

        if not valid:
            return []

        # Sort highest score first
        valid.sort(
            key=lambda item:
                self.number(
                    item.get(
                        "rank_score",
                        0
                    )
                ),
            reverse=True
        )

        # Keep multiple sources
        selected = valid[
            :max_results
        ]

        # Give source numbers
        for index, result in enumerate(
            selected,
            start=1
        ):

            result[
                "source_number"
            ] = index

        return selected

    # =================================
    # PROCESS
    # =================================

    def process(
        self,
        results,
        max_results=7
    ):

        return self.rank(
            results,
            max_results
        )