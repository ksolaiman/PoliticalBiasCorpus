# HIT_inputs

This folder contains the exact input files used to generate the HITs (Human Intelligence Tasks) on Amazon Mechanical Turk (MTurk). These files were used to present documents to qualified workers for bias annotation.

## Files

- **`mturk_input_300.csv`**  
  Contains the 300 documents used in the final MTurk HITs.  
  Fields include: `docid`, `title`, `snippet1`, `snippet2`, `snippet3`, `event`, `full_text`.

- **`mturk_input_900.csv`**  
  Full set of 900 curated articles prepared for potential annotation.  
  Only 300 were used in the final experiment; this file supports future extensions.

- **`mturk_input_sample (4 docs - no docid).csv`**  
  A 4-document sample used for HIT template prototyping or user testing.  
  Does not include `docid` field.

- **`mturk_self_eval_input.csv`**  
  A test input used for evaluating worker understanding or task clarity.  
  Includes selected articles with expected bias to test annotator accuracy.

---

These files were generated using scripts in the `code/` folder and represent the original curated content delivered for annotation. For full mapping of annotation results, refer to the `gold/` directory and evaluation scripts.
