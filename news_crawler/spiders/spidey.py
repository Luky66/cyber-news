# -*- coding: utf-8 -*-
import scrapy


class SpideySpider(scrapy.Spider):
    name = 'spidey'
    start_urls = []

    def start_requests(self):
        for pageIndex, site in enumerate(sites):
            self.start_urls.append( site.url )
            yield self.make_requests_from_url(site.url, {'pageIndex': pageIndex})

    def make_requests_from_url(self, url, meta):
       return scrapy.Request(url, callback=self.parse_feed, dont_filter=True, meta=meta)


    def parse_feed(self, response):
        pageIndex = response.meta['pageIndex']
        requests = []

        for feed in response.css(sites[pageIndex].feed_element_selector):
            for entry in feed.css(sites[pageIndex].entry_element_selector):

                # Construct news element and pass it along

                news = Article(
                    entry.css(sites[pageIndex].title_element_selector+' ::text').extract_first(),
                    entry.css(sites[pageIndex].summary_element_selector+' ::text').extract_first(),
                    response.urljoin(entry.css(sites[pageIndex].entry_link_selector+' ::attr(href)').extract_first()),
                    "",
                    ""
                )

                request = scrapy.Request(news.link, callback=self.parse_text)
                request.meta['news'] = news
                request.meta['pageIndex'] = pageIndex
                requests.append(request)
        
        return requests

    def parse_text(self, response):
        news = response.meta['news']
        pageIndex = response.meta['pageIndex']

        if sites[pageIndex].text_paragraph_selector:
            paragraphs = response.css(sites[pageIndex].text_paragraph_selector).extract()
            cleanParagraphs = []

            for p in paragraphs:
                cleanParagraphs = ''.join([p.encode('utf-8') for text in p.css("::text").extract()])

            news.text = '\n'.join([p.encode('utf-8') for p in cleanParagraphs])
            
        if sites[pageIndex].author_selector:
            news.author = response.css(sites[pageIndex].author_selector+' ::text').extract_first()
        if sites[pageIndex].date_selector:
            news.author = response.css(sites[pageIndex].date+' ::text').extract_first()

        yield news.makeJSON()

    
# custom stuff

class Site:
    """A crawlable news site."""

    def __init__(self, 
        url, 
        feed_element_selector, 
        entry_element_selector, 
        title_element_selector, 
        summary_element_selector, 
        entry_link_selector,
        text_paragraph_selector,
        author_selector,
        date_selector):

        self.url = url
        self.feed_element_selector = feed_element_selector
        self.entry_element_selector = entry_element_selector
        self.title_element_selector = title_element_selector
        self.summary_element_selector = summary_element_selector
        self.entry_link_selector = entry_link_selector
        self.text_paragraph_selector = text_paragraph_selector
        self.author_selector = author_selector,
        self.date_selector = date_selector



class Article:
    """Defines all the things we want to store."""

    title = ""
    author = ""
    date = ""
    summary = ""
    link = ""
    text = ""
    page = ""


    def __init__(self, title, author, date, summary, link, text, page):
        self.title = title
        self.author = author
        self.date = date
        self.summary = summary
        self.link = link
        self.text = text
        self.page = page
        
        
    def makeJSON(self):
        return {
            'title': self.title,
            'author': self.author,
            'date': self.date
            'summary': self.summary, 
            'link': self.link,
            'text': self.text,
            'page': self.page
        }
        


# The sites

sites = [
    Site(
        "https://www.fifthdomain.com/dod/", 
        "div.result-listing",
        "article",
        "h4",
        "p.excerpt",
        "a",
        "#article-content p",
        "a.author-name[rel='author']",
        ""
    ),
    Site(
        "https://www.cybersecurityintelligence.com/", 
        "div.list-group",
        "div.teaser",
        "h4.list-group-item-heading a",
        "p.list-group-item-text",
        "h4.list-group-item-heading a",
        "#leftContent p",
        "",
        ""
    )]
