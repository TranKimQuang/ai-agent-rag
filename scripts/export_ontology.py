from pathlib import Path

from rdflib import Graph


def main() -> None:
    project_root = Path(__file__).parents[1]
    source = project_root / "ontology" / "document_qa.ttl"
    destination = project_root / "ontology" / "document_qa.owl"

    graph = Graph()
    graph.parse(source, format="turtle")
    graph.serialize(destination=destination, format="xml")
    print(f"Exported {len(graph)} RDF triples to {destination}")


if __name__ == "__main__":
    main()
