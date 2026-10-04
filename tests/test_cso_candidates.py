import csv
from pathlib import Path

from scripts.analyze_cso_candidates import (
    cso_uri,
    has_lexical_support,
    load_cso_branch,
)


def write_cso(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, delimiter=";").writerows(rows)


def test_load_cso_branch_keeps_descendants_and_aliases(tmp_path: Path) -> None:
    path = tmp_path / "cso.csv"
    write_cso(
        path,
        [
            ["artificial intelligence", "rdfs:label", "artificial intelligence"],
            ["machine learning", "rdfs:label", "machine learning"],
            ["deep learning", "rdfs:label", "deep learning"],
            ["dl", "rdfs:label", "dl"],
            ["dl", "klink:primaryLabel", "deep learning"],
            ["artificial intelligence", "klink:broaderGeneric", "machine learning"],
            ["machine learning", "klink:broaderGeneric", "deep learning"],
        ],
    )

    vocabulary = load_cso_branch(path, ["artificial intelligence"])

    assert set(vocabulary.documents) == {
        "artificial intelligence",
        "machine learning",
        "deep learning",
    }
    assert "dl" in vocabulary.documents["deep learning"]
    assert vocabulary.depths["deep learning"] == 2


def test_cso_uri_uses_official_topic_namespace() -> None:
    assert cso_uri("natural language processing") == (
        "https://cso.kmi.open.ac.uk/topics/natural_language_processing"
    )


def test_lexical_support_handles_simple_plural_inflection() -> None:
    assert has_lexical_support(
        "Which machine translation systems are evaluated?", "machine translations"
    )
    assert not has_lexical_support("How was annotation done?", "annealing process")
