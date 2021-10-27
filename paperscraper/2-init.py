# External packages
import lxml.etree as ET
import sys
import pandas as pd
import os

# Internal modules
import paperscraper.config as config


# FILTER the huge dblp_processed.xml file to keep just the data that we are interested in.
# TODO: Re-run this if (1) The <config.interesting_venues> list has changed or (2) There is a NEW DBLP snapshot .
def main():
    result_list = list()
    src_set = set()
    for event, elem in ET.iterparse(config.path_input, encoding='UTF-8', recover=True):
        obj = dict()
        to_add = False
        for child in elem.getchildren():
            if child.tag not in obj:
                if child.tag in ["author", "ee", "url"]:
                    obj[child.tag] = list()
                else:
                    obj[child.tag] = None

            if child.tag in ["author", "ee", "url"]:
                if child.text is not None:
                    obj[child.tag].append(child.text.replace("%26", "&"))
                else:
                    obj[child.tag].append(child.text)
            else:
                obj[child.tag] = child.text # title, year, pgs

            # Only consider adding entries from the source defined above
            if child.text in config.interesting_venues and child.tag == config.interesting_venues[child.text]["sourcetype"]:
                obj["source"] = child.text
                to_add = True
                if child.text not in src_set:
                    src_set.add(child.text)
                    print(child.text)

        if to_add:
            result_list.append(obj)

    # Create a DataFrame
    df_result_list = pd.DataFrame(result_list)

    # Initialize the fields that we are going to scrape.
    # TODO: Update these if more fields are added.
    df_result_list["abstract"] = "Not Scraped"
    df_result_list["keywords"] = "Not Scraped"
    df_result_list["citation_count"] = "Not Scraped"

    # Save to disk
    df_result_list.to_csv(config.path_output, sep='\t', header=True)


if __name__ == "__main__":
    main()
    sys.exit(os.EX_OK) # code 0, all ok
