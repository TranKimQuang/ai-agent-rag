# Development concept candidate audit

This audit only uses queries from the development split that received no concept. It does not inspect validation or final-test retrieval results.

## Summary

- Uncovered queries: **65**
- Near threshold: **3**
- Weak existing match: **27**
- Vocabulary gap or generic question: **35**
- Unexpected candidate above threshold: **0**

The categories are triage labels, not automatic gold labels. Candidates must be accepted or rejected manually before changing the ontology or threshold.

## Candidate queue

| Category | Top score | Top candidate | Query | Gold evidence concepts |
|---|---:|---|---|---|
| near_threshold | 0.6024 | PhraseBasedMachineTranslation | Which language directions are machine translation systems of WMT evaluated on? | — |
| near_threshold | 0.5834 | ROUGE | What evaluation metrics were used? | ConvolutionalNeuralNetwork |
| near_threshold | 0.5593 | LanguageModel | What programming language is target language? | ParallelCorpus |
| weak_existing_match | 0.5402 | MorphologicalTokenization | How does morphological analysis differ from morphological inflection? | — |
| weak_existing_match | 0.5322 | LanguageModel | What languages are considered? | — |
| weak_existing_match | 0.5318 | HashtagPrediction | What benchmark datasets are used for the link prediction task? | — |
| weak_existing_match | 0.5177 | ROUGE | What metrics are used to benchmark the results? | LongShortTermMemory |
| weak_existing_match | 0.5075 | MachineLearning | How does the context-aware variational autoencoder learn event background information? | — |
| weak_existing_match | 0.5018 | ROUGE | How do they measure the diversity of inferences? | — |
| weak_existing_match | 0.4928 | DatasetBias | What are the characteristics of the dataset? | — |
| weak_existing_match | 0.4880 | MorphologicalTokenization | What model do they use to classify phonetic segments?  | ConvolutionalNeuralNetwork, NeuralNetwork |
| weak_existing_match | 0.4707 | ImageCaptioning | What are state-of-the art models for this task? | — |
| weak_existing_match | 0.4654 | SentimentAnalysis | What language is the Twitter content in? | — |
| weak_existing_match | 0.4454 | EntityLinking | What are their results on the entity recognition task? | — |
| weak_existing_match | 0.4435 | MultitaskLearning | What task-specific features are used? | — |
| weak_existing_match | 0.4424 | ROUGE | What kind of corpus-based features are taken into account? | NaturalLanguageProcessing |
| weak_existing_match | 0.4395 | DatasetBias | How do they select monotonicity facts? | — |
| weak_existing_match | 0.4391 | LanguageModel | What type of models are used for classification? | ConvolutionalNeuralNetwork, NeuralNetwork |
| weak_existing_match | 0.4382 | WordEmbedding | How does soft contextual data augmentation work? | LanguageModel |
| weak_existing_match | 0.4346 | DatasetBias | What dataset do they use? | ParallelCorpus |
| weak_existing_match | 0.4321 | LanguageModel | what are the methods they compare with in the korean-english dataset? | — |
| weak_existing_match | 0.4232 | ROUGE | What additional techniques could be incorporated to further improve accuracy? | WordEmbedding |
| weak_existing_match | 0.4197 | ROUGE | Do they perform manual evaluation? | — |
| weak_existing_match | 0.4181 | LabelPropagation | What feedback labels are used? | — |
| weak_existing_match | 0.4159 | ROUGE | What is result of their attention distribution analysis? | — |
| weak_existing_match | 0.4093 | TransferLearning | How does muli-agent dual learning work? | — |
| weak_existing_match | 0.4086 | ROUGE | What automatic metrics are used to measure performance of the system? | — |
| weak_existing_match | 0.4065 | TextSummarization | How was annotation done? | TransferLearning |
| weak_existing_match | 0.4063 | AuthorProfiling | What simulations are performed by the authors to validate their approach? | — |
| weak_existing_match | 0.4032 | ROUGE | By how much do they improve the accuracy of inferences over state-of-the-art methods? | — |
| vocabulary_gap_or_generic_question | 0.3997 | ROUGE | What are the baselines? | — |
| vocabulary_gap_or_generic_question | 0.3983 | ReciprocalRankFusion | What are 3 novel fusion techniques that are proposed? | MultitaskLearning |
| vocabulary_gap_or_generic_question | 0.3901 | HiddenMarkovModel | What baseline models are offered? | LanguageModel, LongShortTermMemory |
| vocabulary_gap_or_generic_question | 0.3898 | HiddenMarkovModel | What is the results of multimodal compared to unimodal models? | LongShortTermMemory |
| vocabulary_gap_or_generic_question | 0.3806 | DiscourseAnalysis | Do they propose any further additions that could be made to improve generalisation to unseen speakers? | — |
| vocabulary_gap_or_generic_question | 0.3794 | ROUGE | What was the criteria for human evaluation? | — |
| vocabulary_gap_or_generic_question | 0.3657 | CooccurrenceMatrix | How many instances does their dataset have? | — |
| vocabulary_gap_or_generic_question | 0.3654 | ROUGE | What is result of their Principal Component Analysis? | NeuralMachineTranslation |
| vocabulary_gap_or_generic_question | 0.3619 | HiddenMarkovModel | How better does HAKE model peform than state-of-the-art methods? | MeanReciprocalRank |
| vocabulary_gap_or_generic_question | 0.3612 | DatasetBias | What is author's opinion on why current multimodal models cannot outperform models analyzing only text? | ConvolutionalNeuralNetwork, NeuralNetwork |
| vocabulary_gap_or_generic_question | 0.3602 | MultitaskLearning | What are the architectures used for the three tasks? | — |
| vocabulary_gap_or_generic_question | 0.3531 | PyramidMethod | What is task success rate achieved?  | — |
| vocabulary_gap_or_generic_question | 0.3493 | HiddenMarkovModel | Which models do they use as baselines on the Atomic dataset? | RecurrentNeuralNetwork |
| vocabulary_gap_or_generic_question | 0.3472 | LexicalDiversity | what genre was the most difficult to classify? | — |
| vocabulary_gap_or_generic_question | 0.3407 | QuestionAnswering | Which language family does Chatino belong to? | — |
| vocabulary_gap_or_generic_question | 0.3400 | NeuralMachineTranslation | How do they combine MonaLog with BERT? | LanguageModel, NaturalLanguageInference |
| vocabulary_gap_or_generic_question | 0.3374 | TopicModeling | What models do they propose? | ConvolutionalNeuralNetwork, RecurrentNeuralNetwork |
| vocabulary_gap_or_generic_question | 0.3332 | CausalityExtraction | what pitfalls are mentioned in the paper? | NeuralMachineTranslation |
| vocabulary_gap_or_generic_question | 0.3331 | LatentDirichletAllocation | Which six domains are covered in the dataset? | — |
| vocabulary_gap_or_generic_question | 0.3173 | EvidenceF1 | Do they compare against Noraset et al. 2017? | NeuralNetwork, RecurrentNeuralNetwork |
| vocabulary_gap_or_generic_question | 0.3043 | DatasetBias | what were their experimental results in the low-resource dataset? | — |
| vocabulary_gap_or_generic_question | 0.3018 | HiddenMarkovModel | What system is used as baseline? | — |
| vocabulary_gap_or_generic_question | 0.2996 | MorphologicalTokenization | How are entities mapped onto polar coordinate system? | — |
| vocabulary_gap_or_generic_question | 0.2995 | DatasetBias | How large is the dataset? | — |
| vocabulary_gap_or_generic_question | 0.2990 | PyramidMethod | What additional techniques are incorporated? | LongShortTermMemory |
| vocabulary_gap_or_generic_question | 0.2915 | ComputationalSocialScience | What is the architecture of the system? | LongShortTermMemory, NeuralMachineTranslation, NeuralNetwork, RecurrentNeuralNetwork |
| vocabulary_gap_or_generic_question | 0.2902 | MultipleChoiceQuestionAnswering | How many papers are used in experiment? | — |
| vocabulary_gap_or_generic_question | 0.2708 | ParaphraseGeneration | What is a sememe? | — |
| vocabulary_gap_or_generic_question | 0.2661 | QuestionAnswering | Where did the real production data come from? | ConvolutionalNeuralNetwork |
| vocabulary_gap_or_generic_question | 0.2640 | LexicalDiversity | what amounts of size were used on german-english? | NeuralMachineTranslation |
| vocabulary_gap_or_generic_question | 0.2626 | LexicalDiversity | what genres do they songs fall under? | — |
| vocabulary_gap_or_generic_question | 0.2620 | CausalityExtraction | what is the source of the song lyrics? | — |
| vocabulary_gap_or_generic_question | 0.2494 | QASPER | What existing methods is SC-GPT compared to? | LongShortTermMemory |
| vocabulary_gap_or_generic_question | 0.2070 | PyramidMethod | What is the average number of turns per dialog? | — |
| vocabulary_gap_or_generic_question | 0.1184 | DatasetBias | Do they beat current state-of-the-art on SICK? | NaturalLanguageInference |

## Most frequent top candidates

| Concept | Queries |
|---|---:|
| ROUGE | 12 |
| DatasetBias | 7 |
| HiddenMarkovModel | 5 |
| LanguageModel | 4 |
| MorphologicalTokenization | 3 |
| PyramidMethod | 3 |
| LexicalDiversity | 3 |
| MultitaskLearning | 2 |
| QuestionAnswering | 2 |
| CausalityExtraction | 2 |
| PhraseBasedMachineTranslation | 1 |
| HashtagPrediction | 1 |
| MachineLearning | 1 |
| ImageCaptioning | 1 |
| SentimentAnalysis | 1 |
