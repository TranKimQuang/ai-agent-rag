from pathlib import Path

from rdflib import OWL, RDF, Graph, URIRef

from app.models import OntologyRelation, OntologySummary

DEFAULT_ONTOLOGY_PATH = Path(__file__).parents[2] / "ontology" / "document_qa.ttl"


def local_name(value: URIRef) -> str:
    """Return the readable last component of an RDF URI."""
    text = str(value)
    return text.rsplit("#", maxsplit=1)[-1].rsplit("/", maxsplit=1)[-1]


class OntologyService:
    """Loads the small AI/NLP ontology and exposes read-only queries."""

    def __init__(self, ontology_path: Path = DEFAULT_ONTOLOGY_PATH) -> None:
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")

    def summary(self) -> OntologySummary:
        classes = set(self.graph.subjects(RDF.type, OWL.Class))
        object_properties = set(self.graph.subjects(RDF.type, OWL.ObjectProperty))
        data_properties = set(self.graph.subjects(RDF.type, OWL.DatatypeProperty))
        schema_resources = classes | object_properties | data_properties
        individuals = {
            subject
            for subject, object_type in self.graph.subject_objects(RDF.type)
            if object_type in classes and subject not in schema_resources
        }
        return OntologySummary(
            classes=len(classes),
            object_properties=len(object_properties),
            data_properties=len(data_properties),
            individuals=len(individuals),
        )

    def find_relations(self, concept: str) -> list[OntologyRelation]:
        """Find outgoing and incoming relations for one named resource."""
        wanted = concept.strip().casefold()
        resources = {
            value
            for value in set(self.graph.subjects()) | set(self.graph.objects())
            if isinstance(value, URIRef) and local_name(value).casefold() == wanted
        }
        if not resources:
            return []

        relations: set[tuple[str, str, str]] = set()
        for resource in resources:
            for subject, predicate, object_value in self.graph.triples((resource, None, None)):
                if isinstance(object_value, URIRef) and predicate != RDF.type:
                    relations.add(
                        (local_name(subject), local_name(predicate), local_name(object_value))
                    )
            for subject, predicate, object_value in self.graph.triples((None, None, resource)):
                if isinstance(subject, URIRef) and predicate != RDF.type:
                    relations.add(
                        (local_name(subject), local_name(predicate), local_name(object_value))
                    )

        return [
            OntologyRelation(subject=subject, predicate=predicate, object=object_value)
            for subject, predicate, object_value in sorted(relations)
        ]
