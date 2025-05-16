# Gold Annotations for Political Bias Corpus

This folder contains the finalized **gold-standard annotations** from our political bias dataset based on MTurk worker agreement. Each file represents a distinct category of agreement or perceptual mismatch between annotators and outlet labels.

## Inclusion Criteria
We selected **only those documents** where **two independent crowd annotators agreed** on the bias label. Based on whether this agreed label matches the known outlet bias or not, the documents are grouped as follows:

## Files

### `gold_docs_workers_agreed_and_matched_outlet.csv`
- **Count**: 144 articles  
- **Description**: Articles where both annotators agreed on the bias label (13 articles), or one selected Center and the other selected partisan (131 articles). In the later case, we choose the partisan label as final human label. The final human label matches the known political leaning of the news outlet.
- **Use**: High-confidence training and evaluation set for bias detection. 
- **Human-label**: `L`, `R` (left, right)

### `gold_docs_workers_agreed_labeled_center_conflicted_with_outlet_lr.csv`  
- **Count**: 72 articles 
- **Description**: Articles perceived as **center** by both annotators, even though the publishing outlet is known to be partisan (**left, leaning left, leaning right,** or **right**).
- **Use**: Highlights **perceived neutrality** from otherwise partisan outlets. Useful for subtle framing or rhetorical analysis.
- **Human-label**: `C` (center)

### `gold_docs_workers_agreed_conflicted_with_outlet.csv`
- **Count**: 54 articles 
- **Description**: Articles where both annotators agreed on a label that **conflicts** with the outlet’s known political leaning (e.g., both label it `L`, but the outlet is `R`).
- **Use**: Potentially valuable for identifying **atypical framing** or misalignment between perception and source bias.
- **Human-label**: `L`, `R` (disagreeing with `outlet_bias`)

---

### 📁 `sample-docs-from-conflicted-labels-workerVSsourceLabel/`  
- **Contents**:  
  - Hand-picked examples from disagreement/conflict cases  
  - Additional `.txt` files showing the breakdown of annotator behavior  
- **Purpose**: Useful for qualitative inspection and error analysis. Not part of main gold set, but valuable for interpretation or annotation refinement.

---

## Format

Each CSV contains the following columns:

- `docid`: Unique identifier for the document
- `title`: Headline or title of the article
- `event`: The political topic or event covered
- `full_text`: Full text or extended excerpt used for annotation
- `worker_1_label`
- `worker_2_label`
- `human_label`: Final perceived bias label agreed upon by annotators (`L`, `R`, or `C`)
- `outlet_bias`: Known political leaning of the source (`L` or `R`)

## Notes

- Articles where annotators **disagreed** were excluded from this release.
- Only documents with **two valid annotations** and agreement were included.
- All annotations were conducted using a custom MTurk interface with pre-qualified workers.


---

## Licensing

You may use this dataset for **non-commercial academic purposes**, with proper citation. If you build upon this work, please reference our upcoming paper and this repository.

---

For questions, please contact: [ksolaima@umbc.edu](mailto:ksolaima@umbc.edu)
