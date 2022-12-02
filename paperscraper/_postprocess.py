# External packages
import ast
import re
import string
import unicodedata

from sqlitedict import SqliteDict
from loguru import logger
from tqdm import tqdm

# Internal modules
from paperscraper.config import config, Config

regex = re.compile(r'[\n\r\t]')
set_punctuations = set(string.punctuation)
set_numbers = set("0123456789")

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)


def _clean_string(_string):
    _string_normalized = unicodedata.normalize("NFKD", _string)
    _string_stripped = str(regex.sub("", _string_normalized)).strip()
    _string_recoded = _string_stripped.encode('ascii', 'ignore').decode('UTF-8')
    return _string_recoded


def process_title(title_string):
    """Ensure that there aren't new lines and that the titles are between X and Y characters in length."""
    try:
        if not (5 < len(title_string) < 250):
            return None

        return " ".join(title_string.split())
    except Exception:
        # print(e)
        return None


def process_abstract(abstract_string):
    """Ensure that there aren't new lines and that the abstracts are between X and Y characters in length."""
    try:
        if abstract_string in ["Not Scraped", "Error", "No Url"]:
            return None

        if not (50 < len(abstract_string) < 2500):
            return None

        return " ".join(abstract_string.split())
    except Exception:
        # print(e)
        return None


def process_authors(author_string):
    """
    Convert utf-8 characters to ascii so that they are searchable via a keyboard.

    (will result in data loss but ignore errors)
    """
    try:
        author_list = ast.literal_eval(author_string)
        if isinstance(author_list, list):
            recoded_author_list = [string.capwords(_author.encode('ascii', 'ignore').decode('UTF-8')) for _author in author_list]
            return str(recoded_author_list)
    except Exception:
        # print(e)
        pass
    return author_string


def process_citation_counts(citation_count_string):
    """Ensure that this is always NONE or NUMERIC."""
    try:
        if not citation_count_string.isnumeric():
            return None
        else:
            return citation_count_string
    except Exception:
        return None


def process_keywords(keywords_string):
    """
    Convert utf-8 characters to ascii  so that they are searchable via a keyboard.

    (will result in data loss but ignore errors)
    """
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
            processed_keywords_list = [_clean_string(kw) for kw in processed_keywords_list]

            # Remove weird phrases in the Keyword that sometimes happens based on how it's maintained on the Publisher's website.
            _interim_processed_list = []
            for kw in processed_keywords_list:
                for regex in config.keyword_patterns_to_remove:
                    kw = re.sub(regex, "", kw)
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
    except Exception:
        # print(e)
        pass
    return None


def get_post_processed_data(config: Config, force: bool = False) -> SqliteDict:
    """Process fields and return them."""
    if force or not config.path_output.exists():
        # Read it
        papers_db = SqliteDict(config.path_output)

        author_processed = []
        keywords_processed = []
        citation_count_processed = []
        abstract_processed = []
        title_processed = []

        for index, row in tqdm(papers_db.items(), desc="Papers", total=len(papers_db)):
            # Process authors
            author_processed.append(process_authors(row["author"]))

            # Process keywords
            keywords_processed.append(process_keywords(row["keywords"]))

            # Process citation counts
            citation_count_processed.append(process_citation_counts(row["citation_count"]))

            # Process abstract
            abstract_processed.append(process_abstract(row["abstract"]))

            # Process titles
            title_processed.append(process_title(row["title"]))

        papers_db.close()

        # Commit all the data to db
        scraped_input_db = SqliteDict(config.path_postprocessing_output)
        scraped_input_db["author_processed"] = author_processed
        scraped_input_db["keywords_processed"] = keywords_processed
        scraped_input_db["citation_count_processed"] = citation_count_processed
        scraped_input_db["abstract_processed"] = abstract_processed
        scraped_input_db["title_processed"] = title_processed

        # Save POST-PROCESSED FILE
        scraped_input_db.commit()
    else:
        scraped_input_db = SqliteDict(config.path_postprocessing_output)

    return scraped_input_db
