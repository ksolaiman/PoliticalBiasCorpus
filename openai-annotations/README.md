# OpenAI Annotations

This folder contains supplementary figures and CSV data files for the **BiasLab** paper, specifically supporting the GPT-4o annotation simulation and comparison analysis.

## Folder Structure

### `/figures`
Visual assets used in the paper and appendix, generated from OpenAI model annotations.

- `confusion_matrix_cleaned.png`: Cleaned visualization of GPT-4o vs. outlet label alignment.
- `error-patterns.png`: Common misclassification patterns (e.g., Right → Left).
- `Per-Batch Annotation Accuracy (Batches 1–30).png`: Accuracy trend across all 30 batches.
- `summary_chart_batch21_30.png`: Subset view for batches 21–30.

### CSV Files

- `gold_openai_annotations_all_batches_1_30.csv`: Final structured annotation labels from GPT-4o across all 300 articles.
- `openai_annotations_batch11_20_full.csv`: Raw outputs and metadata for batches 11–20.
- `openai_annotations_batch21_30.csv`: Raw outputs for batches 21–30.
- `openai_vs_outlet_labels_batch1_10.csv`: Alignment comparison between OpenAI labels and outlet bias for batches 1–10.

## Notes

- All OpenAI annotations were generated using the same prompt schema shown in the paper.
- Contact `ksolaima@umbc.edu` for replication instructions or schema details.


