import logging

class AdminFilter(logging.Filter):

    def __init__(self,foo):
        self.foo = foo

    def filter(self, record):
        return "admin" not in record.lower()

#return True or False