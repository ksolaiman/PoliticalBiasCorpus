# Pilot Phase - Bias Annotation Dataset (MTurk)

This folder contains the pilot-phase data, MTurk input/output, annotation highlights, and evaluation analysis for the political bias annotation project. The goal of this phase was to refine annotation protocols, develop marker-based interpretation of bias, and prepare for larger-scale classification or dataset release.

---

## 📁 Folder Structure & File Descriptions

### `16_articles_5_workers--input+output/`
- Contains input documents and corresponding annotation outputs for 16 political news articles.
- Each article was annotated by 5 MTurk workers.
- Includes individual responses and extracted highlights.

### `markers_where_bias_is_perceived/`
- Contains `.markers.rtf` files with structured annotations per document.
- Each file includes:
  - `entities`: Named entities mentioned in the article.
  - `markers`: Worker-highlighted spans perceived as biased.
  - `Label`: Final label assigned (Left, Right, Center).
  - `Reasoning`: Worker-provided rationale for bias judgment.
- Used by the notebook to parse and visualize bias sources.

#### 📄 `6e2ec9f5-eb67-4422-84d8-3d68b1a50220.markers.rtf`
- Example `.rtf` file for one article (from the `markers/` folder).
- Contains:
  - Entity and bias annotations.
  - Highlighted phrases or words (markers) used by crowdworkers to infer bias.
  - Final bias label and annotator reasoning.
- Format used for spot-checking MTurk annotations and for developing gold labels.

### 📄 `annotation_info_result.json`
- Main MTurk results file.
- Each key is a document ID (`docid`) corresponding to an article.
- Contains:
  - An array of MTurk responses (`annotation_results`) for each article.
  - Worker IDs, time spent, perceived `bias`, `newstype`, `markers`, and reasoning.
  - Consensus/majority labels: `mturk_majority_label` and `label_by_us`.

### `doc_annotation_info.pkl`
- Python pickled version of the JSON above, optimized for quick analysis in the notebook.

### `input_csv.csv`
- The original CSV submitted as input to MTurk.
- Includes document ID, title, and three snippets (intro, mid, conclusion) per article.


### 📄 `input.txt`
- Raw source data: Contains article IDs, titles, and three article snippets (title, intro, and main body).
- Format: Tab-separated columns — `doc_id`, `title`, `snippet1`, `snippet2`, `snippet3`.
- Redundant plain-text versions of input used during iteration/testing.

### 📄 `input_backup_title.txt`
- Backup copy of the `input.txt` file, preserving the original phrasing of article titles and snippet structure.

### 📄 `input_with_gold_annotated_markers.txt`
- Same format as `input.txt`, but includes a gold label at the end of each row indicating the consensus political bias (`Left`, `Right`, or `Center`).
- Also includes ground-truth marker locations derived manually or via initial annotations.


### `pilot-phase-observations-and-close-examine-results-and-observations.docx`
- Internal summary document of the pilot study:
  - Agreement rates
  - Annotation patterns
  - Worker biases and common justifications
  - Suggested refinements to task design

### `sample-docs-from-pilot-phase-conflicted-labels/`
- Sample documents where MTurk annotators had high disagreement.
- Useful for studying annotation subjectivity and edge cases.

---

## 📊 Notebook Reference

### `MTurk.ipynb`
- Main notebook for analysis and post-processing of the pilot annotations.
- found in `../code/mturk_annotation/MTurk.ipynb`

---

## 🔍 What This Pilot Phase Covers

- Evaluation of task setup and annotation instruction clarity
- Initial scoring schema for ideological slant (via 5-point polarity)
- Bias marker identification (worker-highlighted spans + justification)
- Inter-annotator agreement analysis and scoring normalization strategies

---

## ✅ How to Use This

- Use `annotation_info_result.json` or `doc_annotation_info.pkl` for programmatic label retrieval.
- Inspect `.markers.rtf` files for qualitative examples of perceived bias.
- Reference the notebook (`MTurk.ipynb`) for aggregation, plotting, and label distribution.
- Use `pilot-phase-observations-...docx` to understand lessons learned before scaling.

---


## Citation

> Solaiman, KMA. *Bias-Annotated Political News Snippets via Crowdsourcing: A Pilot Dataset*. 2019.  

---

For questions or contributions, contact: **ksolaima@umbc.edu**
