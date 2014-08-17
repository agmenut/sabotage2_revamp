# -*- coding: utf-8 -*-
from TestBase import TestBase
from haxorbb import app


class FrontPageTests(TestBase):
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)