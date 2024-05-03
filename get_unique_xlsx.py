import argparse
import openpyxl
import os
import pandas as pd
import numpy as np

dict_acm = {"%B": "Book Title",
            "%Z": "Adviser",
            "%0": "Type",
            "%T": "Title",
            "%J": "Journal/Book",
            "%V": "Volume",
            "%N": "Issue",
            "%P": "Pages",
            "%D": "Publication Year",
            "%U": "DOI Full",
            "%R": "DOI",
            "%X": "Abstract",
            "%I": "Publisher",
            "%K": "Keywords",
            "%A": "Authors",
            "First Author": "First Author",
            "%C": "City",
            "@": "ISSN/ISBN"}

dict_ris = {"TY": "Type",
            "TI": "Title",
            "T1": "Title",
            "T2": "Title2",
            "AU": "Authors",
            "JO": "Journal/Book",
            "IS": "Issue",
            "VL": "Volume",
            "SP": "Pages",
            "EP": "Pages",
            "PY": "Publication Year",
            "DA": "Publication Date",
            "SN": "ISSN/ISBN",
            "DO": "DOI",
            "UR": "URL",
            "KW": "Keywords",
            "AB": "Abstract",
            "ER": "End of Reference",
            "BT": "Book Title",
            "PB": "Publisher",
            "CY": "City"}


def autofit_filter(input_excel, output_filename):
    """
    1. load excel file
    2. first row shall be filtered (to get dropdown capability)
    3. all columns shall be autofitted
    save again
    """
    wb = openpyxl.load_workbook(input_excel)
    ws = wb.active
    # autofit columns
    ws.auto_filter.ref = ws.dimensions
    for c_idx in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                  "M", "N", "O",
                  "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA",
                  "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK"]:
        ws.column_dimensions[c_idx].auto_size = True
    # freeze first row
    ws.freeze_panes = "A2"
    wb.save(output_filename)


def unique_excel(input_excel: str,
                 output_filename: str,
                 column_name: str = "DOI",
                 export_duplicated: bool = True,
                 export_subset_empty: bool = True) -> None:
    """
    Removes duplicates from excel file by searching for duplicactes in
    "column_name" column

    :param input_excel: path to input excel file
    :param output_filename: file name of xlsx file to be saved
    :export_duplicated: if True, export a file with duplicated entries
    :export_subset_empty: if True, export a file with NAs in column_name
    :param column_name: name of column to be checked for duplicates
    """
    df = pd.read_excel(input_excel)

    # some databases have DOIs containging uppercase letters, some lowercase ->
    # make comparable
    df["DOI"] = df["DOI"].str.lower()

    # get subset  with empty cells in coulmn_name column
    subset_empty_idx = df.loc[df[column_name].isnull()].index
    subset_empty = df.loc[subset_empty_idx]

    # replace  blanks in subset[column_name] with NaN
    subset_empty[column_name] = subset_empty[column_name].replace(r'^\s*$',
                                                                  "NA",
                                                                  regex=True)
    # replace np.nan with "NA"
    subset_empty[column_name] = subset_empty[column_name].fillna("NA")

    # drop empty rows
    df = df.drop(subset_empty_idx)

    # drop empty cells in column_name column
    # keep=False -> mark all duplicates as True
    df_duplicated = df[df.duplicated(subset=[column_name], keep=False)]

    # drop duplicates
    df = df.drop_duplicates(subset=[column_name], keep="first")

    # append subset_empty to df
    df = pd.concat([df, subset_empty], ignore_index=True)

    # save as excel with utf-8 encoding
    df.to_excel(output_filename, index=False)

    # autofit all columns -> prettier excel files
    autofit_filter(output_filename, output_filename)
    if export_subset_empty:
        subset_empty.to_excel(output_filename + "_subset_empty.xlsx",
                              index=False)
        autofit_filter(output_filename + "_subset_empty.xlsx",
                       output_filename + "_subset_empty.xlsx")
    if export_duplicated:
        df_duplicated.to_excel(output_filename + "_duplicated.xlsx",
                               index=False)
        autofit_filter(output_filename + "_duplicated.xlsx",
                       output_filename + "_duplicated.xlsx")


def concatenate_tables(list_files: list,
                       output_file_name: str) -> None:
    """
    Full join of all xlsx files in list_files

    :list_files: list of file paths to be concatenated
    :output_file_name: file name of ouput
    """

    # full join: make megafile with all possible clumns
    # load all files from file paths in list_files
    mega_df = pd.DataFrame(columns=list(dict_acm.values()))
    # add column "Source" to keep trrack of where a row came from
    mega_df["Source"] = ""

    for tbl in list_files:

        assert isinstance(tbl, str), "File path must be a string"
        assert os.path.exists(tbl), "File does not exist"

        try:
            df = pd.read_excel(tbl, engine="openpyxl")
        except:  # bare except necessary due to possible occurence of "BadZipFile" from openpyxl
            try:
                df = pd.read_csv(tbl)
            except ValueError:
                try:
                    df = pd.read_excel(tbl, engine="xlrd")
                except ValueError:
                    raise ValueError(
                        "File must be either csv or Excel (xlsx/xls etc.)) supported")

        df["Source"] = tbl
        mega_df = pd.concat([mega_df, df],
                            ignore_index=True,
                            axis=0)  # axis=0 -> add rows
   # clean up DOI columns
    try:
        mega_df["DOI"] = mega_df["DOI"].replace(
            "https://doi.org/", "").astype("string")
        mega_df["DOI Full"] = mega_df["DOI Full"].replace(
            "https://doi.org/", "").astype("string")
    except KeyError:  # in case there is no DOI column
        pass

    # for all entries in ["DOI Full"] that are empty, copy the value from ["DOI"]
    # get indices of empty cells in ["DOI Full"] which are empty
    idx_empty = mega_df.loc[mega_df["DOI Full"].isnull()].index
    mega_df.loc[idx_empty, "DOI Full"] = mega_df.loc[idx_empty,
                                                     "DOI"].astype("string")

    # for all entries in ["DOI Full"] that do not start with "https://doi.org/", add "https://doi.org/"
    mega_df.loc[~mega_df["DOI Full"].str.startswith("https://doi.org/",
                                                    na=False),  # na = False -> ignore NaN values
                "DOI Full"] = "https://doi.org/" + mega_df["DOI Full"]
    mega_df.to_excel(output_file_name, index=False)
    autofit_filter(output_file_name, output_file_name)


def make_xlsx(document: str,
              col_rename_dict: dict,
              outputfilename: str = "output.xlsx",
              acm: bool = True) -> None:
    """
    Takes .enw (==endnote) or .RIS file and converts it to xlsx file

    :param document: string of enw file
    :param col_rename_dict: dictionary with keys as shortcut in enw file and
                            values as column names
    :param outputfilename: name of the output file
    :param acm: if True, the file is an ACM enw file, else it is a RIS file
    """
    # for each line in the file, split by \n
    lines = document.strip().split('\n')

    # store the first 2 letters from each line -> column names
    line_beginnings = []
    for line in lines:
        line_beginnings.append(line[:2])

    # remove duplicates from line_beginnings
    line_beginnings = list(dict.fromkeys(line_beginnings))

    df = pd.DataFrame(columns=line_beginnings)

    # go through each line in the file, match the first 4 letters to the column name,
    # add the rest of the line to the column
    # a new row shall be added after encountering an empty line ('')
    # Example: %0 Journal Article -> column name: %0 (=line[:2]), value: Journal Article (=line[3:len(line)])
    if acm:
        row = 0
        for line in lines:
            if line.startswith('%'):
                column_name = line[:2]
                value = line[3:len(line)]
                try:
                    # concatenate if the column already has a value
                    # (e.g. multiple authors)
                    if df.at[row, column_name] is not np.nan:
                        df.at[row, column_name] = df.at[row,
                                                        column_name] + "," + value
                    else:
                        df.at[row, column_name] = value
                except KeyError:
                    df.at[row, column_name] = value
            else:
                row += 1
    else:
        row = 0
        for line in lines:
            if not line.startswith('ER'):
                column_name = line[:2]
                # delete " - " from the beginning of the line
                value = line[3:len(line)].strip(" - ")
                try:
                    # concatenate if the column already has a value
                    # (e.g. multiple authors)
                    if df.at[row, column_name] is not np.nan:
                        df.at[row, column_name] = df.at[row,
                                                        column_name] + "," + value
                    else:
                        df.at[row, column_name] = value
                except KeyError:
                    df.at[row, column_name] = value
            else:
                row += 1

    # add column "First Author"
    try:
        df["First Author"] = df["%A"].str.split(",").str[0]
    except KeyError:
        pass

    # extract DOI from URL and put in new column
    try:
        df["%R"] = df["%U"].str.replace("https://doi.org/", "")
    except KeyError:
        pass

    # remove "Gr" column
    try:
        df = df.drop(columns=["Gr"])
    except KeyError:
        pass

    # remove blank column
    try:
        df = df.drop(columns=[""])
    except KeyError:
        pass

    # drop all columns which are not in the column rename dict
    try:
        for col in df.columns:
            if col not in col_rename_dict.keys():
                df = df.drop(columns=[col])
        # df = df.drop(columns=[col for col in df.columns if col not in col_rename_dict.keys()])
    except KeyError:
        pass

    # remove "End of Reference" column
    try:
        df = df.drop(columns=["End of Reference"])
    except KeyError:
        pass

    try:
        df["DOI Full"] = df["DOI"]
        df["DOI"] = df["DOI"].str.replace("https://doi.org/", "")
    except KeyError:
        pass

    # rename columns by referring to col_rename_dict
    df = df.rename(columns=col_rename_dict)

    # save as excel with utf-8 encoding
    # Excel "filtering" shall be applied to first row
    df.to_excel(outputfilename, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="get_unique_xlsx.py",
                                     description="Concatenate raw literature database results, deduplicate them and write unique entries to .xlsx file",
                                     epilog="Please refer to daniel.schwabe@ptb.de")
    parser.add_argument("--path_acm_enw",
                        type=str,
                        help="Path to ACM .enw file.",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/acm_new_all.enw")
    parser.add_argument("--path_acm_xlsx",
                        type=str,
                        help="Path to ACM .xlsx file",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/acm_new_all.xlsx")
    parser.add_argument("--path_pubmed",
                        type=str,
                        help="Path to Pubmed .csv file",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/pubmed.csv")
    parser.add_argument("--path_webofscience",
                        type=str,
                        help="Path to Web of Science .xls file",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/wos.xls")
    parser.add_argument("--path_excel_file1",
                        type=str,
                        help="optional Excel file to be added to full join",
                        default="")
    parser.add_argument("--path_excel_file2",
                        type=str,
                        help="optional Excel file to be added to full join",
                        default="")
    parser.add_argument("--path_concatenated",
                        type=str,
                        help="path and name of full join file",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/full_join.xlsx")
    parser.add_argument("--path_concatenated_unique_doi",
                        type=str,
                        help="path and name of full join file with unique DOIs",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/full_join_unique_doi.xlsx")
    parser.add_argument("--path_concatenated_unique_titles",
                        type=str,
                        help="path and name of full join file with unique titles",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/full_join_unique_titles.xlsx")
    parser.add_argument("--path_concatenated_unique_doi_unique_titles",
                        type=str,
                        help="path and name of full join file with unique DOIs and unique titles",
                        default="C:/Users/klass01/Documents/doi_title_extraction/00001/full_join_unique_doi_unique_titles.xlsx")
    args = parser.parse_args()

    if not os.path.exists(args.path_acm_xlsx):
        with open(args.path_acm_enw, 'r', encoding='utf-8') as f:
            enw = f.read()
        make_xlsx(enw, dict_acm, args.path_acm_xlsx)

    # list of paths to tables, drop empty strings
    l_tbls = [args.path_acm_xlsx,
              args.path_pubmed,
              args.path_webofscience,
              args.path_excel_file1,
              args.path_excel_file2]
    l_tbls = [tbl for tbl in l_tbls if tbl != ""]
    print(f'reading {l_tbls}. empty file paths are disregarded')

    concatenate_tables(l_tbls,
                       output_file_name=args.path_concatenated)

    unique_excel(args.path_concatenated,
                 args.path_concatenated_unique_doi,
                 "DOI")

    unique_excel(args.path_concatenated,
                 args.path_concatenated_unique_titles,
                 "Title",
                 export_subset_empty=True)

    unique_excel(args.path_concatenated_unique_doi,
                 args.path_concatenated_unique_doi_unique_titles,
                 "Title",
                 export_duplicated=False,
                 export_subset_empty=False)
    print('\a')
