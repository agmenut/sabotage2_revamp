# *-* coding: utf-8 *-*
import string
import os
from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from warnings import warn


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


def generate_thumbnail(source, dest_path, source_path=None, height=None, width=None, prefix='tn_', preserve_exif=False):
    if height is None and width is None:
        raise ValueError('Either height or width value required')
    if height and width:
        warn("Both height and width are set, defaulting to width", UserWarning)
    path, img = os.path.split(source)
    if source_path:
        path = source_path
    image_buffer = BytesIO()
    im = Image.open(os.path.join(path, source))
    ratio = float(im.size[0]) / float(im.size[1])
    if width:
        height = int(width / ratio)
    elif width is None and height:
        width = int(height / ratio)
    resized = im.resize((width, height), Image.ANTIALIAS)
    image_buffer.seek(0)
    target_file = os.path.join(dest_path, "{}{}".format(prefix, img))
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
    resized.save(target_file, im.format)
