# Repository for Annotation Agreement Experiments
This repository contains all materials, data, and code used in the inter-annotator agreement experiments described in article "Bridging Error Analysis and NLP: Revising Learner Corpus Annotation" on the updated error annotation guidelines for the Russian Learner Corpus (RLC). This repository contains all annotation data, notebooks, and guidelines necessary to fully reproduce the experiments reported in the article. All metric values presented in the paper can be reproduced by running the notebooks or the pipeline script.


## Repository Structure
```
repo/
├── all/                          
│   ├── analysis.ipynb          # Analysis notebook for the second experiment
│   ├── text1.csv               # Annotator labels for Text 1
│   ├── text2.csv               # Annotator labels for Text 2
│   └── text3.csv               # Annotator labels for Text 3
│
├── ortho infl misspell/        
│   ├── analysis.ipynb          # Analysis notebook for the first experiment
│   ├── new1.csv                # Annotations using the new guidelines
│   ├── new2.csv
│   ├── old1.csv                # Annotations using the old guidelines
│   └── old2.csv
│
├── pipeline.py                 # Unified pipeline for computing all agreement metrics
├── requirements.txt            # Python dependencies
├── RLC_old_guidelines_rus.xlsx
├── RLC_old_guidelines_eng.xlsx
├── RLC_new_guidelines_rus.xlsx
└── RLC_new_guidelines_eng.xlsx # Full versions of old and new guidelines (RU + EN)
```

## Annotation Guidelines
The repository includes four files with the full text of the annotation guidelines used in the experiments:
- RLC_old_guidelines_rus.xlsx — original Russian guidelines
- RLC_old_guidelines_eng.xlsx — original English version
- RLC_new_guidelines_rus.xlsx — revised Russian guidelines
- RLC_new_guidelines_eng.xlsx — revised English version
## Experiments
### Experiment 1

Located in: ortho infl misspell/
- Two annotators used the old guidelines and two used the new guidelines.
- Files old1.csv and old2.csv contain the labels produced under the old guidelines; new1.csv and new2.csv contain the labels under the new guidelines.
- The notebook analysis.ipynb computes Fleiss’ kappa and Cohen’s kappa.

### Experiment 2

Located in: all/
- Three learner texts (text1.csv, text2.csv, text3.csv) with manually pre-identified error slots.
- Each text was annotated independently by annotators following the old and the new guidelines.
- The notebook analysis.ipynb computes Fleiss’ kappa, Jaccard similarity, Krippendorff’s alpha, and (for the concatenated dataset) Cohen’s kappa.

## Metric Pipeline

pipeline.py provides a unified implementation of all agreement metrics used in the experiments:
- Fleiss’ kappa
- Cohen’s kappa
- Jaccard similarity
- Krippendorff’s alpha

This module is used by both analysis notebooks and can be adapted for future large-scale evaluations.

## Dependencies

All required Python packages are listed in requirements.txt.
To recreate the environment:
``` bash
pip install -r requirements.txt
```
## How to use
The script `pipeline.py` provides an interface for computing inter-annotator agreement metrics for any set of annotation files. It supports multi-label tags and calculates four agreement measures: Fleiss’ kappa, Cohen’s kappa (mean pairwise), Krippendorff’s alpha, and mean pairwise Jaccard similarity.

### Input Format
Each annotation file must be a CSV table where the first column contains error slot identifiers (e.g., token IDs or manually defined indices), all remaining columns correspond to annotators and each cell contains a list of tags, separated by +, comma, or whitespace.
#### Example
| id | annotator1   | annotator2 | annotator3   |
|----|--------------|------------|--------------|
| 1  | Ortho+Miss   | Ortho      | Ortho        |
| 2  | Misspell     |            | Misspell     |
| 3  | Gov          | Gender     | Gov          |

To run pipeline as a script modify the `FILE_PATHS`:
``` python
if __name__ == "__main__":
    FILE_PATHS = ["all/text1.csv", "all/text2.csv", "all/text3.csv"]
    results = run_pipeline(FILE_PATHS)
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}")
```
and run:
``` bash
python pipeline.py
```
Or you can import it to your project:
```
from pipeline import run_pipeline

files = ["all/text1.csv", "all/text2.csv", "all/text3.csv"]
metrics = run_pipeline(files)
print(metrics)
```
### Notes and Limitations
- Fleiss’ kappa, Cohen’s kappa, and Krippendorff’s alpha currently operate on a single dominant label per annotation slot (the highest-index label after binarization), because standard libraries do not support true multi-label categorical agreement.
- Jaccard similarity captures full multi-label overlap and is often more informative for multi-tag settings.
- Empty cells are treated as “no tags” and converted to empty sets.
