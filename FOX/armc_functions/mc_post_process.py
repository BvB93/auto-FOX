"""
FOX.armc_functions.mc_post_process
==================================

Callables for post-processing :class:`MultiMolecule` instances produced by :class:`MonteCarlo`.

Index
-----
.. currentmodule:: FOX.armc_functions.mc_post_process
.. autosummary::
    AtomsFromPSF

API
---
.. autoclass:: AtomsFromPSF

"""

from typing import Iterable, MutableSequence, Optional, MutableMapping

from ..io.read_psf import PSFContainer
from ..classes.multi_mol import MultiMolecule

__all__ = ['AtomsFromPSF']

AtomMapping = MutableMapping[str, MutableSequence[int]]


class AtomsFromPSF:
    r"""A callable for updating the atoms of a :class:`MultiMolecule` instances.

    Examples
    --------
    .. code:: python

        >>> from typing import Callable
        >>> from FOX import PSFContainer, MultiMolecule

        >>> psf_list = [PSFContainer(...), PSFContainer(...), PSFContainer(...)]
        >>> atoms_from_psf: Callable = AtomsFromPSF.from_psf(*psf_list)

        >>> mol_list = [MultiMolecule(...), MultiMolecule(...), MultiMolecule(...)]
        >>> atoms_from_psf(None, mol_list)

    Parameters
    ----------
    \*atom_dict : :class:`dict` [:class:`str`, :class:`list` [:class:`int`]]
        One or more dictionaries with atomic symbols as keys and
        lists of matching atomic indices as values.

    """

    @classmethod
    def from_psf(cls, *psf: PSFContainer) -> 'AtomsFromPSF':
        """Construct a :class:`AtomsFromPsf` instance from one or more :class:`PSFContainer`."""
        try:
            return cls(*[i.to_atom_dict() for i in psf])
        except AttributeError as ex:
            raise TypeError("'psf' expected one or more PSFContainers; "
                            f"{ex}").with_traceback(ex.__traceback__)

    def __init__(self, *atom_dict: AtomMapping) -> None:
        """Initialize the :class:`AtomsFromPsf` instance."""
        self.atom_dict = atom_dict

    def __call__(self, mol_list: Optional[Iterable[MultiMolecule]],
                 mc: Optional['MonteCarlo'] = None) -> None:
        """Update the :attr:`MultiMolecule.atoms` of **mol_list**."""
        if mol_list is None:
            return
        for atom_dict, mol in zip(self.atom_dict, mol_list):
            mol.atoms.update(atom_dict)
