#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pdfplumber


SOURCE_DIR = Path("/mnt/c/Users/zhi89/Desktop/量化")
OUTPUT_DIR = Path("/mnt/c/Users/zhi89/Desktop/量化/extracted")
MIN_CHARS = 500
MAX_FULL_PAGES = 400
LIMITED_PAGES = 200
TOC_SCAN_PAGES = 20

BOOKS = [
    (
        "common_stocks_and_uncommon_profits_and_other_writings.pdf",
        "common_stocks",
    ),
    (
        "security-analysis-benjamin-graham-6th-edition-pdf-february-24-2010-12-08-am-3-0-meg.pdf",
        "security_analysis",
    ),
    (
        "Essays-of-Warren-Buffett-_-Lessons-for-Corporate-America_Cunningham.pdf",
        "essays_buffett",
    ),
    ("The Most Important Thing by Howard Marks.pdf", "most_important_thing"),
    ("The-Psychology-of-Money-Morgan-Housel.pdf", "psychology_money"),
    ("a-random-walk-down-wall-street.pdf", "random_walk"),
    ("narrative&numbers.pdf", "narrative_numbers"),
    ("the-little-book-of-common-sense-investing.pdf", "little_book_indexing"),
    (
        "Algorithmic Trading Methods_ Applications Using Advanced Statistics, Optimization, and Machine Learning Techniques-Academic Press (2020).pdf",
        "algo_trading_methods",
    ),
    (
        "Machine Learning for Algorithmic Trading (2nd Edition).pdf",
        "ml_algo_trading",
    ),
    (
        "Quantitative Trading_ How to Build Your Own Algorithmic Trading Business-Wiley (2008).pdf",
        "quant_trading",
    ),
    (
        "Inside_the_Black_Box_Raising_Standards_Through_Cla.pdf",
        "black_box",
    ),
    ("Finding Alphas.pdf", "finding_alphas"),
]

CHAPTER_RE = re.compile(
    r"^\s*(chapter|chap\.|part|section)\s+([a-z0-9ivxlcdm]+)?(?:[\s:.\-]+.*)?$",
    re.IGNORECASE,
)
TOC_RE = re.compile(
    r"\b(contents|table of contents|contents at a glance)\b", re.IGNORECASE
)
NON_WORD_RE = re.compile(r"[^a-z0-9]+")


@dataclass
class PageText:
    page_num: int
    text: str


def slugify(value: str) -> str:
    return NON_WORD_RE.sub("_", value.strip().lower()).strip("_")


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def extract_page_text(page) -> str:
    try:
        if hasattr(page, "extract_text_simple"):
            text = page.extract_text_simple() or ""
        else:
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
    except Exception:
        text = page.extract_text() or ""
    return normalize_text(text)


def collect_pages(pdf_path: Path) -> tuple[list[PageText], int, list[int]]:
    pages: list[PageText] = []
    toc_pages: list[int] = []
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        limit = total_pages if total_pages <= MAX_FULL_PAGES else LIMITED_PAGES
        for idx, page in enumerate(pdf.pages[:limit], start=1):
            text = extract_page_text(page)
            if idx <= TOC_SCAN_PAGES and TOC_RE.search(text):
                toc_pages.append(idx)
            pages.append(PageText(page_num=idx, text=text))
    return pages, total_pages, sorted(set(toc_pages))


def detect_boundaries(pages: list[PageText]) -> list[dict]:
    boundaries: list[dict] = []
    for i, page in enumerate(pages):
        for line in page.text.splitlines():
            clean = re.sub(r"\s+", " ", line).strip()
            if not clean:
                continue
            if CHAPTER_RE.match(clean):
                kind_match = re.match(
                    r"^\s*(chapter|chap\.|part|section)\b", clean, re.IGNORECASE
                )
                if not kind_match:
                    continue
                kind = kind_match.group(1).lower()
                if kind.startswith("chap"):
                    kind = "chapter"
                boundaries.append(
                    {
                        "page_num": page.page_num,
                        "index": i,
                        "kind": kind,
                        "title": clean,
                    }
                )
                break
    return boundaries


def write_text(output_path: Path, text: str) -> dict:
    data = {"path": str(output_path), "status": "skipped", "chars": len(text)}
    if len(text) < MIN_CHARS:
        data["reason"] = "below_min_chars"
        return data
    if output_path.exists():
        data["reason"] = "exists"
        return data
    output_path.write_text(text, encoding="utf-8")
    data["status"] = "written"
    return data


def render_pages(pages: list[PageText]) -> str:
    chunks = []
    for page in pages:
        if page.text:
            chunks.append(f"[Page {page.page_num}]\n{page.text}")
    return "\n\n".join(chunks).strip()


def split_by_boundaries(prefix: str, pages: list[PageText], boundaries: list[dict]) -> list[dict]:
    results = []
    chapter_index = 0
    part_index = 0
    section_index = 0
    for pos, boundary in enumerate(boundaries):
        start_idx = boundary["index"]
        end_idx = boundaries[pos + 1]["index"] if pos + 1 < len(boundaries) else len(pages)
        chunk_pages = pages[start_idx:end_idx]
        text = render_pages(chunk_pages)
        kind = boundary["kind"]
        if kind == "part":
            part_index += 1
            stem = f"{prefix}_part{part_index}"
        elif kind == "section":
            section_index += 1
            stem = f"{prefix}_section{section_index}"
        else:
            chapter_index += 1
            stem = f"{prefix}_ch{chapter_index}"
        results.append({"stem": slugify(stem), "text": text, "pages": chunk_pages})
    return results


def split_by_page_segments(prefix: str, pages: list[PageText], segment_size: int = 100) -> list[dict]:
    results = []
    for start in range(0, len(pages), segment_size):
        chunk_pages = pages[start : start + segment_size]
        if not chunk_pages:
            continue
        page_start = chunk_pages[0].page_num
        page_end = chunk_pages[-1].page_num
        stem = slugify(f"{prefix}_pages_{page_start}_{page_end}")
        results.append(
            {"stem": stem, "text": render_pages(chunk_pages), "pages": chunk_pages}
        )
    return results


def extract_book(pdf_path: Path, prefix: str, output_dir: Path) -> dict:
    result = {
        "pdf": str(pdf_path),
        "prefix": prefix,
        "total_pages": 0,
        "toc_pages": [],
        "outputs": [],
        "failures": [],
        "mode": None,
    }
    pages, total_pages, toc_pages = collect_pages(pdf_path)
    result["total_pages"] = total_pages
    result["toc_pages"] = toc_pages
    boundaries = detect_boundaries(pages)

    if boundaries:
        chunks = split_by_boundaries(prefix, pages, boundaries)
        result["mode"] = "chapters"
    else:
        chunks = split_by_page_segments(prefix, pages)
        result["mode"] = "segments"

    for chunk in chunks:
        output_path = output_dir / f"{chunk['stem']}.txt"
        write_result = write_text(output_path, chunk["text"])
        write_result["page_range"] = (
            [chunk["pages"][0].page_num, chunk["pages"][-1].page_num]
            if chunk["pages"]
            else None
        )
        result["outputs"].append(write_result)

    written = [o for o in result["outputs"] if o["status"] == "written"]
    if not written:
        result["failures"].append("no_output_files_written")
    return result


def run_worker(source_dir: Path, output_dir: Path, filename: str, prefix: str) -> dict:
    pdf_path = source_dir / filename
    if not pdf_path.exists():
        return {
            "pdf": str(pdf_path),
            "prefix": prefix,
            "outputs": [],
            "failures": ["missing_file"],
        }
    return extract_book(pdf_path, prefix, output_dir)


def run(
    source_dir: Path,
    output_dir: Path,
    report_json: Path | None = None,
    per_book_timeout: int = 0,
) -> dict:
    summary = {"books": [], "failures": []}
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, prefix in BOOKS:
        print(f"Processing: {filename}", file=sys.stderr, flush=True)
        try:
            if per_book_timeout > 0:
                cmd = [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--worker",
                    "--source-dir",
                    str(source_dir),
                    "--output-dir",
                    str(output_dir),
                    "--worker-filename",
                    filename,
                    "--worker-prefix",
                    prefix,
                ]
                completed = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=per_book_timeout,
                    check=False,
                )
                if completed.returncode != 0:
                    stderr = completed.stderr.strip() or completed.stdout.strip()
                    raise RuntimeError(stderr or f"worker_exit_{completed.returncode}")
                book_result = json.loads(completed.stdout)
            else:
                book_result = run_worker(source_dir, output_dir, filename, prefix)
        except Exception as exc:
            book_result = {
                "pdf": str(source_dir / filename),
                "prefix": prefix,
                "outputs": [],
                "failures": [f"exception: {exc}"],
            }
            summary["failures"].append({"pdf": filename, "error": str(exc)})
        summary["books"].append(book_result)
        if report_json:
            report_json.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=None)
    parser.add_argument("--per-book-timeout", type=int, default=0)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--worker-filename", default=None)
    parser.add_argument("--worker-prefix", default=None)
    args = parser.parse_args()

    if args.worker:
        if not args.worker_filename or not args.worker_prefix:
            raise SystemExit("worker mode requires --worker-filename and --worker-prefix")
        report = run_worker(
            args.source_dir, args.output_dir, args.worker_filename, args.worker_prefix
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    report = run(
        args.source_dir,
        args.output_dir,
        args.report_json,
        per_book_timeout=args.per_book_timeout,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
