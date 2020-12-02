import pkg_resources
import os
import shutil
from .download import download_and_unzip, find_element_in_tarball


def test_download():
    def download(filename):
        download_and_unzip(
            "http://www.idiap.ch/software/bob/databases/latest/mnist.tar.bz2", filename
        )
        uncompressed_filename = os.path.join(os.path.dirname(filename), "data")

        assert os.path.exists(filename)
        assert os.path.exists(uncompressed_filename)

        os.unlink(filename)
        shutil.rmtree(uncompressed_filename)

    # testing Untar
    filename = pkg_resources.resource_filename(__name__, "data/mnist.tar.bz2")
    download(filename)


def test_find_element_in_tarball():
    # testing Untar
    filename = pkg_resources.resource_filename(
        __name__, "data/example_csv_filelist.tar.gz"
    )
    assert (
        find_element_in_tarball(
            filename, "example_csv_filelist/protocol_dev_eval/norm/train_world.csv"
        )
        is not None
    )

    assert (
        find_element_in_tarball(
            filename, "example_csv_filelist/protocol_dev_eval/norm/"
        )
        is None
    )

    assert find_element_in_tarball(filename, "NOTHING") is None

