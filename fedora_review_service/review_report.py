import json


class ReviewReport:

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_url(cls, url):
        raise NotImplementedError

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as fp:
            data = json.load(fp)
        return cls(data)

    def flatten(self):
        result = []
        for group in self.data["results"].values():
            for checks in group.values():
                result.extend(checks)
        return result

    def count(self, status):
        return len([x for x in self.flatten() if x["result"] == status])
