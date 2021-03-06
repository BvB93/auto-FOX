.. _Monte Carlo:

Addaptive Rate Monte Carlo
==========================

The general idea of the MonteCarlo class, and its subclasses, is to fit a
classical potential energy surface (PES) to an *ab-initio* PES by optimizing
the classical forcefield parameters.
This forcefield optimization is conducted using the Addaptive Rate Monte
Carlo (ARMC, 1_) method described by S. Cosseddu *et al* in
*J. Chem. Theory Comput.*, **2017**, *13*, 297–308.

The implemented algorithm can be summarized as following:


The algorithm
-------------

1.  A trial state, :math:`S_{l}`, is generated by moving a random parameter
    retrieved from a user-specified parameter set (*e.g.* atomic charge).

2.  It is checked whether or not the trial state has been previously visited.

    *   If ``True``, retrieve the previously calculated PES.
    *   If ``False``, calculate a new PES with the generated parameters
        :math:`S_{l}`.

.. math::
    :label: 1

    p(k \leftarrow l) =
    \Biggl \lbrace
    {
        1, \quad
            \Delta \varepsilon_{QM-MM} ( S_{k} )
            \; \lt \;
            \Delta \varepsilon_{QM-MM} ( S_{l} )
        \atop
        0, \quad
            \Delta \varepsilon_{QM-MM} ( S_{k} )
            \; \gt \;
            \Delta \varepsilon_{QM-MM} ( S_{l} )
    }

3.  The move is accepted if the new set of parameters, :math:`S_{l}`, lowers
    the auxiliary error (:math:`\Delta \varepsilon_{QM-MM}`) with respect to
    the previous set of accepted parameters, :math:`S_{k}`
    (see :eq:`1`). Given a PES descriptor, :math:`r`, consisting
    of a matrix with :math:`N` elements, the auxiliary error is defined
    in :eq:`2`.

.. math::
    :label: 2

    \Delta \varepsilon_{QM-MM} =
        \frac{
        \sum_{i}^{N}
        \left|
            r_{i}^{QM} - r_{i}^{MM}
        \right |^2}
        {\sum_{i}^{N} r_{i}^{QM} }


4.  The parameter history is updated.
    Based on whether or not the new parameter set is accepted the
    auxiliary error of either :math:`S_{l}` or :math:`S_{k}` is increased
    by the variable :math:`\phi` (see :eq:`3`). In this manner, the
    underlying PES is continuously modified, preventing the optimizer
    from getting stuck in a (local) minima in the parameter space.

.. math::
    :label: 3

    \Delta \varepsilon_{QM-MM} ( S_{k} ) + \phi \quad \text{if}
    \quad \Delta \varepsilon_{QM-MM} ( S_{k} ) \; \lt \; \Delta \varepsilon_{QM-MM} ( S_{l} )
    \atop
    \Delta \varepsilon_{QM-MM} ( S_{l} ) + \phi \quad \text{if}
    \quad \Delta \varepsilon_{QM-MM} ( S_{k} ) \; \gt \; \Delta \varepsilon_{QM-MM} ( S_{l} )

5.  The parameter :math:`\phi` is updated at regular intervals
    in order to maintain a constant acceptance rate, :math:`\alpha_{t}`.
    This is illustrated in :eq:`4`, where :math:`\phi` is updated
    the begining of every super-iteration :math:`\kappa`. In this example
    the total number of iterations, :math:`\kappa \omega`, is divided into
    :math:`\kappa` super- and :math:`\omega` sub-iterations.

.. math::
    :label: 4

    \phi_{\kappa \omega} =
    \phi_{ ( \kappa - 1 ) \omega} * \gamma^{
        \text{sgn} ( \alpha_{t} - \overline{\alpha}_{ ( \kappa - 1 ) })
    }
    \quad
    \kappa = 1, 2, 3, ..., N


Arguments
---------

========================== ================== =================================================================================================================
 Parameter                  Default            Parameter description
========================== ================== =================================================================================================================
 param.prm_file             -                  The path+filename of a CHARMM parameter file.
 param.charge               -                  A dictionary with atoms and matching atomic charges.
 param.epsilon              -                  A dictionary with atom-pairs and the matching Lennard-Jones :math:`\epsilon` parameter.
 param.sigma                -                  A dictionary with atom-pairs and the matching Lennard-Jones :math:`\sigma` parameter.

 psf.str_file               -                  The path+filename to one or more stream file; used for assigning atom types and charges to ligands.
 psf.rtf_file               -                  The path+filename to one or more MATCH-produced rtf file; used for assigning atom types and charges to ligands.
 psf.psf_file               -                  The path+filename to one or more psf files; used for assigning atom types and charges to ligands.
 psf.ligand_atoms           -                  All atoms within a ligand, used for defining residues.

 pes                        -                  A dictionary holding one or more functions for constructing PES descriptors.

 molecule                   -                  A list of one or more :class:`.MultiMolecule` instances or .xyz filenames of a reference PES.

 job.logfile                armc.log           The path+filename for the to-be created `PLAMS logfile <https://www.scm.com/doc/plams/components/functions.html#logging>`_.
 job.job_type               scm.plams.Cp2kJob  The job type, see Job_.
 job.name                   armc               The base name of the various molecular dynamics jobs.
 job.path                   .                  The base path for storing the various molecular dynamics jobs.
 job.folder                 MM_MD_workdir      The name of the to-be created directory for storing all molecular dynamics jobs.
 job.keepfiles              False              Whether the raw MD results should be saved or deleted.
 job.md_settings            -                  A dictionary with the MD job settings. Alternativelly,  the filename of YAML_ file can be supplied.
 job.preopt_setting         -                  A dictionary of geometry preoptimization job settings. Suplemented by job.md_settings.

 hdf5_file                  ARMC.hdf5          The filename of the to-be created HDF5_ file with all ARMC results.

 armc.iter_len              50000              The total number of ARMC iterations :math:`\kappa \omega`.
 armc.sub_iter_len          100                The length of each ARMC subiteration :math:`\omega`.
 armc.gamma                 2.0                The constant :math:`\gamma`, see :eq:`4`.
 armc.a_target              0.25               The target acceptance rate :math:`\alpha_{t}`, see :eq:`4`.
 armc.phi                   1.0                The initial value of the variable :math:`\phi`, see :eq:`3` and :eq:`4`.

 move.range.start           0.005              Controls the minimum stepsize of Monte Carlo moves.
 move.range.stop            0.1                Controls the maximum stepsize of Monte Carlo moves.
 move.range.step            0.005              Controls the allowed stepsize values between the minima and maxima.
========================== ================== =================================================================================================================

Once a the .yaml file with the ARMC settings has been sufficiently customized
the parameter optimization can be started via the command prompt with:
:code:`init_armc my_settings.yaml`.

Previous caculations can be continued with :code:`init_armc my_settings.yaml --restart True`.


The pes block
-------------

Potential energy surface (PES) descriptors can be descriped in the ``"pes"`` block.
Provided below is an example where the radial dsitribution function (RDF) is
used as PES descriptor, more specifically the RDF constructed from all possible
combinations of cadmium, selenium and oxygen atoms.

::

    pes:
        rdf:
            func: FOX.MultiMolecule.init_rdf
            kwarg:
                atom_subset: [Cd, Se, O]

Depending on the system of interest it might be of interest to utilize a PES
descriptor other than the RDF, or potentially even multiple PES descriptors.
In the latter case the the total auxiliary error is defined as the sum of the
auxiliary errors of all individual PES descriptors, :math:`R` (see :eq:`5`).

.. math::
    :label: 5

    \Delta \varepsilon_{QM-MM} = \sum_{r}^{R} \Delta \varepsilon_{r}^{QM-MM}


An example is provided below where both radial and angular distribution
functions (RDF and ADF, respectively) are are used as PES descriptors.
In this example the RDF is construced for all combinations of
cadmium, selenium and oxygen atoms (Cd, Se & O),
whereas the ADF is construced for all combinations of cadmium and
selenium atoms (Cd & Se).

::

    pes:
        rdf:
            func: FOX.MultiMolecule.init_rdf
            args: []
            kwargs:
                atom_subset: [Cd, Se, O]

        adf:
            func: FOX.MultiMolecule.init_adf
            args: []
            kwargs:
                atom_subset: [Cd, Se]

In principle any function, class or method can be provided here,
as type object, as long as the following requirements are fulfilled:

* The name of the block must consist of a user-specified string
  (``"rdf"`` and ``"adf"`` in the example(s) above).
* The ``"func"`` key must contain a string representation of thee requested
  function, method or class.
  Auto-FOX will internally convert the string into a callable object.
* The supplied callable *must* be able to operate on NumPy arrays or
  instances of its :class:`.MultiMolecule` subclass.
* Arguments and keyword argument can be provided with the
  ``"args"`` and ``"kwargs"`` keys, respectively.
  The ``"args"`` and ``"kwargs"`` keys are entirely optional and
  can be skipped if desired.

An example of a custom, albit rather nonsensical, PES descriptor involving the
numpy.sum_ function is provided below:

::

  pes:
    numpy_sum:
        func: numpy.sum
        kwargs:
            axis: 0

This .yaml input, given a :class:`.MultiMolecule` instance ``mol``, is equivalent to:

.. code:: python

    >>> import numpy

    >>> func = numpy.sum
    >>> args = []
    >>> kwargs = {'axis': 0}

    >>> func(mol, *arg, **kwarg)


The param block
---------------

::

    param:
        charge:
            keys: [input, force_eval, mm, forcefield, charge]
            constraints:
                -  0 < Cs < 2
                -  1 < Pb < 3
                -  Cs == 0.5 * Br
            Cs: 1.000
            Pb: 2.000
        epsilon:
            unit: kjmol
            keys: [input, force_eval, mm, forcefield, nonbonded, lennard-jones]
            Cs Cs: 0.1882
            Cs Pb: 0.7227
            Pb Pb: 2.7740
        sigma:
            unit: nm
            keys: [input, force_eval, mm, forcefield, nonbonded, lennard-jones]
            constraints: 'Cs Cs == Pb Pb'
            Cs Cs: 0.60
            Cs Pb: 0.50
            Pb Pb: 0.60

The ``"param"`` key in the .yaml input contains all user-specified
to-be optimized parameters.


There are three critical (and two optional) components to the ``"param"``
block:

    * The key of each block (charge_, epsilon_ & sigma_).
    * The ``"keys"`` sub-block, which points to the section path in the CP2K settings (*e.g.* `['input', 'force_eval', 'mm', 'forcefield', 'charge'] <https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/CHARGE.html>`_).
    * The sub-blocks containing either singular atoms_ or `atom pairs <https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/NONBONDED/LENNARD-JONES.html#list_ATOMS>`_.

Together, these three components point to the appropiate path of the
forcefield parameter(s) of interest.
As of the moment, all bonded and non-bonded potentials implemented in
CP2K_ can be accessed via this section of the input file.
For example, the following input is suitable if one wants to optimize a `torsion potential <https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/TORSION.html#list_K>`_
(starting from :math:`k = 10 \ kcal/mol`) for all C-C-C-C bonds:

::

    param:
        k:
            keys: [input, force_eval, mm, forcefield, torsion]
            unit: kcalmol
            C C C C: 10

Besides the three above-mentioned mandatory components, one can
(optionally) supply the unit_ of the parameter and/or constrain
its value to a certain range.
When supplying units, it is the responsibility of the user to ensure
the units are supported by CP2K.
Furthermore, parameter constraints are, as of the moment, limited to specifying
minimum and/or maximum values (*e.g.* :code:`0 < Cs < 2`).
Additional (more elaborate) constrainst are currently already available for
atomic charges in the ``move.charge_constraints`` block (see below).


Parameter Guessing
------------------

::

    param:
        epsilon:
            unit: kjmol
            keys: [input, force_eval, mm, forcefield, nonbonded, lennard-jones]
            Cs Cs: 0.1882
            Cs Pb: 0.7227
            Pb Pb: 2.7740
            guess: rdf
        sigma:
            unit: nm
            keys: [input, force_eval, mm, forcefield, nonbonded, lennard-jones]
            frozen:
                guess: uff

.. math::

    V_{LJ} = 4 \varepsilon
    \left(
        \left(
            \frac{\sigma}{r}
        \right )^{12} -
        \left(
            \frac{\sigma}{r}
        \right )^6
    \right )

Non-bonded interactions (*i.e.* the Lennard-Jones :math:`\varepsilon` and
:math:`\sigma` values) can be guessed if they're not explicitly by the user.
There are currently two implemented guessing procedures: ``"uff"`` and
``"rdf"``.
Parameter guessing for parameters other than :math:`\varepsilon` and
:math:`\sigma` is not supported as of the moment.

The ``"uff"`` approach simply takes all missing parameters from
the Universal Force Field (UFF)[2_].
Pair-wise parameters are construcetd using the standard combinatorial rules:
the arithmetic mean for :math:`\sigma` and the geometric mean for
:math:`\varepsilon`.

The ``"rdf"`` approach utilizes the radial distribution function for
estimating :math:`\sigma` and :math:`\varepsilon`.
:math:`\sigma` is taken as the base of the first RDF peak,
while the first minimum of the Boltzmann-inverted RDF is taken as
:math:`\varepsilon`.

``"crystal_radius"`` and ``"ion_radius"`` use a similar approach to ``"uff"``,
the key difference being the origin of the parameters:
`10.1107/S0567739476001551 <https://doi.org/10.1107/S0567739476001551>`_:
R. D. Shannon, Revised effective ionic radii and systematic studies of
interatomic distances in halides and chalcogenides, *Acta Cryst.* (1976). A32, 751-767.
Note that:

* Values are averaged with respect to all charges and coordination numbers per atom type.
* These two guess-types can only be used for estimating :math:`\sigma` parameters.

If ``"guess"`` is placed within the ``"frozen"`` block, than the guessed
parameters will be treated as constants rather than to-be optimized variables.

.. admonition:: Note

    The guessing procedure requires the presence of both a .prm and .psf file.
    See the ``"prm_file"`` and ``"psf"`` blocks, respectively.


State-averaged ARMC
-------------------

::

    ...

    molecule:
        - /path/to/md_acetate.xyz
        - /path/to/md_phosphate.xyz
        - /path/to/md_sulfate.xyz

    psf:
        rtf_file:
            - acetate.rtf
            - phosphate.rtf
            - sulfate.rtf
        ligand_atoms: [S, P, O, C, H]

    pes:
        rdf:
            func: FOX.MultiMolecule.init_rdf
            kwargs:
                - atom_subset: [Cd, Se, O]
                - atom_subset: [Cd, Se, P, O]
                - atom_subset: [Cd, Se, S, O]

    ...


FOX.MonteCarlo API
------------------

.. autoclass:: FOX.classes.monte_carlo.MonteCarlo
    :members:


FOX.ARMC API
------------

.. autoclass:: FOX.classes.armc.ARMC
    :members:


.. _1: https://dx.doi.org/10.1021/acs.jctc.6b01089
.. _2: https://doi.org/10.1021/ja00051a040
.. _YAML: https://yaml.org/
.. _HDF5: https://www.h5py.org/
.. _Job: https://www.scm.com/doc/plams/components/jobs.html#scm.plams.core.basejob.Job
.. _numpy.sum: https://docs.scipy.org/doc/numpy/reference/generated/numpy.sum.html
.. _CP2K: https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD.html

.. _charge: https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/CHARGE.html#list_CHARGE
.. _epsilon: https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/NONBONDED/LENNARD-JONES.html#list_EPSILON
.. _sigma: https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/NONBONDED/LENNARD-JONES.html#list_SIGMA
.. _atoms: https://manual.cp2k.org/trunk/CP2K_INPUT/FORCE_EVAL/MM/FORCEFIELD/CHARGE.html#ATOM
.. _unit: https://manual.cp2k.org/cp2k-6_1-branch/units.html
