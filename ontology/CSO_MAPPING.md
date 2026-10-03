# CSO subset mapping

This project reuses a small, task-focused subset of the Computer Science Ontology (CSO)
instead of importing the full ontology. The mapping is aligned with CSO v3.5 and uses the
official topic URI pattern documented by the CSO Portal.

| Local concept | CSO topic | Mapping |
| --- | --- | --- |
| `InformationRetrieval` | `information_retrieval` | `skos:exactMatch` |
| `NaturalLanguageProcessing` | `natural_language_processing` | `skos:exactMatch` |
| `QuestionAnswering` | `question_answering` | `skos:closeMatch` |
| `RetrievalAugmentedGeneration` | `retrieval-augmented_generation` | `skos:closeMatch` |
| `SemanticSearch` | `semantic_search` | `skos:closeMatch` |

`skos:exactMatch` is retained only for the two local `ResearchTopic` concepts whose labels and
scope match the corresponding CSO research areas. `QuestionAnswering` is modeled locally as a
`Task`, while `RetrievalAugmentedGeneration` and `SemanticSearch` are modeled as `Method`;
their CSO resources are research topics. They therefore use the weaker `skos:closeMatch`.
Project-specific implementation concepts are intentionally left unmapped until an equivalent
CSO topic is verified. This avoids asserting unsupported equivalence.

The five URIs were checked against the CSO 3.5 content-negotiation endpoints on 03/10/2026.
This review also corrected the RAG URI from the nonexistent
`retrieval_augmented_generation` resource to the official
`retrieval-augmented_generation` resource.

Sources:

- CSO Portal: https://cso.kmi.open.ac.uk/
- CSO downloads and releases: https://cso.kmi.open.ac.uk/downloads
- CSO data model and URI documentation: https://cso.kmi.open.ac.uk/about
- License: CC BY 4.0

The project stores only outbound mapping links. It does not copy or redistribute the full CSO
dataset.
