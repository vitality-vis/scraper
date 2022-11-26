import ast
import re
import time
from pathlib import Path

import lxml.etree as ET
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sqlitedict import SqliteDict
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

from paperscraper.config import Config, config
from paperscraper.scrapers.abstracts import get_abstract
from paperscraper.scrapers.citations import get_citation_count
from paperscraper.scrapers.keywords import get_keywords

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

# List sources that are to be processed.
# __publication_src = ["IEEE Visualization"]
__publication_src = list(config.interesting_venues.keys())

# Process only the below scraped STATES
# Possible values: ["Not Scraped", "Error", "No Url"]
__scraper_filter = {
    "keywords": ["Not Scraped", "Error", "No Url"],
    "abstract": ["Not Scraped", "Error", "No Url"],
    "citation_count": ["Not Scraped", "Error", "No Url"],
}


def get_processed_db(force: bool = False) -> Path:
    """
    Clean the raw file (set in config.path_input_raw) and writing it out to config.path_input.

    Function is run only if config.path_input doesn't exsit or if `force` is True.
    """
    if force or not config.path_input.exists():
        logger.info(f"Cleaning data from {config.path_input_raw} into {config.path_input}")
        # This Regular Find+Replace replaces instances of &amp; between <ee></ee> tags with a
        # SPECIAL TAG `%26`. This tag will be replaced back to `&` in the code later on.
        regex_find = r'(<ee>.*)&amp;(.*</ee>)'
        regex_replace = r'\1%26\2'

        with open(config.path_input_raw, "r") as raw_dblp:
            with open(config.path_input, "w") as processed_dblp:
                for line in tqdm(raw_dblp, desc="Raw file line"):

                    # Iterations are needed because re.sub replaces just 1 instance at a time
                    intermediate_result = ""
                    while line != intermediate_result:
                        intermediate_result = line
                        line = re.sub(regex_find, regex_replace, line)

                    processed_dblp.write(line)

    return config.path_input


# TODO: Re-run this if (1) The above list has changed OR (2) There is a NEW DBLP snapshot.
def get_unique_venues(config: Config, force: bool = False) -> SqliteDict:
    """
    Find Unique venues from the DBLP xml.

    Looking ONLY for ["article","inproceedings","incollection"] and ["journal", "booktitle"].
    """
    if force or not config.path_unique_venues.exists():
        unique_sources = SqliteDict(config.path_unique_venues)
        unique_sources.clear()  # empty the db
        logger.info(f"Extracting venues to {config.path_unique_venues}")
        for event, elem in tqdm(ET.iterparse(config.path_input, recover=True), desc="Entry"):
            if elem.tag in ["article", "inproceedings", "incollection"]:
                for child in elem.getchildren():
                    if child.tag in ["journal", "booktitle"]:
                        if child.text not in unique_sources:
                            child_dict = {}
                            child_dict["count"] = 0
                            child_dict["child_tag"] = child.tag
                            child_dict["elem_tag"] = elem.tag
                        else:
                            child_dict = unique_sources[child.text]

                        child_dict["count"] += 1
                        unique_sources[child.text] = child_dict

        logger.debug("Writing to disk")
        # Save it to disk
        unique_sources.commit()
    else:
        logger.info(f"Loading data from {config.path_unique_venues}")
        unique_sources = SqliteDict(config.path_unique_venues)

    return unique_sources


# TODO: Re-run this if
#   (1) The <config.interesting_venues> list has changed or
#   (2) There is a NEW DBLP snapshot.
def get_extracted_data(config: Config, force: bool = False) -> SqliteDict:
    """FILTER the huge dblp_processed.xml file to keep just the data that we are interested in."""
    if force or not config.path_output.exists():
        logger.info(f"Extracting data to {config.path_output}")
        result_list = SqliteDict(config.path_output)
        result_list.clear()  # empty the db
        src_set = set()
        for _idx, (event, elem) in tqdm(enumerate(ET.iterparse(config.path_input, encoding='UTF-8', recover=True)), desc="Entry"):
            obj: dict = {}
            # Initialize the fields that we are going to scrape.
            # TODO: Update these if more fields are added.
            obj["abstract"] = "Not Scraped"
            obj["keywords"] = "Not Scraped"
            obj["citation_count"] = "Not Scraped"
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
                    obj[child.tag] = child.text  # title, year, pgs

                # Only consider adding entries from the source defined above
                if (child.text in config.interesting_venues and child.tag == config.interesting_venues[child.text]["sourcetype"]):
                    obj["source"] = child.text
                    to_add = True
                    if child.text not in src_set:
                        src_set.add(child.text)
                        logger.debug(f"Adding source: {child.text}")

            if to_add:
                result_list[_idx] = obj

            # Periodically commiting stuff
            if _idx % 100 == 0:
                result_list.commit()

        logger.debug("Writing to disk")
        # Save to disk
        result_list.commit()
    else:
        logger.info(f"Loading data from {config.path_output}")
        result_list = SqliteDict(config.path_output)

    return result_list


# get a new headless Chrome driver
def _get_webdriver_instance():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.binary_location = config.path_chromeoptions_binary
    # driver = webdriver.chrome(executable_path=config.path_chromedriver, chrome_options=chrome_options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              chrome_options=chrome_options)
    # driver.implicitly_wait(10000)
    return driver


def get_processed_data(cofig: Config, force: bool = False) -> SqliteDict:
    """Scrap the Abstracts, Keywords, and Citations."""
    if force or not config.path_output.exists():
        # Get a webdriver instance (Headless Chrome)
        logger.info(f"Processing data to {config.path_output}")
        driver = _get_webdriver_instance()

        # Read the base datafile
        papers_db = SqliteDict(config.path_output)

        # Initialize a log object to analyze the summary of a particular run.
        log_obj: dict = {}

        # Start scraping
        for index, row in tqdm(papers_db.items(), desc="Papers", total=len(papers_db)):

            # ToDo: Keep Checking this high-level filter to minimize iterations.
            if (str(row["abstract"]) in __scraper_filter["abstract"] or
                str(row["keywords"]) in __scraper_filter["keywords"] or
                str(row["citation_count"]) in __scraper_filter["citation_count"]) \
                    and row["source"] in __publication_src:

                if row["source"] not in log_obj:
                    log_obj[row["source"]] = dict()
                    log_obj[row["source"]]["papers"] = 0
                    log_obj[row["source"]]["abstract_parse_errors"] = 0
                    log_obj[row["source"]]["abstract_fetch_errors"] = 0
                    log_obj[row["source"]]["abstract_errors"] = 0
                    log_obj[row["source"]]["keyword_parse_errors"] = 0
                    log_obj[row["source"]]["keyword_fetch_errors"] = 0
                    log_obj[row["source"]]["keyword_errors"] = 0
                    log_obj[row["source"]]["no_of_citations_parse_errors"] = 0
                    log_obj[row["source"]]["no_of_citations_fetch_errors"] = 0
                    log_obj[row["source"]]["no_of_citations_errors"] = 0

                # Increment no of papers
                log_obj[row["source"]]["papers"] += 1

                # Get the URLs
                urls = []
                try:
                    urls = ast.literal_eval(row["ee"])
                except Exception:
                    # If not ee, check url.
                    # But, this doesn't have HTTP/HTTPS it seems to be following some Relative Paths from a
                    # BaseURL that is unknown. Hence, it will fail 99% of the times.
                    try:
                        urls = ast.literal_eval(row["url"])
                    except Exception:
                        pass

                # If there is No url OR If the URL begins with a db/, continue.
                if len(urls) == 0 or urls[0].startswith("db/"):
                    row['abstract'] = "No Url"
                    row['abstract'] = "No Url"
                    row['abstract'] = "No Url"
                    papers_db[index] = row
                    logger.error(str(index) + " [No URL]: " + str(row["title"]))
                    continue

                # ABSTRACT
                abstract_soup = None
                try:
                    driver.get(urls[0])

                    # Delay to ensure routings are complete, page renders
                    time.sleep(1.5)

                    # Initialize the Soup object
                    abstract_soup = BeautifulSoup(driver.page_source, 'lxml')

                except Exception as e:
                    logger.error('Abstract: ' + str(e))

                if abstract_soup is not None:
                    is_abstract = False
                    for publisher in config.interesting_venues[row["source"]]["publishers"]:
                        abstract = get_abstract(publisher, abstract_soup)
                        if abstract is not None:
                            row['abstract'] = abstract
                            logger.info(str(index) + " [Success][Abstract] " + str(urls[0]) + " " + str(abstract)[:50])
                            is_abstract = True
                            break

                    if not is_abstract:
                        row['abstract'] = "Error"
                        logger.error(str(index) + " [Abstract Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                        log_obj[row["source"]]["abstract_parse_errors"] += 1
                        log_obj[row["source"]]["abstract_errors"] += 1

                else:
                    row['abstract'] = "Error"
                    logger.error(str(index) + " [Abstract URL Fetch]: " + str(row["source"]))
                    log_obj[row["source"]]["abstract_fetch_errors"] += 1
                    log_obj[row["source"]]["abstract_errors"] += 1

                # No. of CITATIONS
                citation_soup = abstract_soup
                if citation_soup is not None:
                    is_citation = False
                    for publisher in config.interesting_venues[row["source"]]["publishers"]:
                        citation_count = get_citation_count(publisher, citation_soup)
                        if citation_count is not None:
                            row['citation_count'] = citation_count
                            logger.info(str(index) + " [Success][Citation Count] " + str(urls[0]) + " " + str(citation_count))
                            is_citation = True
                            break

                    if not is_citation:
                        row['citation_count'] = "Error"
                        logger.error(str(index) + " [Citation Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                        log_obj[row["source"]]["no_of_citations_parse_errors"] += 1
                        log_obj[row["source"]]["no_of_citations_errors"] += 1

                else:
                    row['citation_count'] = "Error"
                    logger.error(str(index) + " [Citation Count URL Fetch]: " + str(row["source"]))
                    log_obj[row["source"]]["no_of_citations_fetch_errors"] += 1
                    log_obj[row["source"]]["no_of_citations_errors"] += 1

                # KEYWORDS
                # Redirect to a different URL to fetch KEYWORDS in some cases.
                is_keyword = False
                current_url = driver.current_url
                for publisher in config.interesting_venues[row["source"]]["publishers"]:
                    try:
                        if publisher == "ieee_explore":
                            driver.get(current_url + "/keywords#keywords")
                        elif publisher == "eurographics_digital_library":
                            driver.get(current_url + "?show=full")
                        else:
                            driver.get(current_url)

                        # Delay to ensure routings are complete, page renders
                        time.sleep(1.5)

                        # Initialize the Soup object
                        keyword_soup = BeautifulSoup(driver.page_source, 'lxml')

                        if keyword_soup is not None:
                            keywords_list = get_keywords(publisher, keyword_soup)
                            if keywords_list is not None:
                                row['keywords'] = keywords_list
                                logger.info(str(index) + " [Success][Keywords] " + str(urls[0]) + " " + str(keywords_list))
                                is_keyword = True
                                break
                        else:
                            row['keywords'] = "Error"
                            logger.error(str(index) + " [Keywords URL Fetch]: " + str(row["source"]))
                            log_obj[row["source"]]["keyword_fetch_errors"] += 1
                            log_obj[row["source"]]["keyword_errors"] += 1

                    except Exception:
                        pass

                if not is_keyword:
                    row['keywords'] = "Error"
                    logger.error(str(index) + " [Error][Keywords Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                    log_obj[row["source"]]["keyword_parse_errors"] += 1
                    log_obj[row["source"]]["keyword_errors"] += 1

                papers_db[index] = row

                if index % 100 == 100:
                    papers_db.commit()

        # Persist the paper file
        papers_db.commit()
        logger.i("scraped papers saved to disk.")

        # Persist Logs
        df_logs = pd.DataFrame.from_dict(log_obj, orient="index")
        logger.i(log_obj)
        df_logs.to_csv(config.path_logfile, sep='\t', header=True)
    else:
        logger.info(f"Loading processed data from {config.path_output}")
        papers_db = SqliteDict(config.path_output)

    return papers_db
