# External packages
import lxml.etree as ET
import sys
import pandas as pd
import os

# Internal modules
import paperscraper.config as config


# Find Unique venues from the DBLP xml looking ONLY for ["article","inproceedings","incollection"] and ["journal", "booktitle"].
# TODO: Re-run this if (1) The above list has changed OR (2) There is a NEW DBLP snapshot.
def main():
    unique_sources = dict()
    for event, elem in ET.iterparse(config.path_input, recover=True):
        if elem.tag in ["article","inproceedings","incollection"]:
            for child in elem.getchildren():
                if child.tag in ["journal", "booktitle"]:
                    if child.text not in unique_sources:
                        unique_sources[child.text] = dict()
                        unique_sources[child.text]["count"] = 0
                        unique_sources[child.text]["child_tag"] = child.tag
                        unique_sources[child.text]["elem_tag"] = elem.tag
                    unique_sources[child.text]["count"] += 1

    # Create a Pandas DataFrame
    df_unique_sources = pd.DataFrame.from_dict(unique_sources, orient="index")

    # Save it to disk
    df_unique_sources.to_csv(config.path_unique_venues, header=True, sep='\t')


if __name__ == "__main__":
    main()
    sys.exit(os.EX_OK)  # code 0, all ok
