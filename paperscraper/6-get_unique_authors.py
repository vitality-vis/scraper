# External packages
import sys
import pandas as pd
import ast
import os

# Internal modules
import paperscraper.config as config


def main():

    # Read input file
    df_scraped_input = pd.read_csv(config.path_postprocessing_output, sep='\t', index_col=0)

    unique_authors = set()
    for index, row in df_scraped_input.iterrows():
        authors_list = list()
        try:
            authors_list = ast.literal_eval(row["author_processed"])
        except Exception as e:
            # These are mostly 'ERROR' and 'No Url' strings that are actually Error Codes defined in the scraper.
            pass

        if isinstance(authors_list, list):
            for au in authors_list:
                unique_authors.add(au)

    # Save list to disk
    pd.DataFrame(list(unique_authors), columns=["author"]).to_csv(config.path_unique_authors, sep='\t', header=True)


if __name__ == "__main__":
    main()
    sys.exit(os.EX_OK)  # code 0, all ok
