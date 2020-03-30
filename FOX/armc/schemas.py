"""
FOX.armc.schemas
================

A module with template validation functions for the ARMC input.

Index
-----
.. currentmodule:: FOX.armc.schemas
.. autosummary::
{autosummary}

API
---
{autofunction}

"""

import os
from collections import abc
from typing import (overload, Any, SupportsInt, SupportsFloat, Type, Mapping,
                    Callable, Union, Optional, Tuple, FrozenSet, MutableMapping)

import numpy as np
from schema import And, Or, Schema, Use, Optional as Optional_

from scm.plams import Settings
from qmflows import cp2k_mm
from qmflows.packages import Package

from .armc import ARMC
from .monte_carlo import MonteCarloABC
from .package_manager import PackageManager, PackageManagerABC
from .phi_updater import PhiUpdater, PhiUpdaterABC
from .param_mapping import ParamMapping, ParamMappingABC
from ..type_hints import Literal, SupportsArray, TypedDict, NDArray
from ..classes import MultiMolecule
from ..functions.utils import get_importable, _get_move_range

__all__ = [
    'validate_phi', 'validate_monte_carlo', 'validate_psf', 'validate_pes',
    'validate_job', 'validate_sub_job', 'validate_param', 'validate_main'
]


@overload
def supports_float(value: SupportsFloat) -> Literal[True]: ...
@overload
def supports_float(value: Any) -> bool: ...
def supports_float(value):  # noqa: E302
    """Check if a float-like object has been passed (:data:`~typing.SupportsFloat`)."""
    try:
        value.__float__()
        return True
    except Exception:
        return False


@overload
def supports_int(value: SupportsInt) -> Literal[True]: ...
@overload
def supports_int(value: Any) -> bool: ...
def supports_int(value):  # noqa: E302
    """Check if a int-like object has been passed (:data:`~typing.SupportsInt`)."""
    # floats that can be exactly represented by an integer are also fine
    try:
        value.__int__()
        return float(value).is_integer()
    except Exception:
        return False


main_schema = Schema({
    'param': Or(
        And(abc.MutableMapping, lambda n: all(isinstance(k, str) for k in n.keys())),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k in n.keys()), Use(dict))
    ),

    'pes': Or(
        And(abc.MutableMapping, lambda n: all(isinstance(k, str) for k in n.keys())),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k in n.keys()), Use(dict))
    ),

    'job': Or(
        And(abc.MutableMapping, lambda n: all(isinstance(k, str) for k in n.keys())),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k in n.keys()), Use(dict))
    ),

    Optional_('monte_carlo', default=dict): Or(
        And(None, lambda n: {}),
        And(abc.MutableMapping, lambda n: all(isinstance(k, str) for k in n.keys())),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k in n.keys()), Use(dict))
    ),

    Optional_('phi', default=dict): Or(
        And(None, lambda n: {}),
        And(abc.MutableMapping, lambda n: all(isinstance(k, str) for k in n.keys())),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k in n.keys()), Use(dict))
    ),

    Optional_('psf', default=None): Or(
        And(None, lambda n: {}),
        And(abc.MutableMapping, lambda n: all(isinstance(k, str) for k in n.keys())),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k in n.keys()), Use(dict))
    )
})


class MainDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`main_schema`."""

    param: MutableMapping[str, Any]
    pes: MutableMapping[str, Any]
    job: MutableMapping[str, Any]
    monte_carlo: MutableMapping[str, Any]
    phi: MutableMapping[str, Any]
    psf: MutableMapping[str, Any]


#: Schema for validating the ``"phi"`` block.
phi_schema = Schema({
    Optional_('type', default=lambda: PhiUpdater): Or(
        And(None, Use(lambda n: PhiUpdater())),
        And(str, Use(lambda n: get_importable(n, lambda i: issubclass(i, PhiUpdaterABC)))),
        And(type, lambda n: issubclass(n, PhiUpdaterABC))
    ),

    Optional_('phi', default=1.0): Or(
        And(None, Use(lambda n: 1.0)),
        And(supports_float, Use(float)),
    ),

    Optional_('gamma', default=2.0): Or(
        And(None, Use(lambda n: 2.0)),
        And(supports_float, Use(float)),
    ),

    Optional_('a_target', default=0.25): Or(
        And(None, Use(lambda n: 0.25)),
        And(supports_float, lambda n: 0 < float(n) <= 1, Use(float)),
    ),

    Optional_('func', default=lambda: np.add): Or(
        And(None, Use(lambda n: np.add)),
        And(str, Use(lambda n: get_importable(n, lambda i: isinstance(i, abc.Callable)))),
        And(abc.Callable)
    ),

    Optional_('kwargs', default=dict): Or(
        And(None, Use(lambda n: {})),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k, _ in n.items()))
    )
})


class PhiDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`phi_schema`."""

    type: Type[PhiUpdaterABC]
    phi: float
    gamma: float
    a_target: float
    func: Callable[[float, float], float]
    kwargs: Mapping[str, Any]


#: Schema for validating the ``"monte_carlo"`` block.
mc_schema = Schema({
    Optional_('type', default=lambda: ARMC): Or(
        And(None, Use(lambda n: ARMC)),
        And(str, Use(lambda n: get_importable(n, lambda i: issubclass(i, MonteCarloABC)))),
        And(type, lambda n: issubclass(n, MonteCarloABC))
    ),

    Optional_('iter_len', default=50000): Or(
        And(None, Use(lambda n: 50000)),
        And(supports_int, lambda n: int(n) > 0, Use(int))
    ),

    Optional_('sub_iter_len', default=100): Or(
        And(None, Use(lambda n: 100)),
        And(supports_int, lambda n: int(n) > 0, Use(int))
    ),

    Optional_('hdf5_file', default=lambda: os.path.abspath('armc.hdf5')): Or(
        And(None, Use(lambda n: os.path.abspath('armc.hdf5'))),
        And(str, Use(os.path.abspath)),
        And(os.PathLike, Use(os.path.abspath))
    ),

    Optional_('logfile', default=lambda: os.path.abspath('armc.log')): Or(
        And(None, Use(lambda n: os.path.abspath('armc.log'))),
        And(str, Use(os.path.abspath)),
        And(os.PathLike, Use(os.path.abspath))
    ),

    Optional_('path', default=lambda: os.getcwd()): Or(
        And(None, Use(lambda n: os.getcwd())),
        And(str, Use(os.path.abspath)),
        And(os.PathLike, Use(os.path.abspath))
    ),

    Optional_('folder', default='MM_MD_workdir'): Or(
        And(None, Use(lambda n: 'MM_MD_workdir')),
        str,
        os.PathLike
    ),

    Optional_('keep_files', default=True): Or(
        And(None, Use(lambda n: True)),
        bool
    )
})


class MCDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`mc_schema`."""

    type: Type[MonteCarloABC]
    iter_len: int
    sub_iter_len: int
    hdf5_file: Union[str, os.PathLike]
    logfile: Union[str, os.PathLike]
    path: Union[str, os.PathLike]
    folder: Union[str, os.PathLike]
    keep_files: bool


#: Schema for validating the ``"psf"`` block.
psf_schema = Schema({
    Optional_('str_file', default=None): Or(
        None,
        And(str, Use(lambda n: (n,))),
        And(os.PathLike, Use(lambda n: (n,))),
        And(abc.Sequence, lambda n: all(isinstance(i, (os.PathLike, str)) for i in n), Use(tuple))
    ),

    Optional_('rtf_file', default=None): Or(
        None,
        And(str, Use(lambda n: (n,))),
        And(os.PathLike, Use(lambda n: (n,))),
        And(abc.Sequence, lambda n: all(isinstance(i, (os.PathLike, str)) for i in n), Use(tuple))
    ),

    Optional_('psf_file', default=None): Or(
        None,
        And(str, Use(lambda n: (n,))),
        And(os.PathLike, Use(lambda n: (n,))),
        And(abc.Sequence, lambda n: all(isinstance(i, (os.PathLike, str)) for i in n), Use(tuple))
    ),

    Optional_('ligand_atoms', default=None): Or(
        None,
        And(str, Use(lambda n: frozenset({n}))),
        And(abc.Collection, lambda n: all(isinstance(i, str) for i in n), Use(frozenset))
    ),
})


class PSFDict(TypedDict):
    """A typed dict represneting the output of :data:`psf_schema`."""

    str_file: Optional[Tuple[Union[str, os.PathLike], ...]]
    rtf_file: Optional[Tuple[Union[str, os.PathLike], ...]]
    psf_file: Optional[Tuple[Union[str, os.PathLike], ...]]
    ligand_atoms: Optional[FrozenSet[str]]


#: Schema for validating the ``"pes"`` block.
pes_schema = Schema({
    'func': Or(
        And(str, Use(lambda n: get_importable(n, validate=callable))),
        abc.Callable
    ),

    Optional_('kwargs', default=dict): Or(
        And(None, Use(lambda n: {})),
        And(abc.Mapping, lambda dct: all(isinstance(k, str) for k, _ in dct.items())),
        And(
            abc.Sequence,
            lambda n: all(isinstance(i, abc.Mapping) for i in n),
            lambda n: all(isinstance(k, str) for dct in n for k, _ in dct.items()),
            Use(tuple)
        )
    )
})


class PESDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`pes_schema`."""

    func: Callable
    kwargs: Union[Mapping[str, Any], Tuple[Mapping[str, Any], ...]]


#: Schema for validating the ``"job"`` block.
job_schema = Schema({
    Optional_('type', default=lambda: PackageManager): Or(
        And(None, Use(lambda n: PackageManager)),
        And(str, Use(lambda n: get_importable(n, lambda i: issubclass(i, PackageManagerABC)))),
        And(type, lambda n: issubclass(n, PackageManagerABC))
    ),

    'molecule': Or(
        And(MultiMolecule, Use(lambda n: (n,))),
        And(str, Use(lambda n: (MultiMolecule.from_xyz(n),))),
        And(os.PathLike, Use(lambda n: (MultiMolecule.from_xyz(n),))),
        And(
            abc.Sequence,
            lambda n: all(isinstance(i, (str, os.PathLike, MultiMolecule)) for i in n),
            Use(lambda n: tuple(
                (i if isinstance(i, MultiMolecule) else MultiMolecule.from_xyz(i)) for i in n
            ))
        )
    )
})


class JobDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`job_schema`."""

    type: Type[PackageManagerABC]
    molecule: Tuple[MultiMolecule, ...]


#: Schema for validating sub blocks within the ``"pes"`` block.
sub_job_schema = Schema({
    Optional_('type', default=lambda: cp2k_mm): Or(
        And(None, Use(lambda n: cp2k_mm)),
        And(str, Use(lambda n: get_importable(n, validate=lambda i: isinstance(i, Package)))),
        Package
    ),

    Optional_('name', default='plamsjob'): Or(
        And(None, Use(lambda n: 'plamsjob')),
        str,
    ),

    Optional_('settings', default=Settings): Or(
        And(None, Use(lambda n: Settings())),
        And(abc.Mapping, Use(Settings))
    ),

    Optional_('template', default=Settings): Or(
        And(None, Use(lambda n: Settings())),
        And(str, Use(lambda n: get_importable(n, validate=lambda i: isinstance(i, Settings)))),
    )
})


class SubJobDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`sub_job_schema`."""

    type: Type[Package]
    name: str
    settings: Settings
    template: Settings


MOVE_DEFAULT = np.array([
    0.900, 0.905, 0.910, 0.915, 0.920, 0.925, 0.930, 0.935, 0.940,
    0.945, 0.950, 0.955, 0.960, 0.965, 0.970, 0.975, 0.980, 0.985,
    0.990, 0.995, 1.005, 1.010, 1.015, 1.020, 1.025, 1.030, 1.035,
    1.040, 1.045, 1.050, 1.055, 1.060, 1.065, 1.070, 1.075, 1.080,
    1.085, 1.090, 1.095, 1.100
], dtype=float)
MOVE_DEFAULT.setflags(write=False)


#: Schema for validating the ``"param"`` block.
param_schema = Schema({
    Optional_('type', default=lambda: ParamMapping): Or(
        And(None, Use(lambda n: ParamMapping)),
        And(str, Use(lambda n: get_importable(n, lambda i: issubclass(i, ParamMappingABC)))),
        And(type, lambda n: issubclass(n, ParamMappingABC))
    ),

    Optional_('func', default=lambda: np.multiply): Or(
        And(None, Use(lambda n: np.multiply)),
        And(str, Use(lambda n: get_importable(n, lambda i: isinstance(i, abc.Callable)))),
        And(abc.Callable)
    ),

    Optional_('kwargs', default=dict): Or(
        And(None, Use(lambda n: {})),
        And(abc.Mapping, lambda n: all(isinstance(k, str) for k, _ in n.items())),
    ),

    Optional_('move_range', default=lambda: MOVE_DEFAULT.copy()): Or(
        And(None, Use(lambda n: MOVE_DEFAULT.copy())),
        And(abc.Sequence, Use(lambda n: np.asarray(n, dtype=float))),
        And(SupportsArray, Use(lambda n: np.asarray(n, dtype=float))),
        And(abc.Iterable, Use(lambda n: np.fromiter(n, dtype=float))),
        And(abc.Mapping, lambda n: {'start', 'stop', 'step'} == n.keys(),
            Use(lambda n: _get_move_range(**n)))
    )

})


class ParamDict(TypedDict):
    """A :class:`~typing.TypedDict` representing the output of :data:`param_schema`."""

    type: Type[ParamMappingABC]
    func: Callable[[float, float], float]
    kwargs: Mapping[str, Any]
    move_range: NDArray[float]


def validate_main(mapping: Mapping[str, Any]) -> MainDict:
    """Validate the all super-keys."""
    return main_schema.validate(mapping)


def validate_phi(mapping: Mapping[str, Any]) -> PhiDict:
    """Validate the ``"phi"`` block."""
    return phi_schema.validate(mapping)


def validate_monte_carlo(mapping: Mapping[str, Any]) -> MCDict:
    """Validate the ``"monte_carlo"`` block."""
    return mc_schema.validate(mapping)


def validate_psf(mapping: Mapping[str, Any]) -> PSFDict:
    """Validate the ``"psf"`` block."""
    return psf_schema.validate(mapping)


def validate_pes(mapping: Mapping[str, Any]) -> PESDict:
    """Validate the ``"pes"`` block."""
    return pes_schema.validate(mapping)


def validate_job(mapping: Mapping[str, Any]) -> JobDict:
    """Validate the ``"job"`` block."""
    return job_schema.validate(mapping)


def validate_sub_job(mapping: Mapping[str, Any]) -> SubJobDict:
    """Validate sub-blocks within the ``"job"`` block."""
    return sub_job_schema.validate(mapping)


def validate_param(mapping: Mapping[str, Any]) -> ParamDict:
    """Validate the ``"param"`` block."""
    return param_schema.validate(mapping)


__doc__ = __doc__.format(
    autosummary='\n'.join(f'    {i}' for i in __all__),
    autofunction='\n'.join(f'.. autofunction:: {i}' for i in __all__)
)
