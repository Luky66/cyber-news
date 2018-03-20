# -*- coding: utf-8 -*-
import scrapy


class SpideySpider(scrapy.Spider):
    name = 'spidey'
    start_urls = []

    def start_requests(self):
        for page_index, site in enumerate(sites):
            self.start_urls.append( site.url )
            yield self.make_requests_from_url(site.url, {'page_index': page_index, 'page_name': site.page_name, 'page_domain': site.page_domain})

    def make_requests_from_url(self, url, meta):
       return scrapy.Request(url, callback=self.parse_feed, dont_filter=True, meta=meta)


    def parse_feed(self, response):
        page_index = response.meta['page_index']
        requests = []

        for feed in response.css(sites[page_index].feed_element_selector):
            for entry in feed.css(sites[page_index].entry_element_selector):

                # Construct news element and pass it along

                news = Article(
                    entry.css(sites[page_index].title_element_selector+' ::text').extract_first(),
                    "", #author
                    "", #date
                    entry.css(sites[page_index].summary_element_selector+' ::text').extract_first(),
                    response.urljoin(entry.css(sites[page_index].entry_link_selector+' ::attr(href)').extract_first()),
                    "", #text
                    response.meta['page_name'],
                    response.meta['page_domain']
                )

                request = scrapy.Request(news.link, callback=self.parse_text)
                request.meta['news'] = news
                request.meta['page_index'] = page_index
                requests.append(request)
        
        return requests

    def parse_text(self, response):
        news = response.meta['news']
        page_index = response.meta['page_index']

        if sites[page_index].text_paragraph_selector:
            paragraphs = response.css(sites[page_index].text_paragraph_selector)
            cleanParagraphs = []

            for p in paragraphs:
                cleanParagraphs.append(''.join([text for text in p.css("::text").extract()]))

            news.text = '\n'.join([p.encode('utf-8') for p in cleanParagraphs])

        if sites[page_index].author_selector:
            news.author = response.css(sites[page_index].author_selector+' ::text').extract_first()
        if sites[page_index].date_selector:
            news.date = response.css(sites[page_index].date_selector+' ::text').extract_first()

        yield news.makeJSON()

    
# custom stuff

class Site:
    """A crawlable news site."""

    def __init__(self, 
        page_name,
        page_domain,
        url, 
        feed_element_selector, 
        entry_element_selector, 
        title_element_selector, 
        summary_element_selector, 
        entry_link_selector,
        text_paragraph_selector,
        author_selector,
        date_selector):

        self.page_name = page_name
        self.page_domain = page_domain
        self.url = url
        self.feed_element_selector = feed_element_selector
        self.entry_element_selector = entry_element_selector
        self.title_element_selector = title_element_selector
        self.summary_element_selector = summary_element_selector
        self.entry_link_selector = entry_link_selector
        self.text_paragraph_selector = text_paragraph_selector
        self.author_selector = author_selector
        self.date_selector = date_selector



class Article:
    """Defines all the things we want to store."""

    title = ""
    author = ""
    date = ""
    summary = ""
    link = ""
    text = ""
    page_name = ""
    page_domain = ""


    def __init__(self, title, author, date, summary, link, text, page_name, page_domain):
        self.title = title
        self.author = author
        self.date = date
        self.summary = summary
        self.link = link
        self.text = text
        self.page_name = page_name
        self.page_domain = page_domain
        
        
    def makeJSON(self):
        return {
            'title': self.title,
            'author': self.author,
            'date': self.date,
            'summary': self.summary, 
            'link': self.link,
            'text': self.text,
            'page_name': self.page_name,
            'page_domain': self.page_domain
        }
        


# The sites

sites = [
    Site(
        "Fifthdomain",
        "fifthdomain.com",
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
        "Cybersecurity Intelligence",
        "cybersecurityintelligence.com",
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
