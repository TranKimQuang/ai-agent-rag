# Concept-linking error audit

- Dataset: `evaluation\qasper_concept_labeling_development_v17\qasper_development.json`
- Questions: **112**
- Usage policy: **development_labeling**

The groups below are descriptive triage labels, not automatic gold labels.

## Summary

| Group | Questions |
|---|---:|
| missing_relation_or_query_mismatch | 11 |
| missing_query_concept | 39 |
| missing_gold_concept | 12 |
| missing_query_and_gold_concepts | 43 |
| useful_relation | 7 |

## Review queue

| Group | Query concepts | Gold concepts | Query proposal | Evidence proposal | Question |
|---|---|---|---|---|---|
| missing_relation_or_query_mismatch | NaturalLanguageProcessing | NeuralNetwork | NaturalLanguageProcessing (0.7181) | SemanticRoleInduction (0.5316) | How is state to learn and complete tasks represented via natural language? |
| missing_relation_or_query_mismatch | LabelPropagation | SentimentAnalysis | LabelPropagation (0.5994) | SentimentAnalysis (0.6234) | How many label options are there in the multi-label task? |
| missing_relation_or_query_mismatch | MultilingualNaturalLanguageProcessing | NeuralMachineTranslation | MultilingualNaturalLanguageProcessing (0.6462) | NaturalLanguageProcessing (0.4433) | What are multilingual models that were outperformed in performed experiment? |
| missing_relation_or_query_mismatch | LanguageModel | TransferLearning | LanguageModel (0.6068) | TransferLearning (0.5157) | Is pivot language used in experiments English or some other language? |
| missing_relation_or_query_mismatch | SemanticRoleInduction | TextSummarization | SemanticRoleInduction (0.7878) | TextSummarization (0.4962) | Is it expected to have speaker role, semantic slot and dialog domain annotations in real world datasets? |
| missing_relation_or_query_mismatch | LanguageModel | NeuralMachineTranslation, WordSegmentation | LanguageModel (0.6164) | WordSegmentation (0.6353) | What are the different bilingual models employed? |
| missing_relation_or_query_mismatch | LanguageModel | InformationRetrieval, LatentDirichletAllocation | LanguageModel (0.7117) | SemanticSearch (0.5088) | By how much does their system outperform the lexicon-based models? |
| missing_relation_or_query_mismatch | ROUGE | BeamSearch, LanguageModel, LongShortTermMemory, NeuralMachineTranslation, WordEmbedding | ROUGE (0.5905) | LanguageModel (0.5351) | Did they use other evaluation metrics? |
| missing_relation_or_query_mismatch | LexicalDiversity, ReciprocalRankFusion | CooccurrenceMatrix, TextSummarization | LexicalDiversity (0.6433) | CooccurrenceMatrix (0.5021) | Do they quantitavely or qualitatively evalute the output of their low-rank approximation to verify the grouping of lexical items? |
| missing_relation_or_query_mismatch | SemanticRoleInduction | TextSummarization | SemanticRoleInduction (0.7878) | SemanticRoleInduction (0.4824) | How does SPNet utilize additional speaker role, semantic slot and dialog domain annotations? |
| missing_relation_or_query_mismatch | ParallelCorpus | BeamSearch, LanguageModel, NeuralMachineTranslation, WordEmbedding | ParallelCorpus (0.8511) | MemoryNetwork (0.4888) | What parallel corpus did they use? |
| missing_query_concept | — | InformationRetrieval | CooccurrenceMatrix (0.4438) | SupervisedLearning (0.6026) | Which paired corpora did they use in the other experiment? |
| missing_query_concept | — | NeuralMachineTranslation, RecurrentNeuralNetwork | PhraseBasedMachineTranslation (0.5430) | NeuralMachineTranslation (0.4653) | What kind of encoders are used for the parsed source sentence? |
| missing_query_concept | — | LongShortTermMemory, NeuralNetwork | DatasetBias (0.4800) | MemoryNetwork (0.4379) | Are the unobserved samples from the same distribution as the training data? |
| missing_query_concept | — | TransferLearning | LanguageModel (0.4707) | TransferLearning (0.5019) | Are experiments performed with any other pair of languages, how did proposed method perform compared to other models? |
| missing_query_concept | — | SentimentAnalysis | DatasetBias (0.5143) | LanguageModel (0.4511) | What dataset do they use? |
| missing_query_concept | — | NaturalLanguageProcessing | LanguageModel (0.4789) | ParallelCorpus (0.4819) | What languages are explored in this paper? |
| missing_query_concept | — | LanguageModel | ROUGE (0.3755) | BidirectionalLanguageModel (0.4333) | Does the paper report the accuracy of the model? |
| missing_query_concept | — | HiddenMarkovModel | LanguageModel (0.3741) | NeuralNetwork (0.4722) | Which architecture is their best model? |
| missing_query_concept | — | SentimentAnalysis | NaturalLanguageProcessing (0.3764) | LanguageModel (0.4511) | Is the data all in Vietnamese? |
| missing_query_concept | — | InformationRetrieval | SentimentAnalysis (0.4898) | ROUGE (0.4973) | How many comments were used? |
| missing_query_concept | — | WordEmbedding | ConvolutionalNeuralNetwork (0.4728) | EvidenceF1 (0.3636) | What is new state-of-the-art performance on CoNLL-2009 dataset? |
| missing_query_concept | — | NeuralNetwork | ROUGE (0.3789) | MemoryNetwork (0.4505) | How do they measure model size? |
| missing_query_concept | — | WordEmbedding | ComputationalSocialScience (0.2621) | ROUGE (0.5012) | What experiments are presented? |
| missing_query_concept | — | LanguageModel, LongShortTermMemory, NeuralNetwork | HiddenMarkovModel (0.3635) | ROUGE (0.3976) | Which of the model yields the best performance? |
| missing_query_concept | — | ConvolutionalNeuralNetwork, NeuralNetwork | HiddenMarkovModel (0.3929) | DiscourseAnalysis (0.4099) | How do they prevent the model complexity increasing with the increased number of slots? |
| missing_query_concept | — | Word2Vec, WordEmbedding | WordEmbedding (0.4075) | WordEmbedding (0.5554) | What embeddings do they use? |
| missing_query_concept | — | CooccurrenceMatrix, LexicalDiversity, TextSummarization, WordEmbedding | ProbabilisticContextFreeGrammar (0.4310) | TextSummarization (0.6594) | What do they constrain using integer linear programming? |
| missing_query_concept | — | Word2Vec, WordEmbedding | PyramidMethod (0.3554) | ROUGE (0.4471) | What conclusions are drawn from these experiments? |
| missing_query_concept | — | MachineLearning, MultitaskLearning, NaturalLanguageProcessing, NeuralNetwork, QuestionAnswering, Word2Vec, WordEmbedding | WordEmbedding (0.4048) | WordEmbedding (0.6979) | What is specific about the specific embeddings? |
| missing_query_concept | — | Word2Vec, WordEmbedding | WordEmbedding (0.4920) | WordEmbedding (0.6979) | What embedding algorithm is used to build the embeddings? |
| missing_query_concept | — | LanguageModel | InformationRetrieval (0.4793) | SupervisedLearning (0.3794) | Do they explore how much traning data is needed for which magnitude of improvement for WER?  |
| missing_query_concept | — | ConvolutionalNeuralNetwork, NeuralNetwork | MemoryNetwork (0.4802) | DiscourseAnalysis (0.4099) | What network architecture do they use for SIM? |
| missing_query_concept | — | LanguageModel, LongShortTermMemory, NeuralNetwork | ImageCaptioning (0.3854) | ROUGE (0.4670) | What is the performance of the models on the tasks? |
| missing_query_concept | — | LongShortTermMemory | OpenInformationExtraction (0.2460) | DatasetBias (0.4378) | Do they use dropout? |
| missing_query_concept | — | LongShortTermMemory | MultipleChoiceQuestionAnswering (0.5459) | MemoryNetwork (0.4055) | Do they use multi-attention heads? |
| missing_query_concept | — | MultilingualNaturalLanguageProcessing | DatasetBias (0.5445) | MultilingualNaturalLanguageProcessing (0.4953) | What datasets are used? |
| missing_query_concept | — | LanguageModel | ROUGE (0.5033) | BidirectionalLanguageModel (0.4333) | Is the model evaluated against any baseline? |
| missing_query_concept | — | LongShortTermMemory, RecurrentNeuralNetwork | NaturalLanguageProcessing (0.5206) | LongShortTermMemory (0.5435) | How do they get the formal languages? |
| missing_query_concept | — | LanguageModel, NeuralNetwork, RecurrentNeuralNetwork, WordEmbedding | HiddenMarkovModel (0.4105) | DiscourseAnalysis (0.5463) | How many models were used? |
| missing_query_concept | — | ConvolutionalNeuralNetwork, ROUGE, TextSummarization | ROUGE (0.5258) | ROUGE (0.5191) | What metric was used in the evaluation step? |
| missing_query_concept | — | NeuralMachineTranslation, RecurrentNeuralNetwork | MachineReadingComprehension (0.3819) | NeuralMachineTranslation (0.4659) | Whas is the performance drop of their model when there is no parsed input? |
| missing_query_concept | — | ConvolutionalNeuralNetwork, LongShortTermMemory, MachineLearning, SentimentAnalysis, WordEmbedding | WordEmbedding (0.4307) | LanguageModel (0.5560) | What classifier do they use? |
| missing_query_concept | — | WordEmbedding | ConvolutionalNeuralNetwork (0.4728) | EvidenceF1 (0.3636) | How big is improvement over the old  state-of-the-art performance on CoNLL-2009 dataset? |
| missing_query_concept | — | LongShortTermMemory | TextSummarization (0.4794) | NaturalLanguageProcessing (0.5034) | Do they perform some annotation? |
| missing_query_concept | — | LongShortTermMemory, NeuralNetwork, RecurrentNeuralNetwork | SupervisedLearning (0.4114) | HiddenMarkovModel (0.4802) | What training settings did they try? |
| missing_query_concept | — | LanguageModel | LanguageModel (0.4199) | MultilingualNaturalLanguageProcessing (0.5206) | How is the performance of the model evaluated? |
| missing_query_concept | — | LongShortTermMemory, NeuralNetwork | LanguageModel (0.4081) | LanguageModel (0.4996) | Do they train their own RE model? |
| missing_query_concept | — | ConvolutionalNeuralNetwork, LanguageModel, NeuralNetwork, TextSummarization | ROUGE (0.4310) | TextSummarization (0.5256) | What were the baselines? |
| missing_query_concept | — | ConvolutionalNeuralNetwork | SupervisedLearning (0.4354) | TextSummarization (0.5282) | What does the data cleaning and filtering process consist of? |
| missing_gold_concept | ConvolutionalNeuralNetwork | — | ConvolutionalNeuralNetwork (0.6167) | ProbabilisticContextFreeGrammar (0.4910) | How many convolutional layers does their model have? |
| missing_gold_concept | OpenInformationExtraction | — | OpenInformationExtraction (0.5734) | HybridSearch (0.4756) | What compleentary PIE extraction methods are used to increase reliability further? |
| missing_gold_concept | SupervisedLearning | — | SupervisedLearning (0.5716) | ROUGE (0.4504) | Do any of the evaluations show that adversarial learning improves performance in at least two different language families? |
| missing_gold_concept | NaturalLanguageProcessing | — | NaturalLanguageProcessing (0.5983) | LanguageModel (0.4400) | What languages do they experiment on? |
| missing_gold_concept | SupervisedLearning | — | WordSegmentation (0.5925) | SupervisedLearning (0.4223) | Does adversarial learning have stronger performance gains for text classification, or for NER? |
| missing_gold_concept | LanguageModel | — | LanguageModel (0.7117) | LatentDirichletAllocation (0.3878) | Which lexicon-based models did they compare with? |
| missing_gold_concept | WordEmbedding | — | WordEmbedding (0.7506) | WordEmbedding (0.5484) | Which word embeddings do they use to represent medical visits? |
| missing_gold_concept | ROUGE | — | ROUGE (0.5862) | PyramidMethod (0.4738) | What evaluation metrics do they use? |
| missing_gold_concept | AuthorProfiling | — | AuthorProfiling (0.5623) | DistributionalSemantics (0.4207) | What different approaches of encoding syntactic information authors present? |
| missing_gold_concept | TextSummarization | — | TextSummarization (0.6154) | MemoryNetwork (0.4825) | How do they combine text representations with the knowledge graph embeddings? |
| missing_gold_concept | DistributionalSemantics | — | DistributionalSemantics (0.6443) | DistributionalSemantics (0.5046) | Which distributional methods did they consider? |
| missing_gold_concept | TopicModeling | — | TopicModeling (0.8089) | ROUGE (0.3652) | Do they build one model per topic or on all topics? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.4009) | RetrievalAugmentedGeneration (0.4901) | Are PIEs extracted automatically subjected to human evaluation? |
| missing_query_and_gold_concepts | — | — | TransferLearning (0.4253) | DatasetBias (0.4433) | How do they model travel behavior? |
| missing_query_and_gold_concepts | — | — | PyramidMethod (0.2968) | ROUGE (0.3672) | What features do they experiment with? |
| missing_query_and_gold_concepts | — | — | DiscourseAnalysis (0.3918) | DiscourseAnalysis (0.4133) | How do you establish the ground truth of who won a debate? |
| missing_query_and_gold_concepts | — | — | SupervisedLearning (0.2365) | LatentDirichletAllocation (0.3626) | What is private dashboard? |
| missing_query_and_gold_concepts | — | — | HiddenMarkovModel (0.3307) | SupervisedLearning (0.3785) | What did they pretrain the model on? |
| missing_query_and_gold_concepts | — | — | SemanticSearch (0.4333) | LatentDirichletAllocation (0.4607) | How big PIE datasets are obtained from dictionaries? |
| missing_query_and_gold_concepts | — | — | Crowdsourcing (0.3615) | DiscourseAnalysis (0.4531) | Who is the crowd in these experiments? |
| missing_query_and_gold_concepts | — | — | DistantSupervision (0.4124) | HashtagPrediction (0.4439) | How was performance of previously proposed rules at very large scale? |
| missing_query_and_gold_concepts | — | — | ParallelCorpus (0.5076) | SupervisedLearning (0.3785) | What unlabeled corpus did they use? |
| missing_query_and_gold_concepts | — | — | MachineLearning (0.3667) | MultilingualNaturalLanguageProcessing (0.4700) | How is the data automatically generated? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.4534) | ROUGE (0.4004) | Which two datasets is the system tested on? |
| missing_query_and_gold_concepts | — | — | OpenInformationExtraction (0.5481) | ParallelCorpus (0.4813) | What dictionaries are used for automatic extraction of PIEs? |
| missing_query_and_gold_concepts | — | — | HiddenMarkovModel (0.4582) | DistributionalSemantics (0.2691) | What new model is proposed for binomial lists? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.4676) | SentimentAnalysis (0.5381) | What other relations were found in the datasets? |
| missing_query_and_gold_concepts | — | — | Crowdsourcing (0.3712) | LatentDirichletAllocation (0.3626) | What is public dashboard? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.3417) | LanguageModel (0.4400) | How big are the datasets? |
| missing_query_and_gold_concepts | — | — | DistantSupervision (0.3922) | TextSummarization (0.4466) | How is order of binomials tracked across time? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.4396) | MachineReadingComprehension (0.4386) | What was their perplexity score? |
| missing_query_and_gold_concepts | — | — | TransferLearning (0.4032) | TransferLearning (0.4483) | How do their train their embeddings? |
| missing_query_and_gold_concepts | — | — | TextSummarization (0.4144) | NaturalLanguageProcessing (0.5034) | Do all the instances contain code-switching? |
| missing_query_and_gold_concepts | — | — | LanguageModel (0.2186) | RecurrentNeuralNetwork (0.4078) | How big is their model? |
| missing_query_and_gold_concepts | — | — | AuthorProfiling (0.4623) | SemanticRoleInduction (0.4412) | What experiments authors perform? |
| missing_query_and_gold_concepts | — | — | LexicalDiversity (0.5150) | ROUGE (0.4207) | Do they explore similarity of texts across different doctors? |
| missing_query_and_gold_concepts | — | — | RetrievalAugmentedGeneration (0.3289) | CooccurrenceMatrix (0.4130) | Are there any new finding in analasys of trinomials that was not present binomials? |
| missing_query_and_gold_concepts | — | — | WordSegmentation (0.4444) | CooccurrenceMatrix (0.3582) | Which clustering technique do they use on partients' visits texts? |
| missing_query_and_gold_concepts | — | — | LexicalDiversity (0.4616) | TextSummarization (0.4466) | What types of various community texts have been investigated for exploring global structure of binomials? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.5390) | MachineReadingComprehension (0.4052) | Which unlabeled data do they pretrain with? |
| missing_query_and_gold_concepts | — | — | ParallelCorpus (0.4334) | ParallelCorpus (0.3786) | How was the KGR10 corpus created? |
| missing_query_and_gold_concepts | — | — | HiddenMarkovModel (0.4671) | MemoryNetwork (0.4912) | How is their model different from BERT? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.5143) | LatentDirichletAllocation (0.4634) | What dataset do they use? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.4970) | MeanReciprocalRank (0.4597) | Which benchmark datasets are used? |
| missing_query_and_gold_concepts | — | — | DatasetBias (0.5648) | PyramidMethod (0.2619) | What datasets are used for evaluation? |
| missing_query_and_gold_concepts | — | — | AuthorProfiling (0.3197) | DatasetBias (0.3762) | How many articles did they have? |
| missing_query_and_gold_concepts | — | — | NaturalLanguageProcessing (0.3264) | SupervisedLearning (0.3352) | What normalization techniques are mentioned? |
| missing_query_and_gold_concepts | — | — | MultitaskLearning (0.3678) | MeanReciprocalRank (0.4597) | What hypernymy tasks do they study? |
| missing_query_and_gold_concepts | — | — | AuthorProfiling (0.3308) | DiscourseAnalysis (0.4531) | Who are the experts? |
| missing_query_and_gold_concepts | — | — | OpenInformationExtraction (0.5091) | DiscourseAnalysis (0.4639) | How does the ensemble annotator extract the final label? |
| missing_query_and_gold_concepts | — | — | TextSummarization (0.4603) | ParallelCorpus (0.5636) | How do they quantify alignment between the embeddings of a document and its translation? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.4294) | DatasetBias (0.4121) | How do their interpret the coefficients? |
| missing_query_and_gold_concepts | — | — | ROUGE (0.3861) | AuthorProfiling (0.4612) | By how much do they outperform standard BERT? |
| missing_query_and_gold_concepts | — | — | PhraseBasedMachineTranslation (0.4972) | TextSummarization (0.4078) | How do they obtain parsed source sentences? |
| missing_query_and_gold_concepts | — | — | MeanReciprocalRank (0.3815) | ROUGE (0.5363) | What is their baseline? |
| useful_relation | WordEmbedding | Word2Vec, WordEmbedding | WordEmbedding (0.7506) | WordEmbedding (0.5437) | Do they fine-tune the used word embeddings on their medical texts? |
| useful_relation | DiscourseAnalysis, LabelPropagation | DiscourseAnalysis | LabelPropagation (0.6429) | DiscourseAnalysis (0.5352) | How were dialogue act labels defined? |
| useful_relation | LanguageModel, NaturalLanguageProcessing | ParallelCorpus | LanguageModel (0.6061) | LanguageModel (0.5363) | How does the well-resourced language impact the quality of the output? |
| useful_relation | TextSummarization | TextSummarization | TextSummarization (0.7748) | ROUGE (0.3249) | What are previous state-of-the-art document summarization methods used? |
| useful_relation | ROUGE | NeuralNetwork, ROUGE | ROUGE (0.5802) | ROUGE (0.4477) | What automatic and human evaluation metrics are used to compare SPNet to its counterparts? |
| useful_relation | LanguageModel, NaturalLanguageProcessing | NaturalLanguageProcessing | NaturalLanguageProcessing (0.7442) | HiddenMarkovModel (0.3982) | What result from experiments suggest that natural language based agents are more robust? |
| useful_relation | TextSummarization | NeuralNetwork, ROUGE | TextSummarization (0.7721) | ROUGE (0.4292) | By how much does SPNet outperforms state-of-the-art abstractive summarization methods on evaluation metrics? |
