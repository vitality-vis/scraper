# VitaLITy - scraper

## Coming soon: Documentation on how to write new scrapers (for new venues)

## Download DBLP
- Go to the [DBLP releases](https://dblp.org/xml/release/) page and download a recent release (e.g., dblp-2020-11-01.xml.gz.md5) 
- Unzip it (dblp-2020-11-01.xml) and copy it into `/assets/data/`

## Scripts

### `config.py`
This file defines various configurations such as path to data, path to output file, the venues of interest, etc.

### `0-preprocess.py`
The DBLP file consists of `&amp;` which causes some issues with the lxml parser. Exec'ing this script replaces instances of `&amp;` between `<ee></ee>` tags with a SPECIAL TAG `%26`. This tag will be replaced back to `&` in a later step.

### `1-get_unique_venues.py`
Exec'ing this script iterates through the DBLP dataset and persists a list of venue types (e.g., booktitle, journal) and article types (e.g., inproceedings, articles, incollections).

### `2-init.py`
Exec'ing this script creates a `.tsv` file with the venues of interest (e.g., VIS, CHI) and their details as filtered from the DBLP dataset. Attributes such as `abstract`, `citation_count`, and `keywords` that are scraped in the subsequent step are also initialized here.

### `3-update.py`
Exec'ing this script calls the `abstract`, `citation_count`, and `keywords` scrapers in the `scrapers/` directory and eventually updates the `.tsv` created in the above step.

### `4-postprocess.py`
Exec'ing this file postprocesses authors and keywords for analysis purposes, for e.g., decoding utf-8 author names to an ascii form. 

### `5-get_unique_keywords.py`
Exec'ing this file creates a list of unique keywords.

### `6-get_unique_authors.py`
Exec'ing this file creates a list of unique author names.

### `scrapers/{abstracts,citations,keywords}.py`
These files contain the scraper code to scrape abstracts, citations, and keywords for different venues.


### Note: 
The scrapers access digital libraries (e.g., IEEE Xplore, ACM Digital Library) and download the _abstracts_, _keywords_, and _citationCounts_ for different articles. These data are readily available  and publicly accessible, that is, do not require any subscriptions, be it paid or free. We do not own the rights to the scraped data and make it available for research purpose only. Also, before running the scrapers, please review the bot policies of the target websites (e.g., robot.txt) to not overwhelm their servers and be in violation.