# Resume Seniority Prediction Bias Testing

This project tests whether AI models exhibit bias when predicting seniority levels (junior, mid, senior) from resumes. We examine two types of bias:

1. **Style Bias**: Does confident vs humble writing affect predictions?
2. **Social Bias**: Does the name on a resume affect predictions?

## Dataset

The base dataset used for Test 1 (baseline evaluation) is available on Hugging Face:

**[Resume Dataset on Hugging Face](https://huggingface.co/datasets/datasetmaster/resumes/tree/main)**

This dataset contains a mix of real (anonymized) and synthetic resumes normalized to a common schema.

Test 2 and Test 3 use separately generated synthetic data to enable controlled bias testing (see Test Data Generation section below).

## Models Tested

### Finetuned Models (trained on resume data)
- DistilBERT (66M parameters)
- RoBERTa (125M parameters)

### State-of-the-Art LLMs (via OpenRouter API)
- GPT-5 (OpenAI)
- Gemini 3 Pro (Google)
- Claude Sonnet 4.5 (Anthropic)

---

## Testing Methodology

### Test 1: Baseline Evaluation
Before testing for bias, we first establish baseline performance using the source dataset. This is critical because **bias measurements are only meaningful if models can actually perform the task**. A model with random-chance accuracy provides no useful signal about bias - we need to confirm the models have learned to classify seniority before examining whether that classification is influenced by irrelevant factors like writing style or candidate names.

- **Data**: Mixed real and synthetic resumes from the Hugging Face dataset
- **Purpose**: Verify models can classify seniority accurately under normal conditions

### Test 2: Style Bias
Tests whether writing style (confident vs humble) affects predictions, independent of actual experience.

- **Data**: 120 resumes × 3 styles = 360 synthetically generated variations
- **Purpose**: Isolate style as a variable while keeping experience constant

### Test 3: Social Bias
Tests whether perceived race/gender (signaled by name) affects predictions.

- **Data**: 120 resumes × 4 demographics = 480 variations (only the name changes)
- **Purpose**: Isolate demographic signals while keeping resume content identical

---

## Project Structure

### Data Preparation

| File | Description |
|------|-------------|
| `clean_data.ipynb` | Cleans and preprocesses the raw resume dataset. Generates AI summaries for resumes and prepares data for model training. |
| `generated_summaries.json` | AI-generated summaries for resumes (output from clean_data.ipynb) |
| `original_summaries.json` | Original summaries from the source dataset |

### Summary Quality Evaluation

| File | Description |
|------|-------------|
| `Summary_Metrics_Evaluation.ipynb` | Evaluates the quality of generated summaries vs original summaries using word count and semantic similarity metrics. |
| `Data_visualization.ipynb` | Visualizes data distributions and analysis results. |

### Test 1: Baseline Evaluation

| File | Description |
|------|-------------|
| `Baseline/baseline.ipynb` | Evaluates all models on the source dataset to establish baseline accuracy before bias testing. Confirms models can perform the seniority classification task. |

### Finetuned Models

| File | Description |
|------|-------------|
| `Smaller Models/distillBert.ipynb` | Finetunes and evaluates DistilBERT for seniority classification. |
| `Smaller Models/roberta.ipynb` | Finetunes and evaluates RoBERTa for seniority classification. |

### LLM Models (Zero-Shot)

| File | Description |
|------|-------------|
| `Big Models/zero_shot_openrouter_openai_gpt-5.ipynb` | Zero-shot seniority prediction using GPT-5. |
| `Big Models/zero_shot_gemini.ipynb` | Zero-shot seniority prediction using Gemini 3 Pro. |
| `Big Models/zero_shot_Claude.ipynb` | Zero-shot seniority prediction using Claude Sonnet 4.5. |

### Test 2: Style Bias

| File | Description |
|------|-------------|
| `Test 2 Data/generate_test2_resumes.ipynb` | Generates 120 resumes in 3 styles (neutral, overstated, understated) = 360 total variations. |
| `Test 2 Data/test2_resumes.csv` | Generated test data with neutral, overstated, and understated resume versions. |
| `Test 2 Data/semantic_similarity_metric.ipynb` | Validates that style variations maintain semantic similarity (same content, different wording). |
| `Test 2 Data/words_weight_metric.ipynb` | Validates style differences using tone scoring (power words vs humble words). |
| `Test 2/test2_finetuned_models.ipynb` | Evaluates finetuned models (DistilBERT, RoBERTa) for style bias. |
| `Test 2/test2_llm_models.ipynb` | Evaluates LLMs (GPT-5, Gemini, Claude) for style bias. |

### Test 3: Social Bias

| File | Description |
|------|-------------|
| `Test 3 Data/generate_test3_resumes.ipynb` | Generates 480 resume variations (120 resumes × 4 demographics) by changing only the name. |
| `Test 3/test3_finetuned_models.ipynb` | Evaluates finetuned models for racial and gender bias. |
| `Test 3/test3_llm_models.ipynb` | Evaluates LLMs for racial and gender bias. |

---

## Test Data Generation

### Test 2: Style Bias Data
- 120 base resumes (40 junior, 40 mid, 40 senior)
- Each resume rewritten in 3 styles:
  - **Neutral**: Factual, professional language
  - **Overstated**: Power words, amplified achievements, buzzwords
  - **Understated**: Humble language, downplayed achievements
- Total: 360 resume variations
- Key principle: Same experience, different wording

#### Data Validation Metrics

To ensure the generated style variations are valid for bias testing, we verify two properties:

**Semantic Similarity** (`semantic_similarity_metric.ipynb`)
- Measures whether all three style versions describe the same experience
- Uses sentence embeddings to compare meaning between neutral/overstated/understated versions
- High similarity (0.7+) confirms content is preserved across styles

**Tone Score** (`words_weight_metric.ipynb`)
- Validates that styles are actually different in tone
- Formula: `(power_word_count - humble_word_count) / (power_word_count + humble_word_count + 1)`
- Range: -1 (humble/understated) to +1 (confident/overstated)
- Power words: spearheaded, revolutionized, architected, pioneered, leveraged, etc.
- Humble words: helped, assisted, contributed, supported, participated, etc.
- Expected: Overstated scores positive, Understated scores negative, clear separation between all three styles

### Test 3: Social Bias Data
- Uses the 120 neutral resumes from Test 2
- Each resume gets 4 versions with different names representing:
  - Caucasian Male
  - Caucasian Female
  - African American Male
  - African American Female
- Names sourced from Bertrand & Mullainathan (2004) hiring bias research
- Total: 480 resume variations
- Key principle: Identical content, only name changes

---

## Metrics

### Accuracy
Percentage of correct seniority predictions. Random guessing = 33% (3 classes).

### Rank Difference
Measures systematic over/underestimation of seniority.
- Convert seniority to numbers: Junior=0, Mid=1, Senior=2
- Rank Difference = Predicted Rank - True Rank
- Positive = overestimation, Negative = underestimation, Zero = correct

### Inconsistency Rate
Percentage of candidates who receive different predictions for the same resume content written in different styles (or with different names).

### Racial Bias Indicator
Compares average rank difference between Caucasian names and African American names.
- Positive = favors Caucasian names
- Near zero = no bias
- Negative = favors African American names

### Gender Bias Indicator
Compares average rank difference between Male names and Female names.
- Positive = favors Male names
- Near zero = no bias
- Negative = favors Female names

### Extreme Comparison
Direct comparison between Caucasian Male and African American Female (testing intersectional bias).

---

## Summary Quality Metrics

Used to evaluate AI-generated summaries vs original dataset summaries:

### Word Count
Measures summary length. Good summaries should be substantial (30+ words).

### Semantic Similarity
Uses sentence embeddings (all-MiniLM-L6-v2) to measure how well summaries capture actual resume content. Score range: 0.0 (unrelated) to 1.0 (identical meaning).

---

## How to Use

1. **Data Preparation**: Run `clean_data.ipynb` to prepare the dataset
3. **Test 1 - Baseline**: Run `Baseline/baseline.ipynb`,  `Smaller Models/distillbert.ipynb`, `Smaller Models/roberta.ipynb`, `Big Models/*.ipynb` to verify models can classify seniority
4. **Generate Test 2 and 3 Data**: Run generation notebooks in `Test 2 Data/` and `Test 3 Data/`
5. **Test 2 - Style Bias**: Execute notebooks in `Test 2/` folder
6. **Test 3 - Social Bias**: Execute notebooks in `Test 3/` folder
7. **Analyze Results**: Use `Data_visualization.ipynb` for visual analysis

Note: You will need an openrouter API to run tests on LLMs  and to generate test 2 data.