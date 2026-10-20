import argparse
import csv
from datetime import datetime
from pathlib import Path

from matcher.pipeline import BASE_DIR, load_config, screen_resumes


def save_csv(results: list, output_dir: Path) -> Path:
    output_dir.mkdir(exist_ok=True)
    out_file = output_dir / f"results_{datetime.now():%Y%m%d_%H%M%S}.csv"

    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "candidate", "score", "matched_required",
                         "missing_required", "matched_preferred", "years_experience", "error"])
        for rank, r in enumerate(results, start=1):
            writer.writerow([
                rank,
                r["candidate"],
                r["score"],
                ", ".join(r.get("matched_required", [])),
                ", ".join(r.get("missing_required", [])),
                ", ".join(r.get("matched_preferred", [])),
                r.get("years_experience", ""),
                r["error"] or "",
            ])
    return out_file


def main():
    config = load_config()

    parser = argparse.ArgumentParser(description="Rank resumes against a job description.")
    parser.add_argument("--jd", type=Path, default=BASE_DIR / "input" / "job_description.txt",
                        help="Path to the job description .txt file")
    parser.add_argument("--resumes", type=Path, default=BASE_DIR / "input" / "resumes",
                        help="Folder containing the resumes")
    parser.add_argument("--top", type=int, default=config["top_n"],
                        help="How many candidates to display")
    args = parser.parse_args()

    jd_text = args.jd.read_text(encoding="utf-8")
    resume_files = sorted(
        p for p in args.resumes.iterdir()
        if p.suffix.lower() in config["supported_extensions"]
    )
    if not resume_files:
        print(f"No resumes found in {args.resumes}")
        return

    results = screen_resumes(jd_text, resume_files)

    print("=" * 60)
    print("SCREENING RESULTS")
    print("=" * 60)
    for rank, r in enumerate(results[:args.top], start=1):
        if r["error"]:
            print(f"Rank #{rank}: {r['candidate']} | ERROR: {r['error']}")
            continue
        matched = ", ".join(r["matched_required"] + r["matched_preferred"]) or "-"
        print(f"Rank #{rank}: {r['candidate']} | Score: {r['score']:.2f}/100 | Matched: {matched}")

    out_file = save_csv(results, BASE_DIR / "output")
    print(f"\nFull results saved to {out_file}")


if __name__ == "__main__":
    # Guard is required for multiprocessing on Windows
    main()
