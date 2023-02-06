
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





