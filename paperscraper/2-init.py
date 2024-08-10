# External packages
import lxml.etree as ET
import sys
import pandas as pd
import os

# Internal modules
import config


# FILTER the huge dblp_processed.xml file to keep just the data that we are interested in.
# TODO: Re-run this if (1) The <config.interesting_venues> list has changed or (2) There is a NEW DBLP snapshot.
def main():

    # Articles already scraped from previously scraped VitaLITy corpus
    papers_existing_in_prev_corpus = dict()
    count_papers_existing = 0
    count_papers_new = 0
    if os.path.exists(config.path_prior_vitality_corpus):
        df_prev_corpus = pd.read_json(config.path_prior_vitality_corpus)
        df_prev_corpus["unique_article_identifier"] = df_prev_corpus['Title'].astype(str) + '\t' + df_prev_corpus['Source'].astype(str) + '\t' + df_prev_corpus['Year'].astype(str)
        papers_existing_in_prev_corpus = df_prev_corpus.set_index("unique_article_identifier").T.to_dict()

    result_list = list()
    result_counter = 0
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
            # Initialize the fields that we are going to scrape.
            # TODO: Update these if more fields are added.
            obj["abstract"] = "Not Scraped"
            obj["keywords"] = "Not Scraped"
            obj["citation_count"] = "Not Scraped"

            # Update the above fields if they have already been scraped before.
            _title = obj["title"] if obj["title"] is not None else ""
            _source = obj["source"] if obj["source"] is not None else ""
            unique_identifier = _title + "\t" + _source + "\t" + obj["year"]
            if unique_identifier in papers_existing_in_prev_corpus:
                obj["abstract"] = papers_existing_in_prev_corpus[unique_identifier]["Abstract"]
                obj["keywords"] = papers_existing_in_prev_corpus[unique_identifier]["Keywords"]
                count_papers_existing += 1
            else:
                count_papers_new += 1

            result_counter += 1
            if result_counter % 5000 == 0:
                print(count_papers_existing, count_papers_new)

            result_list.append(obj)

    # Final tally
    print(count_papers_existing, count_papers_new)

    # Create a DataFrame
    df_result_list = pd.DataFrame(result_list)

    # Save to disk
    df_result_list.to_csv(config.path_output, sep='\t', header=True)

if __name__ == "__main__":
    main()
    sys.exit(os.EX_OK) # code 0, all ok
