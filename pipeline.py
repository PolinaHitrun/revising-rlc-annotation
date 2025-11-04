import pandas as pd
import numpy as np
import itertools
import re
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa
import krippendorff


def parse_labels(cell):
    if pd.isna(cell) or str(cell).strip() == "":
        return []
    return re.split(r"[+, ]+", str(cell).strip())


def load_annotation_files(file_paths):
    dfs = [pd.read_csv(p) for p in file_paths]
    for df in dfs:
        for col in df.columns[1:]:
            df[col] = df[col].apply(parse_labels)
    return dfs


def merge_annotations(dfs):
    merged = dfs[0].copy()
    for df in dfs[1:]:
        merged = merged.merge(df, on=merged.columns[0], suffixes=("", "_dup"))
        dupcols = [c for c in merged.columns if c.endswith("_dup")]
        merged.drop(columns=dupcols, inplace=True)
    return merged


def encode_labels(df):
    annotator_cols = df.columns[1:]
    mlb = MultiLabelBinarizer()
    
    annot_matrix = []
    for col in annotator_cols:
        annot_matrix.append(mlb.fit_transform(df[col]))
    
    annot_array = np.stack(annot_matrix, axis=1)  # shape: (samples, annotators, labels)
    return annot_array, annotator_cols


def mean_pairwise_jaccard(annot_array):
    n_samples, n_annotators, _ = annot_array.shape
    scores = []

    for i, j in itertools.combinations(range(n_annotators), 2):
        sample_scores = []
        for s in range(n_samples):
            a, b = annot_array[s, i], annot_array[s, j]
            inter = np.logical_and(a, b).sum()
            union = np.logical_or(a, b).sum()
            sample_scores.append(inter / union if union > 0 else 0)
        scores.append(np.mean(sample_scores))
    return np.mean(scores)


def compute_metrics(annot_array):
    n_samples, n_annotators, _ = annot_array.shape

    # Fleiss Kappa: flatten as item × rater → category index
    flattened = np.argmax(annot_array, axis=2)
    fleiss = fleiss_kappa(flattened)

    # Cohen pairwise
    cohen_scores = []
    for i, j in itertools.combinations(range(n_annotators), 2):
        cohen_scores.append(
            cohen_kappa_score(flattened[:, i], flattened[:, j])
        )
    cohen_mean = np.mean(cohen_scores)

    # Krippendorff alpha
    data = flattened.T  # shape: raters × units
    alpha = krippendorff.alpha(reliability_data=data)

    # Jaccard
    jaccard = mean_pairwise_jaccard(annot_array)

    return {
        "Fleiss_kappa": fleiss,
        "Cohen_kappa_mean": cohen_mean,
        "Krippendorff_alpha": alpha,
        "Jaccard_mean": jaccard
    }


def run_pipeline(file_paths):
    dfs = load_annotation_files(file_paths)
    merged = merge_annotations(dfs)
    annot_array, cols = encode_labels(merged)
    metrics = compute_metrics(annot_array)
    return metrics

if __name__ == "__main__":
    FILE_PATHS = ["all/text1.csv", "all/text2.csv", "all/text3.csv"] # Example file paths
    results = run_pipeline(FILE_PATHS)
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}")