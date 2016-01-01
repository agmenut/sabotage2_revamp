# *-* coding: utf-8 *-*
import string
import os
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


def exif_orientation_transform(source, orientation):
    angle_values = {2: Image.FLIP_LEFT_RIGHT,
                    3: 180,
                    4: Image.FLIP_TOP_BOTTOM,
                    5: 'transpose_1',
                    6: 270,
                    7: 'transpose_2',
                    8: 90}
    if orientation == 1:
        return source
    elif orientation == 3 or orientation == 6 or orientation == 8:
        return source.rotate(angle_values[orientation])
    elif orientation == 2 or orientation == 4:
        return source.transpose(angle_values[orientation])
    else:
        return source


def generate_thumbnail(source, dest_path, source_path=None, height=None, width=None, prefix='tn_', preserve_exif=False):
    if height is None and width is None:
        raise ValueError('Either height or width value required')
    if height and width:
        warn("Both height and width are set, defaulting to width", UserWarning)
    path, img = os.path.split(source)
    if source_path:
        path = source_path
    im = Image.open(os.path.join(path, source))
    ratio = float(im.width) / float(im.height)

    exif_data = {TAGS[k]: v for k, v in im._getexif().items() if k in TAGS}

    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    if width:
        height = int(width / ratio)
    elif width is None and height:
        width = int(height / ratio)
    resized = im.resize((width, height), Image.ANTIALIAS)
    orientation = exif_data['Orientation']

    if orientation:
        resized = exif_orientation_transform(resized, orientation)

    target_file = os.path.join(dest_path, "{}{}".format(prefix, img))
    resized.save(target_file, im.format)
