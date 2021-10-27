import re


def acm_digital_library(soup):
    try:
        abstract_parent_div = soup.find('div', class_="abstractSection abstractInFull")
        abstract_p = abstract_parent_div.find('p')
        return abstract_p.text
    except Exception as e:
        print(e)
    return None


def graphics_interface_proceedings(soup):
    try:
        abstract_h3 = soup.find("h3", text=re.compile('Abstract'))
        abstract_p = abstract_h3.find_next('p')
        return abstract_p.text
    except Exception as e:
        pass
    return None


def ieee_explore(soup):
    try:
        abstract_parent_div = soup.find('div', class_="abstract-text")
        if abstract_parent_div:
            abstract_div = abstract_parent_div.find('strong').find_next('div')
        else:
            abstract_div = soup.find('div', class_="article-content mt-lg")
            if abstract_div is None:
                abstract_div = soup.findAll('h5', text='Abstract')[0].find_next('div')
        return abstract_div.text
    except Exception as e:
        print(e)
    return None


def scitepress(soup):
    try:
        abstract_span = soup.find('span', id="ContentPlaceHolder1_LinkPaperPage_LinkPaperContent_LabelAbstract")
        return abstract_span.text
    except Exception as e:
        print(e)
    return None


def scienceopen(soup):
    try:
        for header in soup.find_all('header', class_="so-layout-section-header"):
            h3 = header.find("h3", class_="so-layout-section-title")
            if "Abstract" in h3.text:
                abstract_div = header.find_next("div", class_="so-d")
                abstract_p = abstract_div.find('p', class_="first")
                return abstract_p.text
    except Exception as e:
        print(e)
    return None


def eurographics_digital_library(soup):
    try:
        abstract_parent_div = soup.find('div', class_="simple-item-view-description item-page-field-wrapper table")
        abstract_div = abstract_parent_div.find('h5').find_next('div')
        return abstract_div.text
    except Exception as e:
        print(e)
    return None


def springer_v1(soup):
    try:
        abstract_parent_div = soup.find('div', class_="c-article-section__content")
        abstract_p = abstract_parent_div.find('p')
        return abstract_p.text
    except Exception as e:
        print(e)
    return None


def springer_v2(soup):
    try:
        abstract_parent_section = soup.find('section', class_="Abstract")
        abstract_p = abstract_parent_section.find("p", class_="Para")
        if abstract_p is None:
            nearest_tag = abstract_parent_section.find('h3')
            if nearest_tag is None:
                nearest_tag = abstract_parent_section.find('h2')
            abstract_p = nearest_tag.find_next('p')
        return abstract_p.text
    except Exception as e:
        print(e)
    return None


def wiley_online_library(soup):
    try:
        abstract_parent_section = soup.find('div', class_="article-section__content")
        abstract_p = abstract_parent_section.find('p')
        return abstract_p.text
    except Exception as e:
        print(e)
    return None


def dagstuhl(soup):
    try:
        abstract_div = soup.find('div', itemprop="about")
        if abstract_div is not None:
            if abstract_div.text.strip().startswith("Abstract"):
                return abstract_div.text.strip()[len("Abstract"):]
    except Exception as e:
        print(e)
    return None


def cogsci(soup):
    try:
        abstract_p = soup.find('p', id="abstract")
        if abstract_p is not None:
            return abstract_p.text
        else:
            abstract_span = soup.find('span', class_="subAbstract")
            if abstract_span is not None:
                abstract = abstract_span.text
                if abstract.startswith("Abstract"):
                    return abstract.replace("Abstract", "", 1)
                return abstract
            else:
                blockquotes = soup.findAll('blockquote')
                if blockquotes is not None:
                    for blockquote in blockquotes:
                        if len(blockquote.findChildren()) == 0:
                            return blockquote.text
    except Exception as e:
        print(e)
    return None


def aaai(soup):
    try:
        abstract_div = soup.find("div", id="abstract")
        if abstract_div:
            return abstract_div.find("p").find_next("p").text
    except Exception as e:
        print(e)
    return None


def get_abstract(publisher, soup):
    abstract = None
    if publisher == "acm_digital_library":
        abstract = acm_digital_library(soup)

    elif publisher == "graphics_interface_proceedings":
        abstract = graphics_interface_proceedings(soup)

    elif publisher == "ieee_explore":
        abstract = ieee_explore(soup)

    elif publisher == "cogsci":
        abstract = cogsci(soup)

    elif publisher == "springer_v1":
        abstract = springer_v1(soup)

    elif publisher == "springer_v2":
        abstract = springer_v2(soup)

    elif publisher == "scitepress":
        abstract = scitepress(soup)

    elif publisher == "scienceopen":
        abstract = scienceopen(soup)

    elif publisher == "eurographics_digital_library":
        abstract = eurographics_digital_library(soup)

    elif publisher == "wiley_online_library":
        abstract = wiley_online_library(soup)

    elif publisher == "dagstuhl":
        abstract = dagstuhl(soup)

    elif publisher == "aaai":
        abstract = aaai(soup)

    return abstract
