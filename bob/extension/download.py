#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import os
import logging
logger = logging.getLogger(__name__)


def _unzip(zip_file, directory):
    import zipfile

    with zipfile.ZipFile(zip_file) as myzip:
        myzip.extractall(directory)


def _untar(tar_file, directory, ext):

    if ext in [".bz2" or ".tbz2"]:
        mode = "r:bz2"
    elif ext in [".gz" or ".tgz"]:
        mode = "r:gz"
    else:
        mode = "r"

    import tarfile
    with tarfile.open(name=tar_file, mode=mode) as t:
        t.extractall(directory)


def _unbz2(bz2_file):
    import bz2
    with bz2.BZ2File(bz2_file) as t:
        open(os.path.splitext(bz2_file)[0], 'wb').write(t.read())


def download_file(url, out_file):
  """Downloads a file from a given url

  Parameters
  ----------
  url : str
      The url to download form.
      
  out_file : str
      Where to save the file.
  """
  import sys
  if sys.version_info[0] < 3:
    # python2 technique for downloading a file
    from urllib2 import urlopen
    with open(out_file, 'wb') as f:
      response = urlopen(url)
      f.write(response.read())

  else:
    # python3 technique for downloading a file
    from urllib.request import urlopen
    from shutil import copyfileobj
    with urlopen(url) as response:
      with open(out_file, 'wb') as f:
        copyfileobj(response, f)


def download_and_unzip(urls, filename):
    """
    Download a file from a given URL list, save it somewhere and unzip/untar if necessary
    
    Example:
       download_and_unzip(["https://mytesturl.co/my_file_example.tag.bz2"], filename="~/my_file_example.tag.bz2")

   
    Parameters
    ----------
    
      urls: list
        List containing the all the URLs.
        The function will try to download them in order
        
      filename: str
        File name (full path) where the downloaded file will be written and uncompressed

    """

    # Just testing if string and wrap it in a list if it's the case
    if isinstance(urls, str):
        urls = [urls]

    for url in urls:
        try:
            logger.info(
                "Downloading from "
                "{} ...".format(url))
            download_file(url, filename)

            break
        except Exception:
            logger.warning(
                "Could not download from the %s url", url, exc_info=True)
    else:  # else is for the for loop
        if not os.path.isfile(filename):
            raise RuntimeError("Could not download the file.")

    # Uncompressing if it is the case
    ext = os.path.splitext(filename)[-1].lower()
    header = os.path.splitext(filename)[0].lower()
    if ext == ".zip":
        logger.info("Unziping in {0}".format(filename))
        _unzip(filename, os.path.dirname(filename))
 
    elif header[-4:] == ".tar" or ext in [".tgz", ".tbz2"]:
        logger.info("Untar/gzip in {0}".format(filename))
        _untar(filename, os.path.dirname(filename), ext)

    elif ext == ".bz2":
        logger.info("Unbz2 in {0}".format(filename))
        _unbz2(filename)

