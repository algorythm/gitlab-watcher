import re

class Change:
    def __init__(self, message):
        change_type, scope, breaking, message, mr = self.split(message)
        self.change_type = change_type
        self.scope = scope
        self.message = message
        self.mr = mr
        self.is_breaking = breaking == '!'

    def split(self, line):
        return re.findall(r'(\w+)(?:\(([^\)]+)\))?(!?):\s?([^\[]+)?\s?\[!(\d+)\]', line)[0]

if __name__ == '__main__':
    changes = [
        'feat(hello): this is not breaking [!123]',
        'fix(asd): i did it all [!321]',
        'refactor(hello)!: breaking all the things! [!111]'
    ]

    for change in changes:
        c = Change(change)
        print(f'{c.change_type} - {c.scope}: Breaking: {c.is_breaking}, !{c.mr}, {c.message}')
