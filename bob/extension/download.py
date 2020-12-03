#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import os
import logging
import hashlib

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
        open(os.path.splitext(bz2_file)[0], "wb").write(t.read())


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

        with open(out_file, "wb") as f:
            response = urlopen(url)
            f.write(response.read())

    else:
        # python3 technique for downloading a file
        from urllib.request import urlopen
        from shutil import copyfileobj

        with urlopen(url) as response:
            with open(out_file, "wb") as f:
                copyfileobj(response, f)


def validate_file(fpath, file_hash, algorithm="auto", chunk_size=65535):
    """Validates a file against a sha256 or md5 hash.
  
  Parameters
  ----------
      fpath: str
          path to the file being validated
      
      file_hash: str
          The expected hash string of the file.
          The sha256 and md5 hash algorithms are both supported.
      
      algorithm: str
          Hash algorithm, one of 'auto', 'sha256', or 'md5'.
          The default 'auto' detects the hash algorithm in use.
      
      chunk_size: int
          Bytes to read at a time, important for large files.
  Returns
  -------
      Whether the file is valid
  """
    # Code from https://github.com/tensorflow/tensorflow/blob/v2.3.1/tensorflow/python/keras/utils/data_utils.py#L312
    # Very useful

    if (algorithm == "sha256") or (algorithm == "auto" and len(file_hash) == 64):
        hasher = "sha256"
    else:
        hasher = "md5"

    if str(_hash_file(fpath, hasher, chunk_size)) == str(file_hash):
        return True
    else:
        return False


def _hash_file(fpath, algorithm="sha256", chunk_size=65535):
    """Calculates a file sha256 or md5 hash.
  
  Example
  -------
  ```python
  _hash_file('/path/to/file.zip')
  'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
  ```
  
  Parameters
  ----------
      fpath: str
          Path to the file being validated
      
      algorithm: str
          Hash algorithm, one of `'auto'`, `'sha256'`, or `'md5'`.
          The default `'auto'` detects the hash algorithm in use.

      chunk_size: str
          Bytes to read at a time, important for large files.

  Returns
  -------
      The file hash
  """
    # Code from https://github.com/tensorflow/tensorflow/blob/v2.3.1/tensorflow/python/keras/utils/data_utils.py#L312
    # Very useful

    if (algorithm == "sha256") or (algorithm == "auto" and len(hash) == 64):
        hasher = hashlib.sha256()
    else:
        hasher = hashlib.md5()

    with open(fpath, "rb") as fpath_file:
        for chunk in iter(lambda: fpath_file.read(chunk_size), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def download_files(
    urls,
    filename,
    cache_dir=os.path.join(os.path.expanduser("~"), ".bob"),
    cache_subdir="",
    file_hash=None,
    hash_algorithm="auto",
):
    """Downloads a file from a given a list of URLS.
    In case the first link fails, the following ones will be tried.

    Parameters
    ----------
    urls : list
        List containing the all the URLs.
        The function will try to download them in order
        
    filename: str
        Name of the file

    cache_dir: str
          Location to store cached files, default to `~/.bob/`.

    cache_subdir: str
        Subdirectory where the file is saved.

    file_hash: The expected hash string of the file after download.
               The sha256 and md5 hash algorithms are both supported.          
    
    hash_algorithm: str
         Select the hash algorithm to verify the file.
          options are `'md5'`, `'sha256'`, and `'auto'`.
          The default 'auto' detects the hash algorithm in use.
    """
    # Inspired in https://github.com/tensorflow/tensorflow/blob/v2.3.1/tensorflow/python/keras/utils/data_utils.py#L312
    if cache_dir is None:
        cache_dir = os.path.join(os.path.expanduser("~"), ".bob")

    cache_dir = os.path.join(cache_dir, cache_subdir)
    os.makedirs(cache_dir, exist_ok=True)

    final_filename = os.path.join(cache_dir, filename)

    download = True
    if os.path.exists(final_filename):
        if file_hash is not None:
            if not validate_file(final_filename, file_hash, algorithm=hash_algorithm):
                logger.warning(
                    f"A file was found, but it seems to be "
                    "corrupted or outdated because its "
                    " hash does not match the original value of {file_hash}"
                    " so, will be re-download."
                )
            else:
                download = False

    if download:
        for url in urls:
            try:
                logger.info("Downloading from " "{} ...".format(url))
                download_file(url, final_filename)

                if file_hash is not None:
                    if not validate_file(
                        final_filename, file_hash, algorithm=hash_algorithm
                    ):
                        raise ValueError(
                            "File was downloaded, but it is corrupted. Please re-do the procedure."
                        )
                break
            except Exception:
                logger.warning("Could not download from the %s url", url, exc_info=True)
        else:  # else is for the for loop
            if not os.path.isfile(final_filename):
                raise RuntimeError("Could not download the file.")


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

    download_files(urls, filename)

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


def find_element_in_tarball(filename, target_path):
    """
    Search an element in a tarball.
    
    Parameters
    ----------
    
    filename: str
       Tarball file name
       
    target_path: str
       Target path to be searched inside of the tarball
    
    
    Returns
    -------
       It returns an opened file
    
    """
    import tarfile
    import io

    f = tarfile.open(filename)
    for member in f.getmembers():
        if member.isdir():
            continue

        if (
            member.isfile()
            and target_path in member.name
            and os.path.split(target_path)[-1] == os.path.split(member.name)[-1]
        ):

            return io.TextIOWrapper(f.extractfile(member), encoding="utf-8")
    else:
        return None
