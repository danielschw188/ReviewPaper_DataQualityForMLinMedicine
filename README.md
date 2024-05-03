# ReviewPaper_DataQualityForMLinMedicine
Supporting code and information for review paper: The METRIC-framework for assessing data quality for trustworthy AI in medicine: a systematic review

## Script for concatenating database results and deduplicating
Run get_xlsx.py
´´´
python3 get_uniqe_xlsx.py --path_acm_enw acm.enw --path_pubmed pb.xlsx --path_webofscience wos.xls --path_concatenated cc.xlsx --path_concatenated_unique_doi uniquedoi.xlsx --path_concatenated_unique_titles uniquetitles.xlsx --path_concatenated_unique_doi_unique_titles uniquedoiuniquetitles.xlsx
´´´
## Figure 2 - Corpus records sorted by publication date + grouped by categories and (non-) life science
