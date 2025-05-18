# PoliticalBiasCorpus

## Repository Structure

- `hit_inputs/`: Input article metadata used to generate MTurk HITs (snippets, doc ID, event). Each task in MTurk is denoted as a HIT. The snippets and docs here were used to generate the HTML page for the workers to annotate.
- `mturk_annotations_raw/`: Raw annotation data from MTurk (CSV exports).
- `gold/`: Final, conflict-resolved annotations and agreement statistics.
- `docs/`: Annotation task templates, qualification instructions, and manual audit notes.

### Divergent Label Examples

We include a curated set of documents where the final MTurk label diverged from the known source-level bias (e.g., a Right label on a Left-leaning outlet). These cases highlight subjectivity in perceived ideological bias and are valuable for qualitative and error analysis.

- `conflicting_annotation_cases.csv`: DocID, Title, MTurk label, Source label, Notes
- `conflicting_annotation_articles/`: Optional full article texts for selected divergent cases (for deeper inspection)

These cases are useful for evaluating model generalization, interpretability, and robustness to subtle or tone-shifted bias.


### Party Principle References

To support consistent annotations and bias evaluation, we include reference materials outlining commonly accepted liberal and conservative principles:

- `conservative_beliefs.txt`
- `liberal_beliefs.txt`

These were used during annotation and validation as a reasoning aid - not to enforce any labeling decision. Annotators may have referred to them to calibrate or justify their selections.



## MTurk Annotation Dataset

This folder contains results from a Mechanical Turk annotation task where 300 political news articles were each labeled by two workers for perceived political bias.

## pilot-phase/
Includes:
- Mturk annotations for 16-docs-by-5 separate workers
  - Highlighted bias markers (lines that indicate bias) in the articles
  - inputs and annotation results from this task
  - ran from `../code/mturk_annotation/MTurk.ipynb`
- post-mturk-result-observation-by-2-expert
  - Early conflicted-label examples
- pilot phase observation notes from the 2nd step
- Improvements made in HIT design for final annotation (found in observation notes)


### Files

- `mturk_annotation_raw.csv`: Raw annotations with no postprocessing or interpretation. Each document appears twice, once per annotator. Includes document ID, article snippets, full text, annotator highlights, reason, and scalar Left/Right bias ratings.
- `mturk_annotation_tagged.csv`: Annotator responses, plus additional columns added by the authors indicating:
  - Whether the two annotators agreed.
  - Whether the agreed label matches or conflicts with the original news outlet's known political bias.

This release supports studies of annotator agreement, human-perceived bias, and alignment with known source bias.
