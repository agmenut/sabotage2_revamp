# *-* coding: utf-8 *-*
import string


class Utilities(object):

    @staticmethod
    def generate_slug(title, delimiter='-'):
        exclude = string.punctuation
        result = title.lower().strip(exclude).split()
        return delimiter.join(result)
