
from zipfile import ZipFile
import io
import sys
import base64
import uuid
import re
import urllib
import os
import tkinter
from PIL import Image

if sys.platform == 'darwin':
    sys.path.append('utils')
    from fileDetail import EXTERNAL_DEPENDENCIES
else:
    from utils.fileDetail import EXTERNAL_DEPENDENCIES


def write_page(page):
    """Writes the specified page/module
    To take advantage of this function, a multipage app should be structured into sub-files with a `def write()` function
    Arguments:
            page {module} -- A module with a "def write():" function
    """

    page.write()




def image_to_buffer(input_image):
    '''
    This function will return the buffer for the input image.
    '''

    try:
        input_image = Image.open(input_image)
    except:
        print('file cant open by PIL')

    buffered = io.BytesIO()
    input_image.save(buffered, format='PNG')
    return buffered





def download_file(file):
    # Don't download the file twice. (If possible, verify the download using the file length.)
    if os.path.exists(EXTERNAL_DEPENDENCIES[file]["path"]+file):
        if os.path.getsize(EXTERNAL_DEPENDENCIES[file]["path"]+file)+1000 > EXTERNAL_DEPENDENCIES[file]["size"]:
            return

    # These are handles to two visual elements to animate.
    weights_warning, progress_bar = None, None
    try:
        weights_warning = st.warning("Downloading %s..." % file)
        progress_bar = st.progress(0)
        with open(EXTERNAL_DEPENDENCIES[file]["path"]+file, "wb") as output_file:
            with urllib.request.urlopen(EXTERNAL_DEPENDENCIES[file]["url"]) as response:
                length = int(response.info()["Content-Length"])
                counter = 0.0
                MEGABYTES = 2.0 ** 20.0
                while True:
                    data = response.read(8192)
                    if not data:
                        break
                    counter += len(data)
                    output_file.write(data)

                    # We perform animation by overwriting the elements.
                    weights_warning.warning("Downloading %s... (%6.2f/%6.2f MB)" %
                                            (file, counter / MEGABYTES, length / MEGABYTES))
                    progress_bar.progress(min(counter / length, 1.0))

    # Finally, we remove these visual elements by calling .empty().
    finally:
        if weights_warning is not None:
            weights_warning.empty()
        if progress_bar is not None:
            progress_bar.empty()
