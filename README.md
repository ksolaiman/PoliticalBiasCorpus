# PoliticalBiasCorpus

## Repository Structure

- `hit_inputs/`: Input article metadata used to generate MTurk HITs (snippets, doc ID, event). Each task in MTurk is denoted as a HIT. The snippets and docs here were used to generate the HTML page for the workers to annotate.
- `annotations_raw/`: Raw annotation data from MTurk (CSV exports).
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

