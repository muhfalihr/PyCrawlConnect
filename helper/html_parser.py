from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


class HtmlParser:
    """
    Provides a framework for parsing HTML content using different parsing libraries. 
    Offers flexibility in choosing parsing methods based on preferences or specific needs.
    """

    def __init__(self):
        pass

    def bs4_parser(self, html, selector):
        """
        Employs the BeautifulSoup library for parsing.
        Parses the provided HTML string using the "lxml" parser.
        Applies the specified selector to extract relevant elements.
        Handles potential exceptions and returns the parsed results.
        """
        result = None
        try:
            html = BeautifulSoup(html, "lxml")
            result = html.select(selector)
        except Exception as e:
            print(e)
        finally:
            return result

    def pyq_parser(self, html, selector):
        """
        Utilizes the PyQuery library for parsing.
        Processes the HTML string using PyQuery's syntax.
        Applies the selector to select desired elements.
        Manages exceptions and returns the extracted data.
        """
        result = None
        try:
            html = pq(html)
            result = html(selector)
        except Exception as e:
            print(e)
        finally:
            return result
