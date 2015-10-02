# *-* coding: utf-8 *-*
import string


class Utilities(object):

    @staticmethod
    def generate_slug(title, delimiter='-'):
        slug = []
        symbol_map = dict((ord(char), None) for char in string.punctuation)
        result = title.lower().split()
        for word in result:
            word = word.translate(symbol_map)
            slug.append(word)
        return delimiter.join(slug)[:30]
