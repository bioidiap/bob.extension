import os
import shutil
import tempfile

import pkg_resources

from bob.extension import rc_context
from bob.extension.download import (
    _untar,
    download_and_unzip,
    find_element_in_tarball,
    get_file,
    list_dir,
    search_file,
)


def test_download_unzip():
    def download(filename):
        download_and_unzip(
            "http://www.idiap.ch/software/bob/databases/latest/mnist.tar.bz2",
            filename,
        )
        uncompressed_filename = os.path.join(os.path.dirname(filename), "data")

        assert os.path.exists(filename)
        assert os.path.exists(uncompressed_filename)

        os.unlink(filename)
        shutil.rmtree(uncompressed_filename)

    # testing Untar
    filename = pkg_resources.resource_filename(__name__, "data/mnist.tar.bz2")
    download(filename)


def test_get_file():

    filename = "mnist.tar.bz2"
    urls = ["http://www.idiap.ch/software/bob/databases/latest/mnist.tar.bz2"]
    file_hash = "d72c7e80534d980d1df23f78242c595a"

    with tempfile.TemporaryDirectory() as temp_dir, rc_context(
        {"bob_data_folder": temp_dir}
    ):

        final_filename = get_file(
            filename,
            urls,
            cache_subdir="databases",
            file_hash=file_hash,
        )
        assert os.path.exists(final_filename)

        # Download again. to check the cache
        final_filename = get_file(
            filename,
            urls,
            cache_subdir="databases",
            file_hash=file_hash,
        )
        assert os.path.exists(final_filename)

        # Download again, no hash. to check the cache
        final_filename = get_file(
            filename,
            urls,
            cache_subdir="databases",
        )
        assert os.path.exists(final_filename)


def test_find_element_in_tarball():
    # testing Untar
    filename = pkg_resources.resource_filename(
        __name__, "data/example_csv_filelist.tar.gz"
    )
    assert (
        find_element_in_tarball(
            filename,
            "example_csv_filelist/protocol_dev_eval/norm/train_world.csv",
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


def test_search_file():
    filename = pkg_resources.resource_filename(
        __name__, "data/example_csv_filelist.tar.gz"
    )

    with tempfile.TemporaryDirectory(suffix="_extracted") as tmpdir:

        _untar(filename, tmpdir, ".gz")

        # Search in the tarball and in its extracted folder
        for final_path in (filename, tmpdir):
            in_extracted_folder = final_path.endswith("_extracted")
            all_files = list_dir(final_path)

            output_file = search_file(
                final_path, "protocol_dev_eval/norm/train_world.csv"
            )
            assert output_file is not None, all_files

            # test to see if using / we can force an exact match
            output_file = search_file(
                final_path, "/protocol_dev_eval/norm/train_world.csv"
            )
            assert output_file is not None, all_files
            assert "my_data" not in output_file.read()
            if in_extracted_folder:
                assert "my_protocol" not in output_file.name

            assert (
                search_file(final_path, "norm/train_world.csv") is not None
            ), all_files
            assert (
                search_file(final_path, "protocol_dev_eval/norm/xuxa.csv")
                is None
            ), all_files


def test_list_dir():
    data_folder = pkg_resources.resource_filename(__name__, "data")

    folder = os.path.join(data_folder, "test_list_folders")
    tar1 = os.path.join(data_folder, "test_list_folders1.tar.gz")
    tar2 = os.path.join(data_folder, "test_list_folders2.tar.gz")

    for root_folder in (folder, tar1, tar2):
        fldrs = list_dir(root_folder)
        assert fldrs == ["README.rst", "database1", "database2"], (
            fldrs,
            root_folder,
        )
        fldrs = list_dir(root_folder, files=False)
        assert fldrs == ["database1", "database2"], (fldrs, root_folder)
        fldrs = list_dir(root_folder, folders=False)
        assert fldrs == ["README.rst"], (fldrs, root_folder)
        fldrs = list_dir(root_folder, folders=False, files=False)
        assert fldrs == [], (fldrs, root_folder)

        fldrs = list_dir(root_folder, "database1")
        assert fldrs == ["README1.rst", "protocol1", "protocol2"], (
            fldrs,
            root_folder,
        )
        fldrs = list_dir(root_folder, "database1", files=False)
        assert fldrs == ["protocol1", "protocol2"], (fldrs, root_folder)
        fldrs = list_dir(root_folder, "database1", folders=False)
        assert fldrs == ["README1.rst"], (fldrs, root_folder)

        fldrs = list_dir(root_folder, "database1/protocol1")
        assert fldrs == ["dev.csv", "train.csv"], (fldrs, root_folder)
        fldrs = list_dir(root_folder, "database1/protocol1", files=False)
        assert fldrs == [], (fldrs, root_folder)
        fldrs = list_dir(root_folder, "database1/protocol1", folders=False)
        assert fldrs == ["dev.csv", "train.csv"], (fldrs, root_folder)
