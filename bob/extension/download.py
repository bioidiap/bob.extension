#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bz2
import glob
import hashlib
import io
import logging
import os
import tarfile
import zipfile

from pathlib import Path
from shutil import copyfileobj
from urllib.request import urlopen

from . import rc

logger = logging.getLogger(__name__)


def _bob_data_folder():
    return rc.get(
        "bob_data_folder", os.path.join(os.path.expanduser("~"), "bob_data")
    )


def _unzip(zip_file, directory):

    with zipfile.ZipFile(zip_file) as myzip:
        myzip.extractall(directory)


def _untar(tar_file, directory, ext):

    if ext in [".bz2" or ".tbz2"]:
        mode = "r:bz2"
    elif ext in [".gz" or ".tgz"]:
        mode = "r:gz"
    else:
        mode = "r"

    with tarfile.open(name=tar_file, mode=mode) as t:
        t.extractall(directory)


def _unbz2(bz2_file):

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
            logger.warning(
                "Could not download from the %s url", url, exc_info=True
            )
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
    file_hash = str(file_hash)
    if (algorithm == "md5") or (algorithm == "auto" and len(file_hash) == 32):
        hasher = "md5"
    else:
        hasher = "sha256"

    if _hash_file(fpath, hasher, chunk_size).startswith(file_hash):
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

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        hasher = hashlib.md5()

    with open(fpath, "rb") as fpath_file:
        for chunk in iter(lambda: fpath_file.read(chunk_size), b""):
            hasher.update(chunk)

    return str(hasher.hexdigest())


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

        if file_hash is not None and not validate_file(
            final_filename, file_hash, algorithm=hash_algorithm
        ):
            found_hash = _hash_file(final_filename, algorithm=hash_algorithm)
            raise ValueError(
                f"The downloaded file: {final_filename} has the hash of {found_hash}, but we expected {file_hash}. Please re-do the procedure."
            )

    # Finally extract if wanted. This will always extract over what would already exist
    # so that if a new version of the archive is downloaded, the extracted folder is
    # updated.
    if extract:
        extract_compressed_file(final_filename)

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


def find_element_in_tarball(filename, target_path, open_as_stream=False):
    """
    Search an element in a tarball.

    Parameters
    ----------
    filename : str
       Tarball file name

    target_path : str
       Target path to be searched inside of the tarball

    open_as_stream: bool
       If `True`, will load the element from the tarball as a byte_stream.
       If `False`, will load as text


    Returns
    -------
    object
        It returns an opened file
    """

    f = tarfile.open(filename)
    # iterate over the members of the tarball
    while True:
        member = f.next()
        if member is None:
            return None

        if not member.isfile():
            continue

        if not member.name.endswith(target_path):
            continue

        if open_as_stream:
            return io.BufferedReader(f.extractfile(member)).read()
        else:
            return io.TextIOWrapper(f.extractfile(member), encoding="utf-8")


def search_file(base_path, options):
    """
    Search for files either in a file structure, or in a tarball.

    Parameters
    ----------

    base_path: str
        Base folder to start the search, or the tarball to be searched

    options: list
        Files to be searched. This function will return the first occurrence.
        The option can be an incomplete relative path. For example, if you have
        a file called ``"/a/b/c/d.txt"``, and base_path is ``"/a/b"``, then
        options can be ``["d.txt"]``.

    Returns
    -------
    object
        It returns an opened file
    """

    if not isinstance(options, list):
        options = [options]

    # If the input is a directory
    if os.path.isdir(base_path):
        for o in options:
            # we append './' to o because o might start with /
            pattern = os.path.join(base_path, "**", f"./{o}")
            for path in glob.iglob(pattern, recursive=True):
                if not os.path.isfile(path):
                    continue
                return open(path)
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


def list_dir(base_path, inner_folder="", folders=True, files=True):
    """Lists the files and folders inside a folder or a tarball.
    To list an inner level folder (useful when base_path is a tarball),
    provide the inner_folder argument.

    Parameters
    ----------
    base_path : str
        Path to a folder or a tarball
    inner_folder : str
        Path to an inner folder inside base_path. If given, the folders inside
        this folder are listed.
    folders : bool
        If False, will exclude folders from the results.
    files : bool
        If False, will exclude files from the results.

    Returns
    -------
    list
        Sorted list of file and directory names

    Raises
    ------
    ValueError
        If base_path is not a folder or a tarball
    """
    # If the input is a directory
    path = Path(base_path)
    results = []
    if path.is_dir():
        path = path / inner_folder
        for x in path.iterdir():
            if x.is_dir() and folders:
                results.append(x.name)
            if x.is_file() and files:
                results.append(x.name)

    # If it's not a directory, is it a tarball?
    elif tarfile.is_tarfile(base_path):
        with tarfile.open(base_path, mode="r") as t:
            tar_infos = t.getmembers()
            commonpath = os.path.commonpath([info.name for info in tar_infos])
            commonpath = Path(commonpath) / inner_folder
            for info in tar_infos:
                if info.name == ".":
                    continue
                path = Path(info.name)
                if path.parent != commonpath:
                    continue
                if info.isdir() and folders:
                    results.append(path.name)
                if info.isfile() and files:
                    results.append(path.name)
    else:
        raise ValueError(
            f"The provided path: `{base_path}` should be a directory or a tarball."
        )

    return sorted(results)
