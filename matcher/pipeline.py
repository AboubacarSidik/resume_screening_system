import json
from multiprocessing import Pool, cpu_count
from pathlib import Path

from extractors.keyword_extractor import KeywordExtractor
from matcher.scorer import ResumeScorer
from parsers.jd_parser import JDParser
from parsers.resume_parser import ResumeParser

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_config() -> dict:
    with open(DATA_DIR / "config.json", encoding="utf-8") as f:
        return json.load(f)


def _process_one(args):
    file_path, jd, weights = args
    file_path = Path(file_path)
    extractor = KeywordExtractor(DATA_DIR / "skills_taxonomy.json")
    scorer = ResumeScorer(extractor, weights)

    try:
        text = ResumeParser().parse(file_path)
        if not text:
            raise ValueError("no text could be extracted")
        result = scorer.score(text, jd)
        result["error"] = None
    except Exception as e:
        # One broken file shouldn't stop the whole batch
        result = {"score": 0.0, "error": str(e)}

    result["candidate"] = file_path.name
    return result


def screen_resumes(jd_text: str, resume_paths, parallel: bool = True) -> list:
    """Parse the JD, score every resume, and return results ranked best first."""
    config = load_config()
    extractor = KeywordExtractor(DATA_DIR / "skills_taxonomy.json")
    jd = JDParser(extractor).parse(jd_text)

    tasks = [(str(p), jd, config["weights"]) for p in resume_paths]
    if not tasks:
        return []

    if parallel and len(tasks) > 1:
        with Pool(processes=min(cpu_count(), len(tasks))) as pool:
            results = pool.map(_process_one, tasks)
    else:
        results = [_process_one(t) for t in tasks]

    return sorted(results, key=lambda r: r["score"], reverse=True)
