import json
import re
from pathlib import Path
from typing import Set

# Matches "5 years", "3+ years", "10 yrs" ...
YEARS_PATTERN = re.compile(r"(\d{1,2})\s*\+?\s*(?:years|yrs)", re.IGNORECASE)


class KeywordExtractor:
    """Finds known skills and years of experience in a piece of text."""

    def __init__(self, taxonomy_path):
        with open(taxonomy_path, encoding="utf-8") as f:
            self.skills_taxonomy = json.load(f)

    def extract_skills(self, text: str) -> Set[str]:
        text_lower = text.lower()
        found_skills = set()

        for category, skills_dict in self.skills_taxonomy.items():
            for skill_name, variations in skills_dict.items():
                for variation in variations:
                    # Custom boundaries instead of \b so "c++", "c#" and ".js" work,
                    # and "java" doesn't match inside "javascript"
                    pattern = r"(?<![\w+#.])" + re.escape(variation) + r"(?![\w+#])"
                    if re.search(pattern, text_lower):
                        found_skills.add(skill_name)
                        break
        return found_skills

    def extract_years_of_experience(self, text: str) -> int:
        years = [int(n) for n in YEARS_PATTERN.findall(text)]
        return max(years, default=0)
