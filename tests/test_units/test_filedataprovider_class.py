"""Test the _MetaData class from the _metadata.py module"""
import os
from pathlib import Path

import pytest

from fmu.dataionew._filedata_provider import _FileDataProvider
from fmu.dataionew._objectdata_provider import _ObjectDataProvider
from fmu.dataionew._utils import C, S


def get_cfg(tagname, parentname, time1, time2):
    cfg = dict()

    cfg[S] = {
        "basepath": "casepath",
        "tagname": tagname,
        "parentname": parentname,
        "time1": time1,
        "time2": time2,
        "extension": ".ext",
        "efolder": "efolder",
        "forcefolder": "",
        "subfolder": "",
    }
    cfg[C] = {
        "createfolder": False,
        "verifyfolder": False,
    }
    return cfg


@pytest.mark.parametrize(
    "name, tagname, parentname, time1, time2, expected",
    [
        (
            "name",
            "tag",
            "parent",
            "2022-01-02",
            "2020-01-01",
            "parent--name--tag--20220102_20200101",
        ),
        (
            "name",
            "",
            "",
            "2022-01-02",
            "2020-01-01",
            "name--20220102_20200101",
        ),
        (
            "name",
            "",
            "",
            "2022-01-02",
            "",
            "name--20220102",
        ),
        (
            "name",
            "",
            "",
            "",
            "",
            "name",
        ),
        (
            "name",
            "",
            "",
            20220102,
            20210101,
            "name--20220102_20210101",
        ),
    ],
)
def test_get_filestem(
    regsurf,
    internalcfg1,
    name,
    tagname,
    parentname,
    time1,
    time2,
    expected,
):
    """Testing the private _get_filestem method."""
    objdata = _ObjectDataProvider(regsurf, internalcfg1)
    objdata.name = name

    cfg = get_cfg(tagname, parentname, time1, time2)

    fdata = _FileDataProvider(
        cfg,
        objdata,
    )

    stem = fdata._get_filestem()
    assert stem == expected


@pytest.mark.parametrize(
    "name, tagname, parentname, time1, time2, message",
    [
        (
            "",
            "tag",
            "parent",
            "2022-01-02",
            "2020-01-01",
            "'name' entry is missing",
        ),
        (
            "name",
            "tag",
            "parent",
            "",
            "2020-01-01",
            "'time1' is missing while",
        ),
    ],
)
def test_get_filestem_shall_fail(
    regsurf,
    internalcfg1,
    name,
    tagname,
    parentname,
    time1,
    time2,
    message,
):
    """Testing the private _get_filestem method when it shall fail."""
    objdata = _ObjectDataProvider(regsurf, internalcfg1)
    objdata.name = name

    cfg = get_cfg(tagname, parentname, time1, time2)

    fdata = _FileDataProvider(cfg, objdata)

    with pytest.raises(ValueError) as msg:
        _ = fdata._get_filestem()
        assert message in str(msg)


def test_get_paths_path_exists_already(regsurf, internalcfg1, tmp_path):
    """Testing the private _get_path method."""

    os.chdir(tmp_path)
    newpath = tmp_path / "share" / "results" / "efolder"
    newpath.mkdir(parents=True, exist_ok=True)

    cfg = get_cfg("tag", "parent", "t1", "t2")
    cfg[S]["basepath"] = Path(".")

    objdata = _ObjectDataProvider(regsurf, internalcfg1)
    objdata.name = "some"
    objdata.efolder = "efolder"

    fdata = _FileDataProvider(cfg, objdata)

    path = fdata._get_path()
    assert str(path) == "share/results/efolder"


def test_get_paths_not_exists_so_create(regsurf, internalcfg1, tmp_path):
    """Testing the private _get_path method, creating the path."""

    os.chdir(tmp_path)

    objdata = _ObjectDataProvider(regsurf, internalcfg1)
    objdata.name = "some"
    objdata.efolder = "efolder"

    cfg = get_cfg("tag", "parent", "t1", "t2")
    cfg[C]["createfolder"] = True
    cfg[S]["basepath"] = Path(".")

    fdata = _FileDataProvider(cfg, objdata)

    path = fdata._get_path()
    assert str(path) == "share/results/efolder"


def test_filedata_provider(regsurf, internalcfg1, tmp_path):
    """Testing the derive_filedata function."""

    os.chdir(tmp_path)

    objdata = _ObjectDataProvider(regsurf, internalcfg1)
    objdata.name = "name"
    objdata.efolder = "efolder"
    objdata.extension = ".ext"

    cfg = get_cfg("tag", "parent", "t1", "t2")
    cfg[C]["createfolder"] = True
    cfg[S]["basepath"] = Path(".")

    fdata = _FileDataProvider(cfg, objdata)
    fdata.derive_filedata()

    print(fdata.relative_path)
    assert fdata.relative_path == "share/results/efolder/parent--name--tag--t1_t2.ext"
    absdata = str(tmp_path / "share/results/efolder/parent--name--tag--t1_t2.ext")
    assert fdata.absolute_path == absdata
