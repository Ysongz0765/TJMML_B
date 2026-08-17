import json
import re
from pathlib import Path


def extract_leaderboard(html_path: Path) -> list[dict]:
    html = html_path.read_text(encoding="utf-8")
    for match in re.finditer(r"<script[^>]*>(.*?)</script>", html, flags=re.DOTALL | re.IGNORECASE):
        text = match.group(1)
        if "AA-LCR" not in text or '"data"' not in text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        rows = payload.get("data") if isinstance(payload, dict) else None
        if isinstance(rows, list) and any(isinstance(row, dict) and "AA-LCR" in row for row in rows):
            return rows
    raise ValueError("AA-LCR leaderboard dataset was not found in the archived HTML")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    html_path = root / "sources" / "html" / "SRC014_artificial_analysis_aa_lcr.html"
    rows = extract_leaderboard(html_path)
    print(f"rows={len(rows)}")
    for row in rows:
        print(row.get("label"), row.get("AA-LCR"), row.get("detailsUrl"))

    html = html_path.read_text(encoding="utf-8")
    for slug in (
        "gpt-5-5",
        "claude-opus-4-8",
        "gemini-3-1-pro-preview",
        "deepseek-v4-pro",
        "deepseek-v4-flash",
        "qwen3-8-max",
    ):
        marker = f'\\"slug\\":\\"{slug}\\"'
        positions = [match.start() for match in re.finditer(re.escape(marker), html)]
        if not positions:
            print("MODEL", slug, "not found")
            continue
        candidate = "not found"
        candidate_distance = None
        for position in positions:
            window = html[max(0, position - 80_000) : position + len(marker)]
            lcr_matches = list(re.finditer(re.escape('\\"lcr\\":') + r"([^,}]+)", window))
            if lcr_matches:
                candidate = lcr_matches[-1].group(1)
                candidate_distance = len(window) - lcr_matches[-1].start()
        print("MODEL", slug, "lcr", candidate, "distance", candidate_distance, "occurrences", len(positions))


if __name__ == "__main__":
    main()
