import re

class Change:
    def __init__(self, message):
        change_type, scope, message, mr = self.split(message)
        self.change_type = change_type
        self.scope = scope
        self.message = message
        self.mr = mr
        self.is_breaking = False

    def split(self, line):
        return re.findall(r'(\w+)(?:\(([^\)]+)\))?:\s?([^\[]+)?\s?\[!(\d+)\]', line)[0]