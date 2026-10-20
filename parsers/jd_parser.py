from extractors.keyword_extractor import KeywordExtractor

REQUIRED_HEADINGS = ("required", "requirements", "must have")
PREFERRED_HEADINGS = ("preferred", "nice to have", "bonus")
OTHER_HEADINGS = ("experience", "responsibilities", "about", "benefits")


class JDParser:
    """Splits a job description into required skills, preferred skills and keywords."""

    def __init__(self, extractor: KeywordExtractor):
        self.extractor = extractor

    def parse(self, jd_text: str) -> dict:
        sections = {"required": [], "preferred": [], "other": []}
        current = "other"

        for line in jd_text.splitlines():
            heading = line.strip().lower().rstrip(":")
            if heading.startswith(REQUIRED_HEADINGS):
                current = "required"
                continue
            if heading.startswith(PREFERRED_HEADINGS):
                current = "preferred"
                continue
            if heading.startswith(OTHER_HEADINGS):
                current = "other"
                continue
            sections[current].append(line)

        required = self.extractor.extract_skills("\n".join(sections["required"]))
        preferred = self.extractor.extract_skills("\n".join(sections["preferred"])) - required
        keywords = self.extractor.extract_skills(jd_text) - required - preferred

        return {
            "required_skills": required,
            "preferred_skills": preferred,
            "keywords": keywords,
            "min_years": self.extractor.extract_years_of_experience(jd_text),
        }
