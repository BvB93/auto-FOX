"""A module for testing files in the :mod:`FOX.functions.utils` module,"""

from os.path import join

import pandas as pd
import numpy as np

from scm.plams import Settings
from assertionlib import assertion

from FOX.functions.utils import (
    assert_error, get_template, template_to_df, serialize_array, read_str_file, get_shape,
    dict_to_pandas
)

PATH = join('tests', 'test_files')


def test_assert_error():
    """Test :func:`FOX.functions.utils.assert_error`,"""
    msg = 'test error {}'
    @assert_error(msg)
    def test_func():
        pass

    assertion.assert_(test_func, exception=ModuleNotFoundError)


def test_get_template():
    """Test :func:`FOX.functions.utils.get_template`,"""
    s = get_template(name='md_cp2k_template.yaml')
    assertion.isinstance(s, Settings)

    dict_ = get_template(name='md_cp2k_template.yaml', as_settings=False)
    assertion.isinstance(dict_, Settings, invert=True)
    assertion.isinstance(dict_, dict)


def test_template_to_df():
    """Test :func:`FOX.functions.utils.template_to_df`,"""
    df = template_to_df('param.yaml', path=PATH)
    assertion.isinstance(df, pd.DataFrame)

    idx = np.array(['charge', 'epsilon', 'sigma'], dtype=object)
    np.testing.assert_array_equal(idx, df.index.values)

    ref = np.array([
        'CG2O3', 'Cd', 'Cd Cd', 'Cd OG2D2', 'Cd Se', 'OG2D2', 'Se', 'Se OG2D2', 'Se Se'
    ], dtype=object)
    ref.sort()

    columns = np.array(df.columns)
    columns.sort()

    np.testing.assert_array_equal(ref, columns)


def test_serialize_array():
    """Test :func:`FOX.functions.utils.serialize_array`,"""
    zeros = np.zeros((10, 2), dtype=bool)
    ref = ('         0         0         0         0         0         0         0         '
           '0\n         0         0         0         0         0         0         0         '
           '0\n         0         0         0         0')
    assertion.eq(serialize_array(zeros), ref)


def test_read_str_file():
    """Test :func:`FOX.functions.utils.read_str_file`,"""
    at, charge = read_str_file(join(PATH, 'ligand.str'))
    assertion.eq(at, ('CG2O3', 'HGR52', 'OG2D2', 'OG2D2'))
    assertion.eq(charge, (0.52, 0.0, -0.76, -0.76))


def test_get_shape():
    """Test :func:`FOX.functions.utils.get_shape`,"""
    a = np.random.rand(100, 10)
    b = a[0:15, 0].tolist()
    c = 5

    assertion.eq(get_shape(a), (100, 10))
    assertion.eq(get_shape(b), (15,))
    assertion.eq(get_shape(c), (1,))


def test_dict_to_pandas():
    """Test :func:`FOX.functions.utils.dict_to_pandas`,"""
    dict_ = {}
    dict_['a'] = {'a1': 1, 'a2': 2, 'a3': 3}
    dict_['b'] = {'b1': 4, 'b2': 5}
    dict_['c'] = {'c1': 6}

    df = dict_to_pandas(dict_)
    idx = pd.MultiIndex.from_tuples([
        ('a', 'a1'), ('a', 'a2'), ('a', 'a3'), ('b', 'b1'), ('b', 'b2'), ('c', 'c1')
    ])
    np.testing.assert_array_equal(df.index, idx)
