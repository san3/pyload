#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile
from time import time

from module.Plugin import Plugin

class MegauploadCom(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self, parent)
        props = {}
        props['name'] = "MegauploadCom"
        props['type'] = "hoster"
        props['pattern'] = r"http://(?:www.)megaupload.com/"
        props['version'] = "0.1"
        props['description'] = """Megaupload.com Download Plugin"""
        props['author_name'] = ("spoob")
        props['author_mail'] = ("spoob@pyload.org")
        self.props = props
        self.parent = parent
        self.time_plus_wait = None
        self.html = [None, None]
        self.init_ocr()
        self.multi_dl = False

    def download_html(self):
        captcha_image = tempfile.NamedTemporaryFile(suffix=".gif").name
        
        for i in range(5):
            self.html[0] = self.req.load(self.parent.url, cookies=True)
            url_captcha_html = re.search('(http://www.{,3}\.megaupload\.com/gencap.php\?.*\.gif)', self.html[0]).group(1)
            self.req.download(url_captcha_html, captcha_image, cookies=True)
            captcha = self.ocr.get_captcha(captcha_image)
            os.remove(captcha_image)            
            captchacode = re.search('name="captchacode" value="(.*)"', self.html[0]).group(1)
            megavar = re.search('name="megavar" value="(.*)">', self.html[0]).group(1)
            self.html[1] = self.req.load(self.parent.url, post={"captcha": captcha, "captchacode": captchacode, "megavar": megavar}, cookies=True)
            if re.search(r"Waiting time before each download begins", self.html[1]) != None:
                break
        self.time_plus_wait = time() + 45

    def get_file_url(self):
        file_url_pattern = 'id="downloadlink"><a href="(.*)" onclick="'
        search = re.search(file_url_pattern, self.html[1])
        return search.group(1).replace(" ", "%20")

    def get_file_name(self):
        file_name_pattern = 'id="downloadlink"><a href="(.*)" onclick="'
        return re.search(file_name_pattern, self.html[1]).group(1).split("/")[-1]

    def file_exists(self):
        self.download_html()
        if re.search(r"Unfortunately, the link you have clicked is not available.", self.html[0]) != None or \
            re.search(r"Download limit exceeded", self.html[0]):
            return False
        return True
