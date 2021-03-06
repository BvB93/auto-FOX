"""
FOX.armc_functions.csv_utils
============================

A module for exporting ARMC result to .csv files.

Index
-----
.. currentmodule:: FOX.armc_functions.csv_utils
.. autosummary::
    dset_to_csv

API
---
.. autofunction:: dset_to_csv

"""

from os import PathLike
from typing import Optional, AnyStr, Union

from ..io.hdf5_utils import from_hdf5


def dset_to_csv(filename_in: Union[AnyStr, PathLike],
                dataset: str,
                filename_out: Union[None, AnyStr, PathLike] = None,
                iteration: int = -1) -> None:
    """Export ARMC results to one or more .csv files.

    A single .csv file will be created for all datasets in **datasets**.

    Parameters
    ----------
    filename_in : str
        The path+name of the ARMC .hdf5 file.

    dataset : |str|_
        The name of the dataset containing the to-be retrieved datasets (*e.g.* ``"aux_error"``).

    filename_out : str
        The path+name of the to-be created image.
        Will default to to **datasets** (appended with ``'.csv'``) if ``None``.

    iteration : int
        The ARMC iteration containg the dataset of interest.
        Only relevant when dealing with datasets with more than three dimensions;
        will be ignored otherwise.

    Returns
    -------
    |matplotlib.figure.Figure|_:
        A matplotlib figure containg PES descriptors.

    """
    filename_out = filename_out or dataset + '.csv'

    # Gather the pes descriptors
    df = from_hdf5(filename_in, dataset)
    if isinstance(df, list):
        df = df[iteration]

    df.to_csv(filename_out)
