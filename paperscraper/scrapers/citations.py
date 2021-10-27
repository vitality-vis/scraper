import re

def ieee_explore(soup):
    try:
        # Check if it is indeed the Citation count and NOT the number of Full Text Views
        parent_div = soup.find("div", class_="document-banner-metric-container")
        if parent_div:
            for citation_parent_btn in parent_div.findChildren('button', class_="document-banner-metric"):
                citation_div = citation_parent_btn.find('div', class_="document-banner-metric-count")
                # Check if it is indeed the Citation count and NOT the number of Full Text Views
                if citation_div:
                    paper_text_div = citation_div.find_next('div')
                    if paper_text_div.text == "Paper":
                        citation_text_div = paper_text_div.find_next('div')
                        if citation_text_div.text in ["Citation", "Citations"]:
                            # Now, it's confirmed that this button is indeed the citation button
                            citation_count = citation_div.text
                            return str(citation_count)
    except Exception as e:
        print(e)
    return None


def eurographics_digital_library(soup):
    return None


def acm_digital_library(soup):
    try:
        grandparent_ul = soup\
            .find("div", class_="issue-item__footer")\
            .find("div", class_="issue-item__footer-info")\
            .find("div", class_="tooltip")\
            .find('ul', class_="rlist--inline")
        if grandparent_ul:
            for parent_li in grandparent_ul.findChildren('li'):
                citation_span = parent_li.find("span", class_="citation")
                if citation_span:
                    for citation_child in citation_span.findChildren("span"):
                        return str(citation_child.text)
    except Exception as e:
        print(e)

    return None


def graphics_interface_proceedings(soup):
    return None


def springer_v2(soup):
    try:
        citation_span = soup.find("span", id="chaptercitations-count-number")
        if citation_span:
            return str(citation_span.text)
        else:
            citation_span = soup.find("span", id="bookcitations-count-number")
            if citation_span:
                return str(citation_span.text)
    except Exception as e:
        print(e)
    return None


def springer_v1(soup):
    try:
        citation_ul = soup.find("ul", class_="c-article-metrics-bar u-list-reset")
        if citation_ul:
            for citation_parent_li in citation_ul.findChildren('li', class_="c-article-metrics-bar__item"):
                citation_parent_p = citation_parent_li.find('p', class_="c-article-metrics-bar__count")
                if citation_parent_p:
                    label_span = citation_parent_p.find('span', class_="c-article-metrics-bar__label")
                    if label_span.text in ["Citation", "Citations"]:
                        return str(citation_parent_p.contents[0])
    except Exception as e:
        print(e)
    return None


def wiley_online_library(soup):
    try:
        parent_div = soup.find('div', class_="cited-by-count")
        citation_span = parent_div.find('span')
        citation_a = citation_span.find('a')
        return str(citation_a.text)
    except Exception as e:
        print(e)
    return None


def cogsci(soup):
    return None


def scitepress(soup):
    return None


def dagstuhl(soup):
    return None


def scienceopen(soup):
    try:
        citation_label = soup.find("div", class_="so-stats2-label", text=re.compile('cited by'))
        if citation_label:
            citation_div = citation_label.find_previous("div", class_="so-stats2-num")
            return citation_div.text
    except Exception as e:
        print(e)

    return None


def aaai(soup):
    return None

def get_citation_count(publisher, soup):
    citation_count = None

    if publisher == "acm_digital_library":
        citation_count = acm_digital_library(soup)

    elif publisher == "graphics_interface_proceedings":
        citation_count = graphics_interface_proceedings(soup)

    elif publisher == "ieee_explore":
        citation_count = ieee_explore(soup)

    elif publisher == "cogsci":
        citation_count = cogsci(soup)

    elif publisher == "springer_v1":
        citation_count = springer_v1(soup)

    elif publisher == "springer_v2":
        citation_count = springer_v2(soup)

    elif publisher == "scitepress":
        citation_count = scitepress(soup)

    elif publisher == "scienceopen":
        citation_count = scienceopen(soup)

    elif publisher == "eurographics_digital_library":
        citation_count = eurographics_digital_library(soup)

    elif publisher == "wiley_online_library":
        citation_count = wiley_online_library(soup)

    elif publisher == "dagstuhl":
        citation_count = dagstuhl(soup)

    elif publisher == "aaai":
        citation_count = aaai(soup)

    return citation_count
