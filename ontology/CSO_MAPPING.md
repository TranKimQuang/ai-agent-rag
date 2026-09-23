# CSO subset mapping

This project reuses a small, task-focused subset of the Computer Science Ontology (CSO)
instead of importing the full ontology. The mapping is aligned with CSO v3.5 and uses the
official topic URI pattern documented by the CSO Portal.

| Local concept | CSO topic | Mapping |
| --- | --- | --- |
| `InformationRetrieval` | `information_retrieval` | `skos:exactMatch` |
| `NaturalLanguageProcessing` | `natural_language_processing` | `skos:exactMatch` |
| `QuestionAnswering` | `question_answering` | `skos:exactMatch` |
| `RetrievalAugmentedGeneration` | `retrieval_augmented_generation` | `skos:exactMatch` |
| `SemanticSearch` | `semantic_search` | `skos:exactMatch` |

`skos:exactMatch` is used only where the local concept and CSO topic denote the same research
area. Project-specific implementation concepts are intentionally left unmapped until an
equivalent CSO topic is verified. This avoids asserting unsupported equivalence.

Sources:

- CSO Portal: https://cso.kmi.open.ac.uk/
- CSO downloads and releases: https://cso.kmi.open.ac.uk/downloads
- CSO data model and URI documentation: https://cso.kmi.open.ac.uk/about
- License: CC BY 4.0

The project stores only outbound mapping links. It does not copy or redistribute the full CSO
dataset.
