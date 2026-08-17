"""Inspect and extract structured leaderboard payloads from archived AA pages."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._inside_script = False
        self._parts: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self._inside_script = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_script:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._inside_script:
            self.scripts.append("".join(self._parts))
            self._inside_script = False
            self._parts = []


def walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def structured_datasets(html: str) -> list[list[dict[str, Any]]]:
    collector = ScriptCollector()
    collector.feed(html)
    found: list[list[dict[str, Any]]] = []
    seen: set[str] = set()
    for script in collector.scripts:
        try:
            payload = json.loads(script)
        except json.JSONDecodeError:
            continue
        for value in walk(payload):
            if not isinstance(value, list) or not value or not all(isinstance(row, dict) for row in value):
                continue
            keys = {key for row in value for key in row.keys()}
            if "label" not in keys or len(keys) < 3:
                continue
            signature = json.dumps(value, sort_keys=True, ensure_ascii=True)
            if signature not in seen:
                seen.add(signature)
                found.append(value)
    return found


def nearest_escaped_field(html: str, slug: str, field: str) -> tuple[str | None, int | None]:
    marker = f'\\"slug\\":\\"{slug}\\"'
    values: list[tuple[str, int]] = []
    for position in (match.start() for match in re.finditer(re.escape(marker), html)):
        window = html[max(0, position - 120_000) : position + len(marker)]
        matches = list(re.finditer(re.escape(f'\\"{field}\\":') + r"([^,}]+)", window))
        if matches:
            values.append((matches[-1].group(1), len(window) - matches[-1].start()))
    return min(values, key=lambda item: item[1]) if values else (None, None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    target_slugs = (
        "kimi-k3",
        "gpt-5-6-sol",
        "gpt-5-5",
        "claude-fable-5",
        "claude-opus-4-8",
        "gemini-3-1-pro-preview",
        "glm-5-2",
        "deepseek-v4-pro",
        "deepseek-v4-flash",
        "qwen3-8-max",
    )
    fields = ("hle", "lcr", "omniscience", "mmmu_pro")

    for path in args.paths:
        html = path.read_text(encoding="utf-8")
        print(f"\nFILE {path} bytes={len(html)}")
        datasets = structured_datasets(html)
        print(f"datasets={len(datasets)}")
        for index, rows in enumerate(datasets, start=1):
            keys = sorted({key for row in rows for key in row.keys()})
            print(f"DATASET {index} rows={len(rows)} keys={keys}")
            for row in rows[:25]:
                print(json.dumps(row, ensure_ascii=False, sort_keys=True))
        for slug in target_slugs:
            extracted = {}
            for field in fields:
                value, distance = nearest_escaped_field(html, slug, field)
                if value is not None:
                    extracted[field] = {"value": value, "distance": distance}
            if extracted:
                print("MODEL", slug, json.dumps(extracted, sort_keys=True))


if __name__ == "__main__":
    main()
