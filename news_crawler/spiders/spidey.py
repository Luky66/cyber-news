# -*- coding: utf-8 -*-
import scrapy


class SpideySpider(scrapy.Spider):
    name = 'spidey'
    start_urls = []

    def start_requests(self):
        for i, site in enumerate(sites):
            self.start_urls.append( site.url )
            yield self.make_requests_from_url(site.url, {'index': i})

    def make_requests_from_url(self, url, meta):
       return scrapy.Request(url, callback=self.parse, dont_filter=True, meta=meta)


    def parse(self, response):
        i = response.meta['index']

        for feed in response.css(sites[i].feed_element_selector):
            for entry in feed.css(sites[i].entry_element_selector):
                yield {
                    'title': entry.css(sites[i].title_element_selector+' ::text').extract_first(),
                    'summary': entry.css(sites[i].summary_element_selector+' ::text').extract_first(),
                    'link': entry.css(sites[i].entry_link_selector+' ::attr(href)').extract_first()
                }


        # for next_page in response.css('div.prev-post > a'):
        #     yield response.follow(next_page, self.parse)

    
# custom stuff

class Site:
    """A crawlable news site."""

    def __init__(self, 
        url, 
        feed_element_selector, 
        entry_element_selector, 
        title_element_selector, 
        summary_element_selector, 
        entry_link_selector):

        self.url = url
        self.feed_element_selector = feed_element_selector
        self.entry_element_selector = entry_element_selector
        self.title_element_selector = title_element_selector
        self.summary_element_selector = summary_element_selector
        self.entry_link_selector = entry_link_selector

sites = [
    Site(
        "https://www.fifthdomain.com/dod/", 
        "div.result-listing",
        "article",
        "h4",
        "p.excerpt",
        "a"
    )]