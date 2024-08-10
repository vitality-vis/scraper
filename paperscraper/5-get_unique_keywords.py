# External packages
import sys
import pandas as pd
import ast
import os

# Internal modules
import config


def main():

    # Read input file
    df_scraped_input = pd.read_csv(config.path_postprocessing_output, sep='\t', index_col=0)

    unique_keywords = set()
    for index, row in df_scraped_input.iterrows():
        keywords_list = list()
        try:
            keywords_list = ast.literal_eval(row["keywords_processed"])
        except Exception as e:
            # These are mostly 'ERROR' and 'No Url' strings that are actually Error Codes defined in the scraper.
            pass

        if isinstance(keywords_list, list):
            for kw in keywords_list:
                unique_keywords.add(kw)

    # Save list to disk
    pd.DataFrame(sorted(list(unique_keywords)), columns=["keyword"]).to_csv(config.path_unique_keywords, sep='\t', header=True)


if __name__ == "__main__":
    main()
    sys.exit(os.EX_OK)  # code 0, all ok
