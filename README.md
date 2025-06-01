![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC--BY--NC--SA-blue)
[![arXiv](https://img.shields.io/badge/arXiv-2505.16081-b31b1b.svg)](https://arxiv.org/abs/2505.16081)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15571668.svg)](https://doi.org/10.5281/zenodo.15571668)



# BiasLab: Political Bias Annotation Corpus

This repository contains a structured political bias dataset annotated via crowd-sourced judgments. Articles are drawn from ideologically labeled media outlets, and annotation is designed to capture sentiment toward political parties, identify bias markers, and evaluate human alignment with known outlet bias.

---

## Repository Structure

- `hit_inputs/`
Input article files used to generate HITs (Human Intelligence Tasks) for MTurk. Includes 300-final and 900-full curated subsets, plus evaluation samples. The snippets and docs created for the HITS here were used to generate the HTML page for the workers to annotate.

- `mturk_annotations_raw/`
  Raw annotations exported from MTurk batches. Includes HIT batch CSV exports, summaries, and conflict case docIDs.

- `gold/`
  Final, conflict-resolved annotations derived from MTurk worker agreement. Documents are grouped by whether annotator consensus matches or conflicts with the known source bias.

- `docs/`
  Article metadata, reference principles, selection logs, and statistical summaries. Includes curated lists of events, issues, and source labels.

- `code/`  
  Scripts and notebooks used to generate HIT inputs, process MTurk annotations, evaluate agreement, and compute dataset-level statistics. Subfolders include:
  - `mturk_automation/`: Qualification test creation and HIT submission logic
  - `preprocessing/`: Scripts for computing agreement, distribution, and confusion matrices
  - `Data Collection/`: Web scraping and article curation utilities
  - `modeling/`: Logistic regression baselines for bias perception alignment and rationale prediction

- `pilot-phase/`  
  MTurk annotation results for 16 articles rated by 5 annotators each. Used to refine annotation protocols and develop justification-based bias detection.

- `mturk_task_templates/`  
  HTML templates used for MTurk HITs and qualification tasks. Includes both annotation and evaluator versions.

- `mturk_metadata/`  
  Metadata logs from MTurk pipeline, including worker qualification tracking and ID history.


## MTurk Annotation Summary

We collected annotations for 300 curated political news articles using qualified U.S.-based MTurk workers. Each article was:

- Shown as 3 snippets (intro, middle, conclusion)
- Rated on a 5-point sentiment scale toward **Democrats** and **Republicans**
- Justified using bias indicators (e.g., omission, spin, tone)

Each article received 2 independent annotations. Final labels were aggregated via:

- Full agreement → accepted
- Center + partisan → use partisan
- Conflict → excluded from gold
  - included in `mturk_annotations_raw/`

---

### Divergent Label Examples

Some articles received human bias labels that **differed** from their outlet’s known leaning. 
They are captured in:
- `gold/` folder breakdowns (e.g., `matched`, `conflicted`, `center-labeled`)
- Diagnostic documents with docID mappings

---

### Party Principle References

To support consistent annotations and bias evaluation, we include reference materials outlining commonly accepted liberal and conservative principles:

- `conservative_beliefs.txt`
- `liberal_beliefs.txt`

<!-- These references informed interpretation but were not prescriptive. -->
These were used during annotation and validation as a reasoning aid - not to enforce any labeling decision. Annotators may have referred to them to calibrate or justify their selections.

---

## pilot-phase/

Before the final annotation, we conducted a 16-article pilot. Includes:
- Mturk annotations for 16 articles by 5 separate workers
  - Highlighted bias markers (lines that indicate bias) in the articles
  - inputs and annotation results from this task
  - ran from `../code/mturk_annotation/MTurk.ipynb`
- post-mturk-result-observation-by-2-expert
  - Early conflicted-label examples
- pilot phase observation notes from the 2nd step
- Improvements made in HIT design for final annotation (found in observation notes)


---

## Citation

If using this dataset, please cite:

### Paper

```bibtex
@misc{solaiman2025biaslab,
      title={BiasLab: Toward Explainable Political Bias Detection with Dual-Axis Annotations and Rationale Indicators}, 
      author={KMA Solaiman},
      year={2025},
      eprint={2505.16081},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.16081}, 
}
```

#### Dataset and Code (Zenodo)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15571668.svg)](https://doi.org/10.5281/zenodo.15571668)
Use this DOI when citing the dataset or code in your work.


---
### License

This dataset and code are released under the [CC BY-NC-SA 4.0 License](https://creativecommons.org/licenses/by-nc-sa/4.0/).  
You are free to use and adapt the materials for non-commercial academic purposes with attribution.

`Developed at H.A.R.M.O.N.I. Lab, UMBC`

---

For questions or contributions, contact:
📧 ksolaima@umbc.edu

🔗 https://ksolaiman.github.io