#!/usr/bin/env python3

from xml import sax
import re

class IpaParser(sax.handler.ContentHandler):

    special_chars = '"&<>'
    region_regex = r"{{a\|(?P<regions>.*?)}}"

    def __init__(self, *args, **kwargs):
        super(sax.handler.ContentHandler, self).__init__(*args, **kwargs)
        self.depth = 0
        self.reading_page = False
        self.reading_ns = False
        self.reading_title = False
        self.reading_text = False
        self.reading_phonetics = False
        self.reading_entry = False
        self.title = None
        self.entry = None
        self.lines = 0

    def emit_entry(self):
        print(self.entry)
        region = re.search(self.region_regex, self.entry)
        if region:
            print("region={0}".format(region.group(1)))

    def startElement(self, name, attrs):
        if name == "page":
            self.reading_page = True
        if self.reading_page and name == "title":
            self.reading_title = True
        if self.reading_page and name == "ns":
            self.reading_ns = True
        if self.reading_page and name == "text":
            self.reading_text = True
        #print("{0}start {1}".format("|  " * self.depth, name))
        self.depth += 1

    def characters(self, content):
        if self.reading_ns and content != "0":
            self.reading_page = False
        if self.reading_title:
            self.title = content
        if self.reading_text:
            if self.lines == 0 :
                print(">>>", self.title)
            if content == "===Pronunciation===":
                self.reading_phonetics = True
            elif content.startswith("==="):
                self.reading_phonetics = False
            self.lines += 1
        if self.reading_phonetics:
            if content.startswith("*"):
                if self.entry:
                    self.emit_entry()
                self.entry = content
            elif self.entry and content[0] in self.special_chars:
                self.entry += content
            elif self.entry and self.entry[-1] in self.special_chars:
                self.entry += content
            elif not content.strip():
                if self.entry:
                    self.emit_entry()
                self.reading_entry = False

    def endElement(self, name):
        self.depth -= 1
        if name == "page":
            self.reading_page = False
            self.title = None
        if name == "ns":
            self.reading_ns = False
        if name == "title":
            self.reading_title = False
        if name == "text":
            self.reading_text = False
            self.reading_phonetics = False
            self.lines = 0

        #print("{0}end {1}".format("|  " * self.depth, name))


parser = sax.make_parser()
parser.setContentHandler(IpaParser())
parser.parse(open("enwik.xml"))
