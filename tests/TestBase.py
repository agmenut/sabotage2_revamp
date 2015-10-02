# -*- coding: utf-8 -*-
import unittest
from haxorbb import app, db


class TestBase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfiguration')
        self.app = app.test_client()
        self.db = db
        self.db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()