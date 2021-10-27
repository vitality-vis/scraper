# External packages
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import sys
import os
import ast

# Internal modules
from paperscraper.scrapers.abstracts import get_abstract
from paperscraper.scrapers.keywords import get_keywords
from paperscraper.scrapers.citations import get_citation_count
import paperscraper.config as config


# get a new headless Chrome driver
def get_webdriver_instance():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = config.path_chromeoptions_binary
    driver = webdriver.Chrome(executable_path=config.path_chromedriver, chrome_options=chrome_options)
    # driver.implicitly_wait(10000)
    return driver


def main():
    # Get a webdriver instance (Headless Chrome)
    driver = get_webdriver_instance()

    # Read the base datafile
    df_papers = pd.read_csv(config.path_output, sep='\t', header=0)

    # Initialize a log object to analyze the summary of a particular run.
    log_obj = dict()

    # Start scraping
    for index, row in df_papers.iterrows():

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
                print(str(index) + " [No URL]: " + row["title"])
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
                print('Abstract: ' + str(e))

            if abstract_soup is not None:
                is_abstract = False
                for publisher in config.interesting_venues[row["source"]]["publishers"]:
                    abstract = get_abstract(publisher, abstract_soup)
                    if abstract is not None:
                        df_papers.at[index, 'abstract'] = abstract
                        print(str(index) + " [Success][Abstract] " + str(urls[0]) + " " + str(abstract)[:50])
                        is_abstract = True
                        break

                if not is_abstract:
                    df_papers.at[index, 'abstract'] = "Error"
                    print(str(index) + " [Error][Abstract Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                    log_obj[row["source"]]["abstract_parse_errors"] += 1
                    log_obj[row["source"]]["abstract_errors"] += 1

            else:
                df_papers.at[index, 'abstract'] = "Error"
                print(str(index) + " [Error][Abstract URL Fetch]: " + str(row["source"]))
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
                        print(str(index) + " [Success][Citation Count] " + str(urls[0]) + " " + str(citation_count))
                        is_citation = True
                        break

                if not is_citation:
                    df_papers.at[index, 'citation_count'] = "Error"
                    print(str(index) + " [Error][Citation Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                    log_obj[row["source"]]["no_of_citations_parse_errors"] += 1
                    log_obj[row["source"]]["no_of_citations_errors"] += 1

            else:
                df_papers.at[index, 'citation_count'] = "Error"
                print(str(index) + " [Error][Citation Count URL Fetch]: " + str(row["source"]))
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
                            print(str(index) + " [Success][Keywords] " + str(urls[0]) + " " + str(keywords_list))
                            is_keyword = True
                            break
                    else:
                        df_papers.at[index, 'keywords'] = "Error"
                        print(str(index) + " [Error][Keywords URL Fetch]: " + str(row["source"]))
                        log_obj[row["source"]]["keyword_fetch_errors"] += 1
                        log_obj[row["source"]]["keyword_errors"] += 1

                except Exception as e:
                    pass

            if not is_keyword:
                df_papers.at[index, 'keywords'] = "Error"
                print(str(index) + " [Error][Keywords Parse]: " + str(urls[0]) + " : " + str(row["source"]))
                log_obj[row["source"]]["keyword_parse_errors"] += 1
                log_obj[row["source"]]["keyword_errors"] += 1

    # Persist the paper file
    print("---------------")
    df_papers.to_csv(config.path_output, sep='\t', header=True, index=False)
    print("scraped papers saved to disk.")

    # Persist Logs
    df_logs = pd.DataFrame.from_dict(log_obj, orient="index")
    print("---------------")
    print("logs saved to disk.")
    print(log_obj)
    df_logs.to_csv(config.path_logfile, sep='\t', header=True)


if __name__ == "__main__":

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

    # Scrap the Abstracts, Keywords, and Citations
    main()

    sys.exit(os.EX_OK) # code 0, all ok
