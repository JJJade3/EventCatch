"""Runs extract_and_clean against a hand-labeled golden dataset and reports field-level accuracy.

See README.md "Eval" section for methodology and how to read the result.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from eventcatch.extraction import extract_and_clean
from eventcatch.logging_config import configure_logging

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


def normalize(value: Any) -> str:
    return str(value).lower().strip()


def compare_record(
    expected: dict[str, Any], actual: dict[str, Any]
) -> tuple[int, int, list[tuple[str, Any, Any]]]:
    correct = 0
    mismatches = []

    for field_name, expected_value in expected.items():
        if field_name in actual and normalize(expected_value) == normalize(actual[field_name]):
            correct += 1
        else:
            mismatches.append((field_name, expected_value, actual.get(field_name)))

    return correct, len(expected), mismatches


async def run_eval() -> None:
    golden_dataset = json.loads(GOLDEN_DATASET_PATH.read_text())

    total_correct = 0
    total_fields = 0

    for item in golden_dataset:
        post = item["post"]
        expected = item["expected"]

        record = await extract_and_clean(post)
        actual = record.model_dump(mode="json", exclude_none=True)

        correct, total, mismatches = compare_record(expected, actual)
        total_correct += correct
        total_fields += total

        print(f"Post: {post[:40]}...")
        print(f"  {correct}/{total} fields correct")
        if mismatches:
            print("  Mismatches:")
            for field_name, expected_value, actual_value in mismatches:
                print(f"    {field_name}: expected {expected_value!r}, got {actual_value!r}")

    accuracy = total_correct / total_fields
    print(f"\nOverall accuracy: {total_correct}/{total_fields} = {accuracy:.1%}")


def main() -> None:
    configure_logging()
    asyncio.run(run_eval())


if __name__ == "__main__":
    main()
