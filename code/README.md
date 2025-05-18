
### raw_selection_of_issues_events_articles+create_MTurk_HIT_input+outlet_bias_label_mapping.ipynb (previously Untitled1.ipynb)
(Not adding in git repo, but individual *.py files are added)
- The steps are below:

1. Found all the issues in the full data (article_metadata.xml) i.e., abortion, criminal justice
2. Found all the events in the full data (article_metadata.xml) - each issue may have multiple events
    - stories are just events
3. Find all the documents for each event - each event may have multiple articles

4. Then manually went through all the events via multiple sweeps using many temp files - i.e., selected_story_files_..., selected_article_files...., full_story_sweep,... etc

5. Curated `414 events/stories` from selected `issues`          -- `selected_story_file_v2.txt`
6. The 414 events has `900 articles`                            -- `selected_article_file_v2.txt`


7. Created the MTurk input for all 900 articles
8. Created the `source bias` label for 300 articles 
    -- need more of this task (for the rest of 900)


## We separated the above file into:
- create_MTurk_HIT_input.py
- outlet_bias_label_mapping.py
and ran them with current directory structure in git repo.

## MTurk Task Automation
- mturk_automation/
    - MTurk.ipynb — bulk HIT generation, task formatting, and submission logic
    - MTurk_Qualification_Test.ipynb — task qualification questions and examples


## Processing the MTurk Response
- create_list_of_docids_of_disagreement_and_high_agreement_from_MTurk_tagged_annotations.py
- evaluate-worker-vs-outlet-label-from-gold-csvs.py


## Stat Calculation of the Dataset
- preprocessing/
- input is in ../docs/stats/
— scripts for computing annotation agreement, event-topic frequency, and bias alignment

## Results and Figures
- results_figures/


## Data Collection Scripts
- event_spider.py — scrape events and match to article IDs
- sourceurl_scrap.py — scrape raw article URLs from known sources
- NewsArticleExtractor.py — extract and format article content
- helper_functions.py — shared utilities for metadata extraction