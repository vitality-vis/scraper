import re
from pathlib import Path
import lxml.etree as ET
import pandas as pd
from loguru import logger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import ast
import time

import paperscraper.config as config
from paperscraper.scrapers.abstracts import get_abstract
from paperscraper.scrapers.keywords import get_keywords
from paperscraper.scrapers.citations import get_citation_count

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


def get_processed_db(force:bool=False) -> Path:
    if force or not config.path_input.exists():
        logger.info(f"Cleaning data from {config.path_input_raw} into {config.path_input}")
        # This Regular Find+Replace replaces instances of &amp; between <ee></ee> tags with a SPECIAL TAG `%26`. This tag will be replaced back to `&` in the code later on.
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


# Find Unique venues from the DBLP xml looking ONLY for ["article","inproceedings","incollection"] and ["journal", "booktitle"].
# TODO: Re-run this if (1) The above list has changed OR (2) There is a NEW DBLP snapshot.
def get_unique_venues(force:bool=False) -> pd.DataFrame:
    if force or not config.path_unique_venues.exists():
        logger.info(f"Extracting venues to {config.path_unique_venues}")
        unique_sources = dict()
        for event, elem in tqdm(ET.iterparse(config.path_input, recover=True), desc="Entry"):
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

        logger.debug("Writing to disk")
        # Save it to disk
        df_unique_sources.to_csv(config.path_unique_venues, header=True, sep='\t')
    else:
        logger.info(f"Loading data from {config.path_unique_venues}")
        df_unique_sources = pd.read_csv(config.path_unique_venues, header=0, sep='\t')

    return df_unique_sources


# FILTER the huge dblp_processed.xml file to keep just the data that we are interested in.
# TODO: Re-run this if (1) The <config.interesting_venues> list has changed or (2) There is a NEW DBLP snapshot .
def get_extracted_data(force:bool=False) -> pd.DataFrame:
    if force or not config.path_output.exists():
        logger.info(f"Extracting data to {config.path_output}")
        result_list = list()
        src_set = set()
        for event, elem in tqdm(ET.iterparse(config.path_input, encoding='UTF-8', recover=True), desc="Entry"):
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
                        logger.debug(f"Adding source: {child.text}")

            if to_add:
                result_list.append(obj)

        # Create a DataFrame
        df_result_list = pd.DataFrame(result_list)

        # Initialize the fields that we are going to scrape.
        # TODO: Update these if more fields are added.
        df_result_list["abstract"] = "Not Scraped"
        df_result_list["keywords"] = "Not Scraped"
        df_result_list["citation_count"] = "Not Scraped"

        logger.debug("Writing to disk")
        # Save to disk
        df_result_list.to_csv(config.path_output, sep='\t', header=True)
    else:
        logger.info(f"Loading data from {config.path_output}")
        df_result_list = pd.read_csv(config.path_output, sep='\t', header=0)

    return df_result_list


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


# Scrap the Abstracts, Keywords, and Citations
def get_processed_data(force:bool=False) -> pd.DataFrame:
    if force or not config.path_output.exists():
        # Get a webdriver instance (Headless Chrome)
        logger.info(f"Processing data to {config.path_output}")
        driver = _get_webdriver_instance()

        # Read the base datafile
        df_papers = pd.read_csv(config.path_output, sep='\t', header=0)

        # Initialize a log object to analyze the summary of a particular run.
        log_obj = dict()

        # Start scraping
        for index, row in tqdm(df_papers.iterrows(), desc="Papers", total=df_papers.shape[0]):

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
                except Exception as e:
                    # If not ee, check url.
                    # But, this doesn't have HTTP/HTTPS it seems to be following some Relative Paths from a BaseURL that is unknown.
                    # Hence, it will fail 99% of the times.
                    try:
                        urls = ast.literal_eval(row["url"])
                    except:
                        pass

                # If there is No url OR If the URL begins with a db/, continue.
                if len(urls) == 0 or urls[0].startswith("db/"):
                    df_papers.at[index, 'abstract'] = "No Url"
                    df_papers.at[index, 'keywords'] = "No Url"
                    df_papers.at[index, 'citation_count'] = "No Url"
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
                            df_papers.at[index, 'abstract'] = abstract
                            logger.info(str(index) + " [Success][Abstract] " + str(urls[0]) + " " + str(abstract)[:50])
                            is_abstract = True
                            break

                    if not is_abstract:
                        df_papers.at[index, 'abstract'] = "Error"
                        logger.error(str(index) + " [Abstract Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                        log_obj[row["source"]]["abstract_parse_errors"] += 1
                        log_obj[row["source"]]["abstract_errors"] += 1

                else:
                    df_papers.at[index, 'abstract'] = "Error"
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
                            df_papers.at[index, 'citation_count'] = citation_count
                            logger.info(str(index) + " [Success][Citation Count] " + str(urls[0]) + " " + str(citation_count))
                            is_citation = True
                            break

                    if not is_citation:
                        df_papers.at[index, 'citation_count'] = "Error"
                        logger.error(str(index) + " [Citation Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                        log_obj[row["source"]]["no_of_citations_parse_errors"] += 1
                        log_obj[row["source"]]["no_of_citations_errors"] += 1

                else:
                    df_papers.at[index, 'citation_count'] = "Error"
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
                            driver.get(current_url+ "/keywords#keywords")
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
                                df_papers.at[index, 'keywords'] = keywords_list
                                logger.info(str(index) + " [Success][Keywords] " + str(urls[0]) + " " + str(keywords_list))
                                is_keyword = True
                                break
                        else:
                            df_papers.at[index, 'keywords'] = "Error"
                            logger.error(str(index) + " [Keywords URL Fetch]: " + str(row["source"]))
                            log_obj[row["source"]]["keyword_fetch_errors"] += 1
                            log_obj[row["source"]]["keyword_errors"] += 1

                    except Exception as e:
                        pass

                if not is_keyword:
                    df_papers.at[index, 'keywords'] = "Error"
                    logger.error(str(index) + " [Error][Keywords Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                    log_obj[row["source"]]["keyword_parse_errors"] += 1
                    log_obj[row["source"]]["keyword_errors"] += 1

        # Persist the paper file
        df_papers.to_csv(config.path_output, sep='\t', header=True, index=False)
        logger.i("scraped papers saved to disk.")

        # Persist Logs
        df_logs = pd.DataFrame.from_dict(log_obj, orient="index")
        logger.i(log_obj)
        df_logs.to_csv(config.path_logfile, sep='\t', header=True)
    else:
        logger.info(f"Loading processed data from {config.path_output}")
        df_papers = pd.read_csv(config.path_output, sep='\t', header=0)

    return df_papers
