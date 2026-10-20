from extractors.keyword_extractor import KeywordExtractor


class ResumeScorer:
    """Scores a resume against a parsed job description (0-100)."""

    def __init__(self, extractor: KeywordExtractor, weights: dict):
        self.extractor = extractor
        self.weights = weights

    def score(self, resume_text: str, jd: dict) -> dict:
        resume_skills = self.extractor.extract_skills(resume_text)
        resume_years = self.extractor.extract_years_of_experience(resume_text)

        matched_required = resume_skills & jd["required_skills"]
        matched_preferred = resume_skills & jd["preferred_skills"]
        matched_keywords = resume_skills & jd["keywords"]

        required_score = self._ratio(matched_required, jd["required_skills"])
        preferred_score = self._ratio(matched_preferred, jd["preferred_skills"])
        keyword_score = self._ratio(matched_keywords, jd["keywords"])

        if jd["min_years"] == 0:
            experience_score = 100.0
        else:
            experience_score = min(resume_years / jd["min_years"], 1.0) * 100

        total = (
            self.weights["required_skills"] * required_score
            + self.weights["preferred_skills"] * preferred_score
            + self.weights["experience"] * experience_score
            + self.weights["keywords"] * keyword_score
        )

        return {
            "score": round(total, 2),
            "matched_required": sorted(matched_required),
            "missing_required": sorted(jd["required_skills"] - resume_skills),
            "matched_preferred": sorted(matched_preferred),
            "matched_keywords": sorted(matched_keywords),
            "years_experience": resume_years,
        }

    @staticmethod
    def _ratio(matched: set, wanted: set) -> float:
        # If the JD asks for nothing in a category, don't penalise the candidate
        if not wanted:
            return 100.0
        return len(matched) / len(wanted) * 100
