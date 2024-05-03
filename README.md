# ReviewPaper_DataQualityForMLinMedicine
Supporting code and information for review paper: The METRIC-framework for assessing data quality for trustworthy AI in medicine: a systematic review

The following files are provided:
- Creating literature database
  - "get_unique_xlsx.py"
    - python script for concatenating and deduplicating raw database results
- Plotting Figure 2
  - "fig_2_dotplots.R"
    - R script for generating Figure 2 of the manuscript
  - "provenance_corpus_papers.xlsx"
    - data required for Figure 2

## Script for concatenating database results and deduplicating
Run get_xlsx.py
```
python3 get_uniqe_xlsx.py --path_acm_enw acm.enw --path_pubmed pb.xlsx --path_webofscience wos.xls --path_concatenated cc.xlsx --path_concatenated_unique_doi uniquedoi.xlsx --path_concatenated_unique_titles uniquetitles.xlsx --path_concatenated_unique_doi_unique_titles uniquedoiuniquetitles.xlsx
```
## Figure 2 - Corpus records sorted by publication date + grouped by categories and (non-) life science
