#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-06-06 12:59:02
# rate 0.001
# burst 10
# Project: willhaben_hauser_kaufen_ooe_uu
# crawls search result page of willhaben and extracts information from list-view

from pyspider.libs.base_handler import *
import re


class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v01'
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.willhaben.at/iad/immobilien/haus-kaufen/oberoesterreich/urfahr-umgebung/?rows=300', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for i, article in enumerate(response.doc('div#resultlist>.search-result-entry').items()):
            if article.attr.id is None:
                title=article.find("div.header a").text()
                description=article.find("div.description").text()
                info_left=article.find("div.info .desc-left").text()
                info_regex = re.match( u'([0-9]+) m².*', info_left, re.M|re.I)
                if info_regex:
                    sm_str=info_regex.group(1).replace(',','.')
                    sm=float(sm_str)
                else:
                    sm=None
                price_str=article.find("div.info .pull-right").text().replace('.','').replace(',-','').replace(',','.')
                try:
                    price=float(price_str)
                except:
                    price=0.0

                address=article.find("div.bottom .address-lg")
                address_str=re.sub(r'[\r\n ]+', " ", address.text())
                address_regex = re.match( ur'(([\w]+[ 0-9]*)?, )?([0-9]+)?[ ]*([\w\- ]+)', address_str, re.M|re.I|re.UNICODE)
                if address_regex:
                    street=address_regex.group(2)
                    plz=address_regex.group(3)
                    city=address_regex.group(4)
                else:
                    street='xxx'
                    plz='xxx'
                    city='xxx'


                url=article.find("section.image-section a").attr.href
                img=article.find("section.image-section img").attr.src

                msg = {
                    "url": url,
                    "img": img,
                    "title": title,
                    "description": description,
                    "sm": sm,
                    "info":info_left,
                    "price": price,
                    "price_str": price_str,
                    "address_full": address_str,
                    "street":street,
                    "plz":plz,
                    "city":city,
                }
                self.send_message(self.project_name,msg, url=url)

    def on_message(self, project, msg):
        return msg
