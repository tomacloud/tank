#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

class Pager():

    def __init__(self, url, page_size = 10, item_count = 20, page_var = 'page'):
        self.page_var = page_var     # name of the parameter storing the current page index. default to 'page'.
        self.page_size = page_size   # number of items on each page. default to 10.
        self.item_count = item_count # total number of items.

        self._parse_url(url)

        self.page_count = (item_count + page_size - 1) / page_size
        self.offset = page_size * (self.page - 1)
        self.limit = page_size

    def _parse_url(self, url):
        m = re.search(r'[?&]%s=(\d+)' % self.page_var, url)
        if m:
            match = m.group(0)

            prefix = url[0:m.start()]
            suffix = url[m.start() + len(match):]
            if '?' not in prefix and suffix.startswith('&'):
                suffix = '?' + suffix[1:]

            self.url = '%s%s' % (prefix, suffix)
            self.page = int(m.group(1))

            if not self.page:
                self.page = 1
        else:
            self.page = 1
            self.url = url

    def build_url(self, page = 1):
        separator = '&' if '?' in self.url else '?'
        return '%s%s%s=%d' % (self.url, separator, self.page_var, page)

    def display_pages(self, display_page = 10):
        min_page = self.page - 4
        if min_page < 1:
            min_page = 1

        max_page = min_page + display_page - 1
        if max_page > self.page_count:
            max_page = self.page_count
            min_page = max_page - display_page
            if min_page < 1:
                min_page = 1

        self.display_min_page = min_page
        self.display_max_page = max_page

        if min_page > 2:
            yield 1
            yield '...'

        for i in range(min_page, max_page + 1):
            yield i

        if max_page < self.page_count - 1:
            yield '...'
            yield self.page_count

