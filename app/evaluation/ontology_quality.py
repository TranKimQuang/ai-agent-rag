from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from owlrl import DeductiveClosure, OWLRL_Semantics
from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef
from rdflib.namespace import SKOS

from app.ontology.service import DEFAULT_ONTOLOGY_PATH, OntologyService, local_name

DEFAULT_QUERY_DIRECTORY = Path(__file__).parents[2] / "ontology" / "queries"


@dataclass(frozen=True)
class ConsistencyIssue:
    kind: str
    resource: str
    detail: str


def _read_manifest(query_directory: Path) -> list[dict[str, Any]]:
    path = query_directory / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _display_value(value: object) -> str:
    if isinstance(value, URIRef):
        return local_name(value)
    if isinstance(value, Literal):
        return str(value)
    return str(value)


def _portable_path(path: Path) -> str:
    project_root = Path(__file__).parents[2].resolve()
    try:
        return path.resolve().relative_to(project_root).as_posix()
    except ValueError:
        return str(path.resolve())


def _consistency_issues(graph: Graph) -> list[ConsistencyIssue]:
    issues: set[tuple[str, str, str]] = set()

    for resource in graph.subjects(RDF.type, OWL.Nothing):
        issues.add(
            (
                "owl_nothing_instance",
                _display_value(resource),
                "Resource was inferred as an instance of owl:Nothing.",
            )
        )

    for left_class, right_class in graph.subject_objects(OWL.disjointWith):
        left_instances = set(graph.subjects(RDF.type, left_class))
        for resource in left_instances & set(graph.subjects(RDF.type, right_class)):
            issues.add(
                (
                    "disjoint_class_membership",
                    _display_value(resource),
                    (
                        f"Typed as both {_display_value(left_class)} and "
                        f"{_display_value(right_class)}."
                    ),
                )
            )

    for predicate in graph.subjects(RDF.type, OWL.IrreflexiveProperty):
        for subject in graph.subjects(predicate, None):
            if (subject, predicate, subject) in graph:
                issues.add(
                    (
                        "irreflexive_property_violation",
                        _display_value(subject),
                        f"Self relation through {_display_value(predicate)}.",
                    )
                )

    for predicate in graph.subjects(RDF.type, OWL.AsymmetricProperty):
        for subject, object_value in graph.subject_objects(predicate):
            if subject != object_value and (object_value, predicate, subject) in graph:
                issues.add(
                    (
                        "asymmetric_property_violation",
                        _display_value(predicate),
                        (
                            f"Both {_display_value(subject)} -> "
                            f"{_display_value(object_value)} and the reverse relation exist."
                        ),
                    )
                )

    for predicate in graph.subjects(RDF.type, OWL.FunctionalProperty):
        for subject in set(graph.subjects(predicate, None)):
            values = set(graph.objects(subject, predicate))
            for left in values:
                for right in values:
                    if left != right and (left, OWL.differentFrom, right) in graph:
                        issues.add(
                            (
                                "functional_property_violation",
                                _display_value(subject),
                                f"Different values found for {_display_value(predicate)}.",
                            )
                        )

    return [ConsistencyIssue(*issue) for issue in sorted(issues)]


def evaluate_ontology(
    ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
    query_directory: Path = DEFAULT_QUERY_DIRECTORY,
) -> dict[str, Any]:
    service = OntologyService(ontology_path)
    source_graph = service.graph
    reasoned_graph = Graph()
    for triple in source_graph:
        reasoned_graph.add(triple)

    triples_before_reasoning = len(reasoned_graph)
    DeductiveClosure(
        OWLRL_Semantics,
        axiomatic_triples=False,
        datatype_axioms=True,
    ).expand(reasoned_graph)
    issues = _consistency_issues(reasoned_graph)

    object_properties = set(source_graph.subjects(RDF.type, OWL.ObjectProperty))
    data_properties = set(source_graph.subjects(RDF.type, OWL.DatatypeProperty))
    properties = object_properties | data_properties
    domain_properties = set(source_graph.subjects(RDFS.domain, None))
    range_properties = set(source_graph.subjects(RDFS.range, None))
    inverse_properties = set(source_graph.subjects(OWL.inverseOf, None))

    competency_questions = []
    for item in _read_manifest(query_directory):
        query_path = query_directory / item["query"]
        result = source_graph.query(query_path.read_text(encoding="utf-8"))
        rows = [
            {
                str(variable): _display_value(value)
                for variable, value in zip(result.vars, row, strict=True)
            }
            for row in result
        ]
        minimum_rows = int(item["minimum_rows"])
        competency_questions.append(
            {
                **item,
                "actual_rows": len(rows),
                "passed": len(rows) >= minimum_rows,
                "sample_rows": rows[:5],
            }
        )

    exact_mappings = sorted(
        {
            (_display_value(subject), str(object_value))
            for subject, object_value in source_graph.subject_objects(SKOS.exactMatch)
        }
    )
    close_mappings = sorted(
        {
            (_display_value(subject), str(object_value))
            for subject, object_value in source_graph.subject_objects(SKOS.closeMatch)
        }
    )
    summary = service.summary()

    return {
        "ontology_path": _portable_path(ontology_path),
        "reasoner": "OWL-RL (owlrl)",
        "consistent": not issues,
        "consistency_issues": [asdict(issue) for issue in issues],
        "triples_before_reasoning": triples_before_reasoning,
        "triples_after_reasoning": len(reasoned_graph),
        "inferred_triples": len(reasoned_graph) - triples_before_reasoning,
        "schema": {
            "classes": summary.classes,
            "object_properties": summary.object_properties,
            "data_properties": summary.data_properties,
            "individuals": summary.individuals,
            "properties_with_domain": len(properties & domain_properties),
            "properties_with_range": len(properties & range_properties),
            "object_properties_with_inverse": len(object_properties & inverse_properties),
        },
        "cso_mapping": {
            "exact_match_count": len(exact_mappings),
            "close_match_count": len(close_mappings),
            "exact_matches": [
                {"local_concept": local, "external_uri": external}
                for local, external in exact_mappings
            ],
            "close_matches": [
                {"local_concept": local, "external_uri": external}
                for local, external in close_mappings
            ],
            "source_version": "CSO 3.5",
            "reviewed_on": "2026-10-03",
            "manual_review_status": "completed",
        },
        "competency_questions": competency_questions,
        "competency_questions_passed": sum(
            item["passed"] for item in competency_questions
        ),
        "competency_questions_total": len(competency_questions),
    }


def render_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["consistent"] else "FAIL"
    schema = report["schema"]
    lines = [
        "# Ontology quality evaluation",
        "",
        "## 1. Reasoner consistency",
        "",
        f"- Reasoner: {report['reasoner']}",
        f"- Kết quả: **{status}**",
        f"- Triple trước suy luận: {report['triples_before_reasoning']}",
        f"- Triple sau suy luận: {report['triples_after_reasoning']}",
        f"- Triple suy ra: {report['inferred_triples']}",
        f"- Số lỗi consistency: {len(report['consistency_issues'])}",
        "",
        "## 2. Thống kê mô hình",
        "",
        f"- Class: {schema['classes']}",
        f"- Object property: {schema['object_properties']}",
        f"- Datatype property: {schema['data_properties']}",
        f"- Individual: {schema['individuals']}",
        f"- Property có domain: {schema['properties_with_domain']}",
        f"- Property có range: {schema['properties_with_range']}",
        f"- Object property có inverse: {schema['object_properties_with_inverse']}",
        "",
        "## 3. Competency questions",
        "",
        "| ID | Câu hỏi | Số dòng tối thiểu | Số dòng thực tế | Kết quả |",
        "|---|---|---:|---:|---|",
    ]
    for item in report["competency_questions"]:
        result = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['id']} | {item['question']} | {item['minimum_rows']} | "
            f"{item['actual_rows']} | {result} |"
        )

    mapping = report["cso_mapping"]
    lines.extend(
        [
            "",
            "## 4. CSO mapping",
            "",
            f"- `skos:exactMatch`: {mapping['exact_match_count']}",
            f"- `skos:closeMatch`: {mapping['close_match_count']}",
            (
                "- Đã rà soát thủ công URI và phạm vi ánh xạ với CSO 3.5 ngày 03/10/2026; "
                "reasoner chỉ kiểm tra mô hình nội bộ và không tự chứng minh tương đương "
                "ngữ nghĩa với nguồn bên ngoài."
            ),
            "",
            "| Concept cục bộ | Quan hệ | URI bên ngoài |",
            "|---|---|---|",
        ]
    )
    for item in mapping["exact_matches"]:
        lines.append(
            f"| {item['local_concept']} | exactMatch | {item['external_uri']} |"
        )
    for item in mapping["close_matches"]:
        lines.append(
            f"| {item['local_concept']} | closeMatch | {item['external_uri']} |"
        )

    if report["consistency_issues"]:
        lines.extend(["", "## 5. Consistency issues", ""])
        for issue in report["consistency_issues"]:
            lines.append(
                f"- `{issue['kind']}` — {issue['resource']}: {issue['detail']}"
            )
    return "\n".join(lines) + "\n"
