from app.models import Chunk
from app.ontology.service import OntologyService
from scripts.export_result_context_audit import (
    apply_review_annotations,
    collect_result_rows,
    summarize_review,
)


def test_collect_result_rows_exports_scoped_relations() -> None:
    service = OntologyService()
    chunks, _ = service.index_chunks(
        [
            Chunk(
                id="paper:p1:c1",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text="The ZXNet model achieved 83.5 BLEU on the FooBench dataset.",
            )
        ]
    )

    rows = collect_result_rows(service, chunks)

    assert len(rows) == 1
    assert rows[0]["models"] == "ZXNet"
    assert rows[0]["datasets"] == "FooBench"
    assert rows[0]["metrics"] == "BLEU"
    assert rows[0]["values"] == "83.5"
    assert rows[0]["review_status"] == "pending"


def test_review_annotations_validate_links_and_calculate_precision() -> None:
    rows = [
        {
            "result_id": "r1",
            "methods": "Method A | Wrong Method",
            "models": "Model A",
            "datasets": "",
            "metrics": "BLEU",
            "values": "1.0",
            "review_status": "pending",
            "review_note": "",
        }
    ]
    reviewed = apply_review_annotations(
        rows,
        {
            "annotations": {
                "r1": {
                    "methods_invalid": ["Wrong Method"],
                    "values_ambiguous": ["1.0"],
                }
            }
        },
    )

    assert reviewed[0]["methods_review"] == "mixed"
    assert reviewed[0]["datasets_review"] == "not_present"
    assert reviewed[0]["values_review"] == "ambiguous"
    assert reviewed[0]["review_status"] == "needs_fix"
    summary = summarize_review(reviewed)
    assert summary["result_instance_precision"] == 1.0
    assert summary["role_precision"]["methods"]["reviewed_precision"] == 0.5
    assert summary["role_precision"]["values"]["reviewed_precision"] is None
