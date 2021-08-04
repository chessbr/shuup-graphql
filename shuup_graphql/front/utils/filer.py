import os
from PIL import Image
from six import BytesIO
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from shuup.utils.filer import filer_image_from_data


def filer_image_from_file_path(image_file_path, path):
    _, full_file_name = os.path.split(image_file_path)
    file_name, _ = os.path.splitext(full_file_name)
    image = Image.open(image_file_path)
    sio = BytesIO()
    image.save(sio, format="JPEG")

    return filer_image_from_data(
        request=None, path=path, file_name="{}.jpeg".format(file_name), file_data=sio.getvalue(), sha1=True
    )


def filer_image_from_url(image_url, path):
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()
    image_file_path = img_temp.name
    return filer_image_from_file_path(image_file_path, path)
