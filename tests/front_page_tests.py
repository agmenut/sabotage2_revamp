# -*- coding: utf-8 -*-
from TestBase import TestBase
from haxorbb import app, db
from haxorbb.models import Articles


class FrontPageTests(TestBase):
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database_connection(self):
        #tester = app.test_client(self)
        count = Articles.query.count()
        self.assertIsNotNone(count)