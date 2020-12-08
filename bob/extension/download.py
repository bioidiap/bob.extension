#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import os
import logging
import hashlib
from . import rc
import os

logger = logging.getLogger(__name__)


def _bob_data_folder():
    return rc.get("bob_data_folder", os.path.join(os.path.expanduser("~"), "bob_data"))


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


def extract_compressed_file(filename):
    """Extracts a compressed file.

    Parameters
    ----------
    filename : str
        Path to the .zip, .tar, .tar.*, .tgz, .tbz2, and .bz2 file

    Raises
    ------
    ValueError
        If the extension of the file is not recognized.
    """
    # Uncompressing if it is the case
    header, ext = os.path.splitext(filename)
    header, ext = header.lower(), ext.lower()

    if ext == ".zip":
        logger.info("Unziping in {0}".format(filename))
        _unzip(filename, os.path.dirname(filename))

    elif header[-4:] == ".tar" or ext in [".tar", ".tgz", ".tbz2"]:
        logger.info("Untar/gzip in {0}".format(filename))
        _untar(filename, os.path.dirname(filename), ext)

    elif ext == ".bz2":
        logger.info("Unbz2 in {0}".format(filename))
        _unbz2(filename)

    else:
        raise ValueError(f"Unknown compressed file: {filename}")


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


def download_file_from_possible_urls(urls, out_file):
    """Tries to download a file from a list of possible urls.
    The function stops as soon as one url works and raises an error when all urls fail.

    Parameters
    ----------
    urls : list
        List of urls
    out_file : str
        Path to save the file

    Raises
    ------
    RuntimeError
        If downloading from all urls fails.
    """
    for url in urls:
        try:
            download_file(url, out_file)
            break
        except Exception:
            logger.warning("Could not download from the %s url", url, exc_info=True)
    else:  # else is for the for loop
        raise RuntimeError(
            f"Could not download the requested file from the following urls: {urls}"
        )


def validate_file(fpath, file_hash, algorithm="auto", chunk_size=65535):
    """Validates a file against a sha256 or md5 hash.

    Parameters
    ----------
    fpath : str
        path to the file being validated

    file_hash : str
        The expected hash string of the file.
        The sha256 and md5 hash algorithms are both supported.

    algorithm : str
        Hash algorithm, one of 'auto', 'sha256', or 'md5'.
        The default 'auto' detects the hash algorithm in use.

    chunk_size : int
        Bytes to read at a time, important for large files.

    Returns
    -------
    bool
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
    fpath : str
        Path to the file being validated

    algorithm : str
        Hash algorithm, one of `'auto'`, `'sha256'`, or `'md5'`.
        The default `'auto'` detects the hash algorithm in use.

    chunk_size : str
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


def get_file(
    filename,
    urls,
    cache_subdir="datasets",
    file_hash=None,
    hash_algorithm="auto",
    extract=False,
    force=False,
):
    """Downloads a file from a given a list of URLS.
    In case the first link fails, the following ones will be tried.
    The downloaded files will be saved in ``~/bob_data`` by default. You may change the
    location of this folder using::

        $ bob config set bob_data_folder /another/location/

    Parameters
    ----------
    filename : str
        Name of the file
    urls : list
        List containing the all the URLs.
        The function will try to download them in order and stops if it succeeds.
    cache_subdir : str
        Subdirectory where the file is saved.
    file_hash : str
        The expected hash string of the file after download.
        The sha256 and md5 hash algorithms are both supported.
    hash_algorithm : str
        Select the hash algorithm to verify the file.
        options are `'md5'`, `'sha256'`, and `'auto'`.
        The default 'auto' detects the hash algorithm in use.
    extract : bool
        If True, will extract the downloaded file.
    force : bool
        If True, will download the file anyway if it already exists.

    Returns
    -------
    str
        The path to the downloaded file.

    Raises
    ------
    ValueError
        If the file_hash does not match the downloaded file
    """
    cache_dir = _bob_data_folder()

    cache_dir = os.path.join(cache_dir, cache_subdir)
    os.makedirs(cache_dir, exist_ok=True)

    final_filename = os.path.join(cache_dir, filename)

    download = True
    if os.path.exists(final_filename):
        if file_hash is None or validate_file(
            final_filename, file_hash, algorithm=hash_algorithm
        ):
            download = False
        else:
            logger.warning(
                f"A file was found, but it seems to be "
                f"corrupted or outdated because its "
                f" hash does not match the original value of {file_hash}"
                f" so, will be re-download."
            )

    if download or force:
        logger.info("Downloading %s", final_filename)
        download_file_from_possible_urls(urls, final_filename)
        if extract:
            extract_compressed_file(final_filename)

        if file_hash is not None and not validate_file(
            final_filename, file_hash, algorithm=hash_algorithm
        ):
            raise ValueError(
                "File was downloaded, but it is corrupted. Please re-do the procedure."
            )

    return final_filename


def download_and_unzip(urls, filename):
    """
    Download a file from a given URL list, save it somewhere and unzip/untar if necessary

    Example::

        download_and_unzip(
            ["https://mytesturl.co/my_file_example.tag.bz2"],
            filename="~/my_file_example.tag.bz2"
        )


    Parameters
    ----------
    urls : list
      List containing the all the URLs.
      The function will try to download them in order

    filename : str
      File name (full path) where the downloaded file will be written and uncompressed

    """

    # Just testing if string and wrap it in a list if it's the case
    if isinstance(urls, str):
        urls = [urls]

    download_file_from_possible_urls(urls, filename)
    extract_compressed_file(filename)


def find_element_in_tarball(filename, target_path):
    """
    Search an element in a tarball.

    Parameters
    ----------
    filename : str
       Tarball file name

    target_path : str
       Target path to be searched inside of the tarball


    Returns
    -------
    object
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


def search_file(base_path, options):
    """
    Search for files either in a file structure, or in a tarball.

    Parameters
    ----------

    base_path: str
       Base path to start the search, or the tarball to be searched

    options: list
       Files to be searched. This function will return the first occurency

    Returns
    -------
    object
        It returns an opened file

    """

    if not isinstance(options, list):
        options = [options]

    # If the input is a directory
    if os.path.isdir(base_path):

        def get_fs():
            fs = []
            for root, _, files in os.walk(base_path, topdown=False):
                for name in files:
                    fs.append(os.path.join(root, name))
            return fs

        def search_in_list(o, lst):
            for i, l in enumerate(lst):
                if o in l:
                    return i
            else:
                return -1

        fs = get_fs()
        for o in options:
            index = search_in_list(o, fs)
            if index >= 0:
                return open(fs[index])
        else:
            return None
    else:
        # If it's not a directory is a tarball

        for o in options:
            f = find_element_in_tarball(base_path, o)
            if f is not None:
                return f

        else:
            return None
