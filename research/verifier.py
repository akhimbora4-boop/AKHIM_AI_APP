import re
from urllib.parse import urlparse


class ResearchVerifier:

    def __init__(self):

        self.high_trust_domains = {
            "gov.in",
            "nic.in",
            "india.gov.in",
            "pib.gov.in",
            "who.int",
            "un.org",
            "nature.com",
            "science.org",
            "openai.com",
            "google.com",
            "microsoft.com",
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "nytimes.com"
        }

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

    def get_domain(self, result):
        url = str(result.get("url", "")).strip()
        if not url:
            return ""
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def domain_matches(self, domain, trusted_domain):
        if not domain:
            return False
        if domain == trusted_domain:
            return True
        return domain.endswith("." + trusted_domain)

    def trust_score(self, result):
        domain = self.get_domain(result)
        if not domain:
            return 0

        for trusted in self.high_trust_domains:
            if self.domain_matches(domain, trusted):
                if domain.endswith(".gov.in") or domain == "gov.in":
                    return 50
                return 40

        for weak in self.weak_domains:
            if self.domain_matches(domain, weak):
                return 5

        return 15

    def normalize(self, text):
        if text is None:
            return ""
        text = str(text).lower()
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def word_set(self, text):
        text = self.normalize(text)
        if not text:
            return set()
        return set(text.split())

    def similarity(self, text1, text2):
        words1 = self.word_set(text1)
        words2 = self.word_set(text2)
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def get_text(self, result):
        parts = []
        for key in ["title", "content", "snippet", "description"]:
            value = result.get(key, "")
            if value:
                parts.append(str(value))
        return " ".join(parts)

    def content_quality(self, result):
        score = 0
        title = str(result.get("title", "")).strip()
        content = str(result.get("content", "")).strip()
        snippet = str(result.get("snippet", "")).strip()

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

    def agreement_score(self, result, results):
        current = self.get_text(result)
        if not current:
            return 0
        score = 0
        current_domain = self.get_domain(result)

        for other in results:
            if other is result:
                continue
            other_domain = self.get_domain(other)
            if current_domain and other_domain and current_domain == other_domain:
                continue
            other_text = self.get_text(other)
            sim = self.similarity(current, other_text)
            if sim >= 0.45:
                score += 25
            elif sim >= 0.30:
                score += 15
            elif sim >= 0.20:
                score += 8

        if score > 50:
            score = 50
        return score

    def verify_one(self, result, results):
        if not isinstance(result, dict):
            return result

        trust = self.trust_score(result)
        content = self.content_quality(result)
        agreement = self.agreement_score(result, results)
        total = trust + content + agreement

        result["trust_score"] = trust
        result["agreement_score"] = agreement
        result["verification_score"] = total

        if trust >= 40 or agreement >= 25:
            result["status"] = "CONFIRMED"
        elif trust >= 15 and content >= 15:
            result["status"] = "REPORTED"
        elif content >= 8:
            result["status"] = "REPORTED"
        else:
            result["status"] = "UNCERTAIN"

        return result

    def verify(self, results):
        if not results:
            return []

        valid = [r for r in results if isinstance(r, dict)]
        if not valid:
            return []

        for result in valid:
            self.verify_one(result, valid)

        for result in valid:
            result["agreement_score"] = self.agreement_score(result, valid)

        for result in valid:
            trust = float(result.get("trust_score", 0))
            agreement = float(result.get("agreement_score", 0))
            content = self.content_quality(result)
            result["verification_score"] = trust + agreement + content

            if trust >= 40 or agreement >= 25:
                result["status"] = "CONFIRMED"
            elif trust >= 15 and content >= 15:
                result["status"] = "REPORTED"
            elif content >= 8:
                result["status"] = "REPORTED"
            else:
                result["status"] = "UNCERTAIN"

        return valid
