# External packages
import sys
import os
import pandas as pd
import ast
import string
import unicodedata
import re
import string


# Internal modules
import config
regex = re.compile(r'[\n\r\t]')
set_punctuations = set(string.punctuation)
set_numbers = set("0123456789")

def clean_string(_string):
    _string_normalized = unicodedata.normalize("NFKD", _string)
    _string_stripped = str(regex.sub("", _string_normalized)).strip()
    _string_recoded = _string_stripped.encode('ascii', 'ignore').decode('UTF-8')
    return _string_recoded


def process_title(title_string):
    try:
        if not (5 < len(title_string) < 250):
            return None

        return " ".join(title_string.split())
    except Exception as e:
        # print(e)
        return None

def process_abstract(abstract_string):
    try:
        if abstract_string in ["Not Scraped", "Error", "No Url"]:
            return None

        if not (50 < len(abstract_string) < 2500):
            return None

        return " ".join(abstract_string.split())
    except Exception as e:
        # print(e)
        return None

def process_authors(author_string):
    try:
        author_list = ast.literal_eval(author_string)
        if isinstance(author_list, list):
            recoded_author_list = [string.capwords(_author.encode('ascii', 'ignore').decode('UTF-8')) for _author in author_list]
            return str(recoded_author_list)
    except Exception as e:
        # print(e)
        pass
    return author_string


def process_citation_counts(citation_count_string):
    try:
        if not citation_count_string.isnumeric():
            return None
        else:
            return citation_count_string
    except Exception as e:
        return None


def process_keywords(keywords_string):
    try:
        keywords_list = ast.literal_eval(keywords_string)
        if isinstance(keywords_list, list):
            processed_keywords_list = list()

            for _keyword in keywords_list:
                if "→" in _keyword:
                    kws = _keyword.split("→")
                    for kw in kws:
                        processed_keywords_list.append(kw)
                elif "Key words: " in _keyword:
                    _keyword = re.sub("Key words: ","",_keyword)
                    kws = _keyword.split(" – ")
                    for kw in kws:
                        processed_keywords_list.append(kw)
                else:
                    processed_keywords_list.append(_keyword)

            # Start with removing Nones.
            processed_keywords_list = list(filter(None, processed_keywords_list))

            # Make them all lower-case for case insensitive match to be successful.
            processed_keywords_list = [str(kw).lower() for kw in processed_keywords_list]

            # Clean the Keyword String
            processed_keywords_list = [clean_string(kw) for kw in processed_keywords_list]

            # Remove weird phrases in the Keyword that sometimes happens based on how it's maintained on the Publisher's website.
            _interim_processed_list = []
            for kw in processed_keywords_list:
                for regex in config.keyword_patterns_to_remove:
                    kw = re.sub(regex,"",kw)
                _interim_processed_list.append(kw)
            processed_keywords_list = _interim_processed_list

            # Remove keywords if it has Only keywords or Only punctuations
            processed_keywords_list = [i for i in processed_keywords_list if not all(j in set_punctuations or j in set_numbers for j in i)]

            # Finally, Remove None's again.
            processed_keywords_list = list(filter(None, processed_keywords_list))

            # Merge Different Variations of the same Keyword
            _interim_processed_list = []
            for kw in processed_keywords_list:
                if kw in config.keywords_to_merge:
                    _interim_processed_list.append(config.keywords_to_merge[kw])
                else:
                    _interim_processed_list.append(kw)
            processed_keywords_list = _interim_processed_list

            # And of course, de-duplicate if some have both HCI and Human-Computer Interaction initially.
            processed_keywords_list = list(set(processed_keywords_list))

            # Let's capitalize the keywords so that they look nice.
            processed_keywords_list = [string.capwords(kw) for kw in processed_keywords_list]

            return str(processed_keywords_list)
    except Exception as e:
        # print(e)
        pass
    return None


def main():
    # Read it
    df_scraped_input = pd.read_csv(config.path_output, sep='\t', index_col=0)

    # Process authors
    # 1) Convert utf-8 characters to ascii (will result in data loss but ignore errors) so that they are searchable via a keyboard.
    df_scraped_input["author_processed"] = df_scraped_input.apply(lambda row: process_authors(row["author"]), axis=1)

    # Process keywords
    # 2) Convert utf-8 characters to ascii (will result in data loss but ignore errors) so that they are searchable via a keyboard.
    df_scraped_input["keywords_processed"] = df_scraped_input.apply(lambda row: process_keywords(row["keywords"]), axis=1)

    # Process citation counts
    # 3) Ensure that this is always NONE or NUMERIC
    df_scraped_input["citation_count_processed"] = df_scraped_input.apply(lambda row: process_citation_counts(row["citation_count"]), axis=1)

    # Process abstract
    # 4) Ensure that there aren't new lines and that the abstracts are between X and Y characters in length
    df_scraped_input["abstract_processed"] = df_scraped_input.apply(lambda row: process_abstract(row["abstract"]), axis=1)

    # Process titles
    # 5) Ensure that there aren't new lines and that the titles are between X and Y characters in length
    df_scraped_input["title_processed"] = df_scraped_input.apply(lambda row: process_title(row["title"]), axis=1)

    # Save POST-PROCESSED FILE
    df_scraped_input.to_csv(config.path_postprocessing_output, sep='\t', header=True)


if __name__ == "__main__":
    main()

    # code 0, all ok
    sys.exit(0)
