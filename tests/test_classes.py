from typing import List, NewType

import networkx as nx
import pandas as pd
import pytest

from graphtype import Graph, GraphData, validate


def test_empty():
    GEmpty = Graph[GraphData[...]]

    assert GEmpty.graph_columns == set()
    assert GEmpty.graph_dtypes == {}
    assert GEmpty.graph_only_specified == False


def test_columns():
    GName = Graph[GraphData["id", "name"]]

    assert GName.graph_columns == {"id", "name"}
    assert GName.graph_dtypes == {}
    assert GName.graph_only_specified == True


def test_ellipsis():
    GName = Graph[GraphData["id", "name", ...]]

    assert GName.graph_columns == {"id", "name"}
    assert GName.graph_dtypes == {}
    assert GName.graph_only_specified == False


def test_dtypes():
    GName = Graph[GraphData["id":int, "name":object, "location"]]

    assert GName.graph_columns == {"id", "name", "location"}
    assert GName.graph_dtypes == {"id": int, "name": object}
    assert GName.graph_only_specified == True


def test_validate_newtype():
    UserId = NewType("UserId", int)

    g = nx.Graph()
    g.graph["a"] = UserId(1)
    g.graph["b"] = ["list", "of", "strings"]

    h = nx.Graph()

    @validate
    def process(data: Graph[GraphData["a":UserId, "b" : List[str]]]):
        pass

    process(g)

    with pytest.raises(TypeError):
        process(h)


@pytest.mark.skip(reason="Not yet implemented")
def test_nested():
    GName = GraphData["id":int, "name":object]
    GLocation = GraphData["id":int, "longitude":float, "latitude":float]

    GNameLoc = Graph[GName, GLocation]

    assert GNameLoc.graph_columns == {"id", "name", "longitude", "latitude"}
    assert GNameLoc.graph_dtypes == {
        "id": int,
        "name": object,
        "longitude": float,
        "latitude": float,
    }
    assert GNameLoc.graph_only_specified == True

    GNameLocEtc = Graph[GraphData[GNameLoc, "description":object, ...]]
    assert GNameLocEtc.graph_columns == {
        "id",
        "name",
        "longitude",
        "latitude",
        "description",
    }
    assert GNameLocEtc.graph_dtypes == {
        "id": int,
        "name": object,
        "longitude": float,
        "latitude": float,
        "description": object,
    }
    assert GNameLocEtc.graph_only_specified == False


def test_init():
    with pytest.raises(TypeError):
        Graph()
