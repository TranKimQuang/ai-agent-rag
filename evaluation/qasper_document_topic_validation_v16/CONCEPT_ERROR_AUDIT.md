# Concept-linking error audit

- Dataset: `evaluation\qasper_document_topic_validation_v16\qasper_validation.json`
- Questions: **77**
- Usage policy: **locked_validation_analysis_only**

The groups below are descriptive triage labels, not automatic gold labels.

## Summary

| Group | Questions |
|---|---:|
| missing_relation_or_query_mismatch | 2 |
| missing_query_concept | 20 |
| missing_gold_concept | 14 |
| missing_query_and_gold_concepts | 38 |
| useful_relation | 3 |

## Review queue

| Group | Query concepts | Gold concepts | Query proposal | Evidence proposal | Question |
|---|---|---|---|---|---|
| missing_relation_or_query_mismatch | TextSummarization | MachineLearning | DatasetBias (0.5342) | MachineLearning (0.5300) | In what sense is data annotation similar to structured content analysis?  |
| missing_relation_or_query_mismatch | ROUGE | NaturalLanguageProcessing | ROUGE (0.6062) | ROUGE (0.3322) | What evaluation metric were used for presenting results?  |
| missing_query_concept | — | LongShortTermMemory | MachineReadingComprehension (0.3967) | NeuralMachineTranslation (0.4820) | What three machine architectures are analyzed? |
| missing_query_concept | — | ConvolutionalNeuralNetwork | GrammaticalErrorCorrection (0.4578) | EvidenceF1 (0.3978) | What is improvement in accuracy for short Jokes in relation other types of jokes? |
| missing_query_concept | — | LongShortTermMemory, WordEmbedding | DatasetBias (0.3584) | LatentDirichletAllocation (0.4633) | How big is slot filing dataset? |
| missing_query_concept | — | Crowdsourcing, NaturalLanguageProcessing, SentimentAnalysis | ROUGE (0.4306) | Crowdsourcing (0.4957) | What are the key issues around whether the gold standard data produced in such an annotation is reliable?  |
| missing_query_concept | — | MeanReciprocalRank | ROUGE (0.5802) | ROUGE (0.4832) | What evaluation metrics were used in the experiment? |
| missing_query_concept | — | MachineReadingComprehension | HiddenMarkovModel (0.4584) | MemoryNetwork (0.4783) | What are previously reported models? |
| missing_query_concept | — | LongShortTermMemory, WordEmbedding | ROUGE (0.5358) | LatentDirichletAllocation (0.4633) | What metris are used for evaluation? |
| missing_query_concept | — | NeuralNetwork | DiscourseAnalysis (0.4345) | SupervisedLearning (0.4243) | Can their method of creating more informative visuals be applied to tasks other than turn taking in conversations? |
| missing_query_concept | — | LongShortTermMemory, WordEmbedding | ROUGE (0.3590) | ROUGE (0.4964) | What is the baseline? |
| missing_query_concept | — | LongShortTermMemory, MachineReadingComprehension, QuestionAnswering | ROUGE (0.4123) | RetrievalAugmentedGeneration (0.5147) | What baseline algorithms were presented? |
| missing_query_concept | — | ConvolutionalNeuralNetwork, LongShortTermMemory, NaturalLanguageProcessing, NeuralNetwork | HiddenMarkovModel (0.3820) | MemoryNetwork (0.4872) | What model did they use? |
| missing_query_concept | — | BeamSearch, NeuralNetwork, TextSummarization | LatentDirichletAllocation (0.3576) | TextSummarization (0.5000) | What is the effectiveness plan generation? |
| missing_query_concept | — | BeamSearch | ROUGE (0.5489) | ROUGE (0.5139) | What metrics are used for automatic evaluation? |
| missing_query_concept | — | QuestionAnswering | MultilingualNaturalLanguageProcessing (0.4611) | DistributionalSemantics (0.4313) | What multimodality is available in the dataset? |
| missing_query_concept | — | LanguageModel, LongShortTermMemory, NaturalLanguageInference, NaturalLanguageProcessing | HiddenMarkovModel (0.4077) | BidirectionalLanguageModel (0.5167) | Which models were compared? |
| missing_query_concept | — | TextSummarization | CooccurrenceMatrix (0.4896) | TextSummarization (0.6048) | What features of the document are integrated into vectors of every sentence? |
| missing_query_concept | — | NeuralNetwork | MorphologicalTokenization (0.3320) | DiscourseAnalysis (0.5442) | What are the nine types? |
| missing_query_concept | — | NeuralNetwork | LanguageModel (0.3986) | SentimentAnalysis (0.5332) | What is the architecture of their model? |
| missing_query_concept | — | LanguageModel | LanguageModel (0.4631) | MachineReadingComprehension (0.3445) | Which model generalized the best? |
| missing_query_concept | — | ConvolutionalNeuralNetwork, LongShortTermMemory | DistantSupervision (0.4359) | HiddenMarkovModel (0.4490) | Why does proposed term help to avoid posterior collapse? |
| missing_gold_concept | DatasetBias | — | DatasetBias (0.5291) | DatasetBias (0.4384) | What datasets do they use? |
| missing_gold_concept | ROUGE | — | ROUGE (0.5334) | ROUGE (0.4964) | What are overall baseline results on new this new task? |
| missing_gold_concept | NeuralMachineTranslation | — | NeuralMachineTranslation (0.5732) | ConvolutionalNeuralNetwork (0.4171) | What neural configurations are explored? |
| missing_gold_concept | SemanticRoleInduction | — | SemanticRoleInduction (0.5463) | SemanticRoleInduction (0.5696) | What non-contextual properties do they refer to? |
| missing_gold_concept | TextSummarization | — | TextSummarization (0.5201) | ROUGE (0.4732) | How is faithfulness of the resulting text evaluated? |
| missing_gold_concept | NaturalLanguageProcessing | — | DistantSupervision (0.5337) | LanguageModel (0.5399) | How they model style as a suite of low-level linguistic controls, such as frequency of pronouns, prepositions, and subordinate clause constructions? |
| missing_gold_concept | NeuralMachineTranslation | — | NeuralMachineTranslation (0.5747) | SupervisedLearning (0.4571) | How is neural planning component trained? |
| missing_gold_concept | TextSummarization | — | TextSummarization (0.5003) | TextSummarization (0.4556) | At what text unit/level were documents processed? |
| missing_gold_concept | LanguageModel | — | MultipleChoiceQuestionAnswering (0.5569) | MultipleChoiceQuestionAnswering (0.3665) | What approach did previous models use for multi-span questions? |
| missing_gold_concept | QuestionAnswering | — | QuestionAnswering (0.5826) | QuestionAnswering (0.5296) | Do they survey visual question generation work? |
| missing_gold_concept | QuestionAnswering | — | QuestionAnswering (0.6296) | QASPER (0.4152) | How authors justify that question answering dataset presented is realistic? |
| missing_gold_concept | MultitaskLearning | — | MultitaskLearning (0.6680) | SemanticRoleInduction (0.5292) | How does their model utilize contextual information for each work in the given sentence in a multi-task setting? setting? |
| missing_gold_concept | QuestionAnswering | — | QuestionAnswering (0.6296) | QASPER (0.4152) | How big is new question answering dataset? |
| missing_gold_concept | AuthorProfiling | — | AuthorProfiling (0.5368) | HiddenMarkovModel (0.4649) | How does explicit constraint on the KL divergence term that authors propose looks like? |
| missing_query_and_gold_concepts | — | — | MultipleChoiceQuestionAnswering (0.2790) | MachineLearning (0.4046) | What is the source of the triples? |
| missing_query_and_gold_concepts | — | — | AuthorProfiling (0.4368) | TransferLearning (0.4015) | How do they gather human reviews? |
| missing_query_and_gold_concepts | — | — | MorphologicalTokenization (0.2379) | ROUGE (0.3780) | Are the Transformers masked? |
| missing_query_and_gold_concepts | — | — | LanguageModel (0.4632) | MultitaskLearning (0.4405) | How better is accuracy of new model compared to previously reported models? |
| missing_query_and_gold_concepts | — | — | TextSummarization (0.4830) | TextSummarization (0.4508) | What are the core best practices of structured content analysis? |
| missing_query_and_gold_concepts | — | — | DynamicMemoryNetwork (0.3840) | ComputationalSocialScience (0.3523) | How does Progressive Dynamic Hurdles work? |
| missing_query_and_gold_concepts | — | — | SupervisedLearning (0.5492) | SupervisedLearning (0.5031) | What learning paradigms do they cover in this survey? |
| missing_query_and_gold_concepts | — | — | TextSummarization (0.4797) | NaturalLanguageProcessing (0.5046) | Does pre-training on general text corpus improve performance? |
| missing_query_and_gold_concepts | — | — | QASPER (0.4056) | TextSummarization (0.4751) | What dataset is used for this task? |
| missing_query_and_gold_concepts | — | — | TextSummarization (0.4906) | CooccurrenceMatrix (0.3739) | How is fluency of generated text evaluated? |
| missing_query_and_gold_concepts | — | — | MultipleChoiceQuestionAnswering (0.5853) | MorphologicalTokenization (0.3708) | How they use sequence tagging to answer multi-span questions? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.5300) | AuthorProfiling (0.4650) | How they perform manual evaluation, what is criteria? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.5016) | ROUGE (0.4964) | What metrics are used in evaluation of this task? |
| missing_query_and_gold_concepts | — | — | TextSummarization (0.3855) | WordEmbedding (0.4516) | How are typing hints suggested? |
| missing_query_and_gold_concepts | — | — | LanguageModel (0.4632) | EvidenceF1 (0.5207) | How better is proposed model compared to baselines? |
| missing_query_and_gold_concepts | — | — | SupervisedLearning (0.3798) | ROUGE (0.4240) | What kind of instructional videos are in the dataset? |
| missing_query_and_gold_concepts | — | — | PyramidMethod (0.3730) | ROUGE (0.5153) | Is new approach tested against state of the art? |
| missing_query_and_gold_concepts | — | — | AuthorProfiling (0.3926) | InformationRetrieval (0.3254) | What type of documents are supported by the annotation platform? |
| missing_query_and_gold_concepts | — | — | GrammaticalErrorCorrection (0.3987) | HiddenMarkovModel (0.3243) | Which part of the joke is more important in humor? |
| missing_query_and_gold_concepts | — | — | GrammaticalErrorCorrection (0.3741) | RevisionDetection (0.3837) | How they evaluate if joke is humorous or not? |
| missing_query_and_gold_concepts | — | — | PyramidMethod (0.4140) | ROUGE (0.4436) | How is this problem evaluated? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.4554) | TopicModeling (0.4495) | Is this style generator compared to some baseline? |
| missing_query_and_gold_concepts | — | — | LatentDirichletAllocation (0.3135) | SemanticRoleInduction (0.5696) | What are their proposed features? |
| missing_query_and_gold_concepts | — | — | LanguageModel (0.4148) | MultipleChoiceQuestionAnswering (0.3808) | What is the performance of proposed model on entire DROP dataset? |
| missing_query_and_gold_concepts | — | — | MultipleChoiceQuestionAnswering (0.5323) | MultipleChoiceQuestionAnswering (0.3665) | What is the previous model that attempted to tackle multi-span questions as a part of its design? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.3527) | SpamDetection (0.4068) | What is the size of the dataset? |
| missing_query_and_gold_concepts | — | — | PyramidMethod (0.3668) | ComputationalSocialScience (0.3523) | what is the proposed Progressive Dynamic Hurdles method? |
| missing_query_and_gold_concepts | — | — | MachineLearning (0.2632) | DatasetBias (0.4403) | What patterns were discovered from the stories? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.2407) | SentimentAnalysis (0.5201) | How is speed measured? |
| missing_query_and_gold_concepts | — | — | DistantSupervision (0.4551) | TextSummarization (0.4556) | Was the structure of regulatory filings exploited when training the model?  |
| missing_query_and_gold_concepts | — | — | WordEmbedding (0.4838) | LanguageModel (0.5007) | How they know what are content words? |
| missing_query_and_gold_concepts | — | — | LanguageModel (0.5240) | TransferLearning (0.4015) | Do they explain model predictions solely on attention weights? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.4350) | EvidenceF1 (0.5207) | What are the baselines? |
| missing_query_and_gold_concepts | — | — | CausalityExtraction (0.4665) | DatasetBias (0.3906) | How strong is negative correlation between compound divergence and accuracy in performed experiment? |
| missing_query_and_gold_concepts | — | — | MorphologicalTokenization (0.5333) | MultipleChoiceQuestionAnswering (0.4480) | What are results of comparison between novel method to other approaches for creating compositional generalization benchmarks? |
| missing_query_and_gold_concepts | — | — | LatentDirichletAllocation (0.4027) | HiddenMarkovModel (0.3622) | What different properties of the posterior distribution are explored in the paper? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.4502) | SentimentAnalysis (0.3319) | What kind of humor they have evaluated? |
| missing_query_and_gold_concepts | — | — | KeywordSearch (0.5977) | MemoryNetwork (0.3982) | What is in the model search space? |
| useful_relation | DatasetBias | DistributionalSemantics, NaturalLanguageInference | DatasetBias (0.5219) | NaturalLanguageInference (0.5431) | Which datasets were used? |
| useful_relation | MachineLearning | InformationRetrieval, MachineLearning | MachineLearning (0.8170) | RetrievalAugmentedGeneration (0.4001) | How were the machine learning papers from ArXiv sampled? |
| useful_relation | QuestionAnswering | ImageCaptioning, QuestionAnswering, TextSummarization | QuestionAnswering (0.5729) | QuestionAnswering (0.5286) | What are all the input modalities considered in prior work in question generation? |
