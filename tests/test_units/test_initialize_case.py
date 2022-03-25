"""Test the dataio running from within RMS interactive as context.

In this case a user sits in RMS, which is in folder rms/model and runs
interactive. Hence the basepath will be ../../
"""
import logging
import os

import pytest

from fmu.dataionew.dataionew import G, InitializeCase

logger = logging.getLogger(__name__)


def test_inicase_barebone(globalconfig2):

    icase = InitializeCase(globalconfig2)
    assert "Drogon" in str(icase.cfg[G])


def test_inicase_pwd_basepath(fmurun, globalconfig2):

    logger.info("Active folder is %s", fmurun)
    os.chdir(fmurun)

    icase = InitializeCase(globalconfig2)
    icase._establish_pwd_basepath()

    logger.info("Basepath is %s", icase.basepath)

    assert icase.basepath == fmurun
    assert icase.pwd == fmurun


def test_inicase_generate_case_metadata(fmurun, globalconfig2):

    logger.info("Active folder is %s", fmurun)
    os.chdir(fmurun)

    icase = InitializeCase(globalconfig2, verbosity="INFO")
    icase.generate_case_metadata()


def test_inicase_generate_case_metadata_exists_so_fails(
    fmurun_w_casemetadata, globalconfig2
):

    logger.info("Active folder is %s", fmurun_w_casemetadata)
    os.chdir(fmurun_w_casemetadata)

    icase = InitializeCase(globalconfig2, verbosity="INFO")
    with pytest.raises(ValueError):
        icase.generate_case_metadata()


# def test_inicase_generate_case_metadata_exists_but_force(
#     fmurun_w_casemetadata, globalconfig2
# ):

#     logger.info("Active folder is %s", fmurun_w_casemetadata)
#     os.chdir(fmurun_w_casemetadata)
#     icase = InitializeCase(globalconfig2, verbosity="INFO")
#     current_case = icase._get_case_metadata()
#     logger.debug("Current case metadata\n%s", prettyprint_dict(current_case))

#     icase.generate_case_metadata(force=True)
#     icase.export(force=True)
#     new_case = icase._get_case_metadata()
#     logger.debug("New case metadata\n%s", prettyprint_dict(new_case))

#     assert current_case["masterdata"] == new_case["masterdata"]
#     assert current_case["class"] == new_case["class"]

#     assert current_case["fmu"]["case"]["user"]["id"] == "peesv"
#     print(new_case["fmu"]["case"]["user"]["id"])  # == "drogon"
