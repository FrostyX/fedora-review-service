import os
import json
import unittest
from fedora_messaging.api import Message


class MessageTestCase(unittest.TestCase):

    def setUp(self):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.data = os.path.join(self.here, "data")

    def get_message(self, name):
        path = os.path.join(self.data, name)
        data = json.load(open(path, "r"))
        del data["id"]
        del data["queue"]
        return Message(**data)
