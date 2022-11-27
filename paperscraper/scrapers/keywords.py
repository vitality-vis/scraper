import re
from loguru import logger

regex = re.compile(r'[\n\r\t]')


def acm_digital_library(soup):
    try:
        # TODO: Get keyoards by clicking on the citation linke (soup.select('a[data-title="Export Citation"]'))
        # Then using the the ActionChains from selenium to click, parse the bib result and get keywords
        keywords = set()
        keywords_parent_ol = soup.find('ol', class_="rlist organizational-chart")
        keywords_divs = keywords_parent_ol.findChildren('div', recursive=True)
        for kw_parent in keywords_divs:
            kw = kw_parent.text
            keywords.add(regex.sub("", kw.split(",")[0]))
        return list(keywords)
    except Exception as e:
        logger.error(e)
    return []


def graphics_interface_proceedings(soup):
    return []


def ieee_explore(soup):
    try:
        keywords = set()
        ggp_ul = soup.find('ul', class_="doc-keywords-list stats-keywords-list")
        gp_li = ggp_ul.findChildren("li", class_="doc-keywords-list-item", recursive=False)
        for p_li in gp_li:
            if p_li.find('strong').text in ["IEEE Keywords", "INSPEC: Controlled Indexing", "INSPEC: Non-Controlled Indexing", "MeSH Terms"]:
                for keywords_l in p_li.find('ul').findChildren("li", recursive=False):
                    a_tag = keywords_l.find("a", class_="stats-keywords-list-item")
                    if a_tag is not None:
                        keywords.add(str(regex.sub("", a_tag.text.split(",")[0])))
                    else:
                        keywords.add(str(regex.sub("", str(keywords_l.text).split(",")[0])))
        return list(keywords)
    except Exception as e:
        logger.error(e)
    return []


def eurographics_digital_library(soup):
    try:
        keywords_set = set()
        p_tablebody = soup.find('table', class_="detailtable").find("tbody")
        p_trs = p_tablebody.findChildren('tr')
        for tr in p_trs:
            label = tr.find("td", class_="label-cell")
            if label.text == "dc.subject":
                keywords = tr.find("td", class_="word-break")
                # e.g. CASE 1: ['Categories and Subject Descriptors (according to ACM CCS): I.4.1 [Image Processing and Computer Vision]: Enhancement-Filtering I.3.3 [Computer Graphics]: Picture/Image Generation-Bitmap and framebuffer operations']
                # e.g. CASE 2 [TODO: Not taken care of yet] Categories and Subject Descriptors (according to ACM CCS): Information Interfaces And Presentation (e.g., HCI) [H.5.2]: User Interfaces-Graphical user interfaces (GUI)
                # Step 1: Remove annoying substrings
                # Step 2: Choose to take ONLY Categories, not the Subject Descriptors > Write a REGEX to take substrings between [].
                # Step 3: Split the string by , or ; or :
                to_replaces = ["CCS Concepts", "Categories and Subject Descriptors", "Categories and subject descriptors", "Categories and Subject Descriptors (according to ACM CCS)", "according to ACM CCS"]
                keywords_str = keywords.text
                for to_replace in to_replaces:
                    keywords_str = keywords_str.replace(to_replace, "")
                keywords_extracted = re.findall(r'\[(.*?)\]', keywords_str)
                if keywords_extracted:
                    keywords_set.update(keywords_extracted)
                else:
                    keywords_set.update(re.split(',|:|;', keywords_str))
        return list(keywords_set)
    except Exception as e:
        logger.error(e)
    return []


def springer_v2(soup):
    try:
        keywords = set()
        keywords_parent_div = soup.find('div', class_="KeywordGroup")
        keywords_span = keywords_parent_div.findChildren("span", class_="Keyword")
        for k in keywords_span:
            keywords.add(k.text)
        return list(keywords)
    except Exception as e:
        logger.error(e)
    return []


def dagstuhl(soup):
    try:
        keywords_label = soup.find('b', text="Keywords:")
        keywords_parent_font = keywords_label.parent
        keywords_parent_td = keywords_parent_font.parent
        keywords_font = keywords_parent_td.find_next('td').find_next('td').find("font")
        if keywords_font is not None:
            return re.split(',', keywords_font.text)
    except Exception as e:
        logger.error(e)
    return []


def springer_v1(soup):
    try:
        keywords = set()
        keywords_parent_section = soup.find('ul', class_="c-article-subject-list")
        keywords_li = keywords_parent_section.findChildren("li", class_="c-article-subject-list__subject")
        for k in keywords_li:
            kw = k.find("span").text
            keywords.add(str(regex.sub("", kw)).strip())
        return list(keywords)
    except Exception as e:
        logger.error(e)
    return []


def wiley_online_library(soup):
    try:
        keywords_parent_section = soup.find('section', class_="keywords")
        keywords_ul = keywords_parent_section.find('ul')
        keywords_lis = keywords_ul.findChildren("li")
        keywords_set = set()
        for keywords_li in keywords_lis:

            # e.g. Case 1: "[3.1.1] Human-Centered Computing" and so on
            # e.g. Case 2: CCS Concepts don't have '[' and ']' but they have strings such as "• Human‐centered computing → Graph drawings"
            # Step 1: Remove annoying substrings
            # Step 2: Choose to take ONLY Categories, not the Subject Descriptors > Write a REGEX to take substrings between [].
            # Step 3: Split the string by , or ; or :
            to_replaces = ["CCS Concepts", "Categories and Subject Descriptors", "Categories and subject descriptors", "Categories and Subject Descriptors (according to ACM CCS)", "according to ACM CCS"]
            keywords_str = keywords_li.find("a").text
            for to_replace in to_replaces:
                keywords_str = keywords_str.replace(to_replace, "")
            keywords_extracted = re.findall(r'\[(.*?)\]', keywords_str)
            if keywords_extracted:
                keywords_set.update(keywords_extracted)
            else:
                # CCS Concepts don't have '[' and ']' but they have strings such as "• Human‐centered computing → Graph drawings"
                regex_find = r'•(.*)→(.*)'
                regex_replace = r'\1;\2' # set the delimiter to either , : ; (as is used below to split)
                keywords_str = re.sub(regex_find, regex_replace, keywords_str)
                keywords_set.update(re.split(',|:|;', keywords_str))

        return list(keywords_set)
    except Exception as e:
        logger.error(e)
    return []


def cogsci(soup):
    return []


def scitepress(soup):
    try:
        keywords_set = set()
        keywords_span = soup.find('span', id="ContentPlaceHolder1_LinkPaperPage_LinkPaperContent_LabelPublicationDetailKeywords")
        for kw in keywords_span.text.split(","):
            keywords_set.add(kw)
        return list(keywords_set)
    except Exception as e:
        logger.error(e)
    return []


def scienceopen(soup):
    try:
        keywords_set = set()
        for span_label in soup.find_all('span', class_="so-metadata-label"):
            if "Keywords" in span_label.text:
                for keyword_a in span_label.find_next_siblings('a'):
                    keywords_set.add(keyword_a.text)
        return list(keywords_set)
    except Exception as e:
        pass
    return []


def aaai(soup):
    return []


def get_keywords(publisher, soup):
    keywords_list = None
    if publisher == "acm_digital_library":
        keywords_list = acm_digital_library(soup)

    elif publisher == "graphics_interface_proceedings":
        keywords_list = graphics_interface_proceedings(soup)

    elif publisher == "ieee_explore":
        keywords_list = ieee_explore(soup)

    elif publisher == "cogsci":
        keywords_list = cogsci(soup)

    elif publisher == "springer_v1":
        keywords_list = springer_v1(soup)

    elif publisher == "springer_v2":
        keywords_list = springer_v2(soup)

    elif publisher == "scitepress":
        keywords_list = scitepress(soup)

    elif publisher == "scienceopen":
        keywords_list = scienceopen(soup)

    elif publisher == "eurographics_digital_library":
        keywords_list = eurographics_digital_library(soup)

    elif publisher == "wiley_online_library":
        keywords_list = wiley_online_library(soup)

    elif publisher == "dagstuhl":
        keywords_list = dagstuhl(soup)

    elif publisher == "aaai":
        keywords_list = aaai(soup)

    return None if len(keywords_list) == 0 else keywords_list
