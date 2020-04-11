# Copyright 2019-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import numpy as np
import pytest
from braket.circuits import Gate, Observable

testdata = [
    (Observable.I(), Gate.I(), ["i"]),
    (Observable.X(), Gate.X(), ["x"]),
    (Observable.Y(), Gate.Y(), ["y"]),
    (Observable.Z(), Gate.Z(), ["z"]),
    (Observable.H(), Gate.H(), ["h"]),
]

invalid_hermitian_matrices = [
    (np.array([[1]])),
    (np.array([1])),
    (np.array([0, 1, 2])),
    (np.array([[0, 1], [1, 2], [3, 4]])),
    (np.array([[0, 1, 2], [2, 3]])),
    (np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])),
    (np.array([[0, 1], ["a", 0]])),
    (Gate.T().to_matrix()),
]


@pytest.mark.parametrize("testobject,gateobject,expected_ir", testdata)
def test_to_ir(testobject, gateobject, expected_ir):
    expected = expected_ir
    actual = testobject.to_ir()
    assert actual == expected


@pytest.mark.parametrize("testobject,gateobject,expected_ir", testdata)
def test_gate_equality(testobject, gateobject, expected_ir):
    assert testobject.qubit_count == gateobject.qubit_count
    assert testobject.ascii_symbols == gateobject.ascii_symbols
    assert testobject.matrix_equivalence(gateobject)


# Hermitian


@pytest.mark.xfail(raises=ValueError)
@pytest.mark.parametrize("matrix", invalid_hermitian_matrices)
def test_hermitian_invalid_matrix(matrix):
    Observable.Hermitian(matrix=matrix)


def test_hermitian_equality():
    matrix = Observable.H().to_matrix()
    a1 = Observable.Hermitian(matrix=matrix)
    a2 = Observable.Hermitian(matrix=matrix)
    a3 = Observable.Hermitian(matrix=Observable.I().to_matrix())
    a4 = "hi"
    assert a1 == a2
    assert a1 != a3
    assert a1 != a4


def test_hermitian_to_ir():
    matrix = Observable.I().to_matrix()
    obs = Observable.Hermitian(matrix=matrix)
    assert obs.to_ir() == [[[[1, 0], [0, 0]], [[0, 0], [1, 0]]]]


# TensorProduct


def test_tensor_product_to_ir():
    t = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    assert t.to_ir() == ["z", "i", "x"]
    assert t.qubit_count == 3
    assert t.ascii_symbols == tuple(["Z@I@X"] * 3)


def test_tensor_product_matmul_tensor():
    t1 = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    t2 = Observable.TensorProduct(
        [Observable.Hermitian(matrix=Observable.I().to_matrix()), Observable.Y()]
    )
    t3 = t1 @ t2
    assert t3.to_ir() == ["z", "i", "x", [[[1.0, 0], [0, 0]], [[0, 0], [1.0, 0]]], "y"]
    assert t3.qubit_count == 5
    assert t3.ascii_symbols == tuple(["Z@I@X@Hermitian@Y"] * 5)


def test_tensor_product_matmul_observable():
    t1 = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    o1 = Observable.I()
    t = t1 @ o1
    assert t.to_ir() == ["z", "i", "x", "i"]
    assert t.qubit_count == 4
    assert t.ascii_symbols == tuple(["Z@I@X@I"] * 4)


@pytest.mark.xfail(raises=ValueError)
def test_tensor_product_value_error():
    Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()]) @ "a"


def test_tensor_product_rmatmul_observable():
    t1 = Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])
    o1 = Observable.I()
    t = o1 @ t1
    assert t.to_ir() == ["i", "z", "i", "x"]
    assert t.qubit_count == 4
    assert t.ascii_symbols == tuple(["I@Z@I@X"] * 4)


@pytest.mark.xfail(raises=ValueError)
def test_tensor_product_rmatmul_value_error():
    "a" @ Observable.TensorProduct([Observable.Z(), Observable.I(), Observable.X()])