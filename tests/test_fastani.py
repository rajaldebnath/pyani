"""Test fastani.py module.

These tests are intended to be run from the repository root using:

pytest -v
"""

import os

from pathlib import Path
from typing import List, NamedTuple, Tuple

import pandas as pd
import pytest

from pandas.util.testing import assert_frame_equal

from pyani import fastani, pyani_files, pyani_tools


### Some classes... to be decided


class ComparisonResult(NamedTuple):
    reference: Path
    query: Path
    ani: float
    matches: int
    fragments: int


class fastANIParsed(NamedTuple):

    """Convenience struct for fastANI .fastani file and associated parsed output."""

    filename: Path
    data: ComparisonResult


@pytest.fixture
def fastanifile_parsed(dir_fastani_in):  # works
    """Example parsed fastANI file."""
    return fastANIParsed(
        dir_fastani_in / "ecoli_vs_shiga.fastani",
        ComparisonResult("ecoli.fna", "shiga.fna", 97.664, 1322, 1547),
    )


def test_fastanifile_parsing(fastanifile_parsed):  # works
    """Check parsing of test fastANI .fastani file."""
    result = fastani.parse_fastani_file(fastanifile_parsed.filename)[0]
    assert result == fastanifile_parsed.data


# Test fastANI command generation
def test_fastani_single(tmp_path, path_file_two):  # works
    """Generate single fastANI command line."""
    fastcmd = fastani.construct_fastani_cmdline(
        path_file_two[0], path_file_two[1], outdir=tmp_path
    )
    dir_fastani = tmp_path
    expected = (
        f"fastANI -q {path_file_two[0]} -r {path_file_two[1]} "
        f"-o {dir_fastani / str(path_file_two[0].stem + '_vs_' + path_file_two[1].stem + '.fastani')} "
        f"--fragLen 3000 -k 16 --minFraction 0.2"
    )
    assert fastcmd == expected


def test_fastani_multiple(fastani_cmds_four):
    """Generate multiple abstract fastANI command-liens.

    Tests that all the input files are correctly-paired.
    """
    cmds = fastani.generate_fastani_commands(fastani_cmds_four.infiles)
    print(f"\n{cmds}")
    print((fastani_cmds_four.fastcmds))
    assert cmds == (fastani_cmds_four.fastcmds)


def test_fastani_job_generation(fastani_cmds_four):
    """Generate dependency"""

    joblist = fastani.generate_fastani_jobs(fastani_cmds_four.infiles, jobprefix="test")
    assert len(joblist) == 6  # ¶ I might want a different number

    for idx, job in enumerate(joblist):
        assert job.name == "test_%06d-fast" % idx
