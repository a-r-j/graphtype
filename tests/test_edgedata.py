from typing import List, NewType

import networkx as nx
import pandas as pd
import pytest

from graphtype import EdgeData, Graph, validate


def test_empty():
    EEmpty = Graph[EdgeData[...]]

    assert EEmpty.edge_columns == set()
    assert EEmpty.edge_dtypes == {}
    assert EEmpty.edge_only_specified == False


def test_columns():
    EName = Graph[EdgeData["id", "name"]]

    assert EName.edge_columns == {"id", "name"}
    assert EName.edge_dtypes == {}
    assert EName.edge_only_specified == True


def test_ellipsis():
    EName = Graph[EdgeData["id", "name", ...]]

    assert EName.edge_columns == {"id", "name"}
    assert EName.edge_dtypes == {}
    assert EName.edge_only_specified == False


def test_dtypes():
    EName = Graph[EdgeData["id":int, "name":object, "location"]]

    assert EName.edge_columns == {"id", "name", "location"}
    assert EName.edge_dtypes == {"id": int, "name": object}
    assert EName.edge_only_specified == True


def test_validate_newtype():
    UserId = NewType("UserId", int)

    g = nx.Graph()
    g = nx.Graph([(1, 2)])
    nx.set_edge_attributes(
        g,
        {(1, 2): {"feature1": UserId(2), "feature2": ["list", "of", "strings"]}},
    )

    h = nx.Graph()

    @validate
    def process(data: Graph[EdgeData["feature1":UserId, "feature2" : List[str]]]):
        pass

    process(g)

    with pytest.raises(TypeError):
        process(h)


@pytest.mark.skip(reason="Not yet implemented")
def test_nested():
    EName = EdgeData["id":int, "name":object]
    ELocation = EdgeData["id":int, "longitude":float, "latitude":float]

    ENameLoc = Graph[EName, ELocation]

    assert ENameLoc.edge_columns == {"id", "name", "longitude", "latitude"}
    assert ENameLoc.edge_dtypes == {
        "id": int,
        "name": object,
        "longitude": float,
        "latitude": float,
    }
    assert ENameLoc.edge_only_specified == True

    ENameLocEtc = Graph[EdgeData[ENameLoc, "description":object, ...]]
    assert ENameLocEtc.edge_columns == {
        "id",
        "name",
        "longitude",
        "latitude",
        "description",
    }
    assert ENameLocEtc.edge_dtypes == {
        "id": int,
        "name": object,
        "longitude": float,
        "latitude": float,
        "description": object,
    }
    assert ENameLocEtc.edge_only_specified == False


def test_init():
    with pytest.raises(TypeError):
        Graph()
