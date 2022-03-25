"""Module for DataIO _FileData

Populate and verify stuff in the 'file' block in fmu (partial excpetion is checksum_md5
as this is convinient to populate later, on demand)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from warnings import warn

from fmu.dataionew._utils import C, S

logger = logging.getLogger(__name__)


@dataclass
class _FileDataProvider:
    """Class for providing metadata for the 'files' block in fmu-dataio.

    Example::

        file:
            relative_path: ... (relative to case)
            absolute_path: ...
            checksum_md5: ...  Will be done in anothr routine!
    """

    # input
    cfg: dict
    objdata: Any
    verbosity: str = "CRITICAL"

    # storing results in these variables
    relative_path: Optional[str] = field(default="", init=False)
    absolute_path: Optional[str] = field(default="", init=False)
    checksum_md5: Optional[str] = field(default="", init=False)

    def __post_init__(self):
        logger.setLevel(level=self.verbosity)

        # set internal variables
        self.settings = self.cfg[S]
        self.classvar = self.cfg[C]

        self.basepath = self.settings["basepath"]
        self.name = self.objdata.name
        self.tagname = self.settings["tagname"]
        self.time1 = self.settings["time1"]
        self.time2 = self.settings["time2"]
        self.parentname = self.settings["parentname"]
        self.extension = self.objdata.extension
        self.efolder = self.objdata.efolder

        self.create_folder = self.classvar["createfolder"]
        self.verify_folder = self.classvar["verifyfolder"]
        self.forcefolder = self.settings["forcefolder"]
        self.subfolder = self.settings["subfolder"]
        logger.info("Initialize %s", __class__)

    def derive_filedata(self):
        stem = self._get_filestem()
        relpath = self._get_path()

        path = Path(relpath) / stem.lower()
        path = path.with_suffix(path.suffix + self.extension)

        # resolve() will fix ".." e.g. change '/some/path/../other' to '/some/other'
        abspath = path.resolve()

        relpath = path.relative_to(self.basepath)
        self.relative_path = str(relpath)
        self.absolute_path = str(abspath)
        logger.info("Derived filedata")

    def _get_filestem(self):
        """Construct the file"""

        if not self.name:
            raise ValueError("The 'name' entry is missing for constructing a file name")
        if not self.time1 and self.time2:
            raise ValueError("Not legal: 'time1' is missing while 'time2' is present")

        stem = self.name.lower()
        if self.tagname:
            stem += "--" + self.tagname.lower()
        if self.parentname:
            stem = self.parentname.lower() + "--" + stem

        if self.time1 and not self.time2:
            stem += "--" + (str(self.time1)[0:10]).replace("-", "")

        elif self.time1 and self.time2:
            monitor = (str(self.time1)[0:10]).replace("-", "")
            base = (str(self.time2)[0:10]).replace("-", "")
            if monitor == base:
                warn(
                    "The monitor date and base date are equal", UserWarning
                )  # TODO: consider add clocktimes in such cases?
            stem += "--" + monitor + "_" + base

        stem = stem.replace(".", "_").replace(" ", "_")
        return stem

    def _get_path(self):
        """Get the folder path and verify."""

        outroot = self.basepath / "share" / "results"
        dest = outroot / self.efolder  # e.g. "maps"

        if self.forcefolder:
            dest = self.forcefolder

        if self.subfolder:
            dest = dest / self.subfolder

        if self.create_folder:
            dest.mkdir(parents=True, exist_ok=True)

        # check that destination actually exists if verify_folder is True
        if self.verify_folder and not dest.exists():
            raise IOError(f"Folder {str(dest)} is not present.")

        return dest
