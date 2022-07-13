from typing import List, NewType

import networkx as nx
import pandas as pd
import pytest

from graphtype import Graph, NodeData, validate


def test_empty():
    NEmpty = Graph[NodeData[...]]

    assert NEmpty.node_columns == set()
    assert NEmpty.node_dtypes == {}
    assert NEmpty.node_only_specified == False


def test_columns():
    NName = Graph[NodeData["id", "name"]]

    assert NName.node_columns == {"id", "name"}
    assert NName.node_dtypes == {}
    assert NName.node_only_specified == True


def test_ellipsis():
    NName = Graph[NodeData["id", "name", ...]]

    assert NName.node_columns == {"id", "name"}
    assert NName.node_dtypes == {}
    assert NName.node_only_specified == False


def test_dtypes():
    NName = Graph[NodeData["id":int, "name":object, "location"]]

    assert NName.node_columns == {"id", "name", "location"}
    assert NName.node_dtypes == {"id": int, "name": object}
    assert NName.node_only_specified == True


def test_validate_newtype():
    UserId = NewType("UserId", int)

    g = nx.Graph()
    g = nx.Graph([(1, 2)])
    nx.set_node_attributes(
        g,
        {
            1: {"feature1": UserId(2), "feature2": ["list", "of", "strings"]},
            2: {"feature1": UserId(3), "feature2": ["string"]},
        },
    )

    h = nx.Graph()

    @validate
    def process(data: Graph[NodeData["feature1":UserId, "feature2" : List[str]]]):
        pass

    process(g)

    with pytest.raises(TypeError):
        process(h)


@pytest.mark.skip(reason="Not yet implemented")
def test_nested():
    NName = NodeData["id":int, "name":object]
    NLocation = NodeData["id":int, "longitude":float, "latitude":float]

    NNameLoc = Graph[NName, NLocation]

    assert NNameLoc.node_columns == {"id", "name", "longitude", "latitude"}
    assert NNameLoc.node_dtypes == {
        "id": int,
        "name": object,
        "longitude": float,
        "latitude": float,
    }
    assert NNameLoc.node_only_specified == True

    NNameLocEtc = Graph[NodeData[NNameLoc, "description":object, ...]]
    assert NNameLocEtc.node_columns == {
        "id",
        "name",
        "longitude",
        "latitude",
        "description",
    }
    assert NNameLocEtc.node_dtypes == {
        "id": int,
        "name": object,
        "longitude": float,
        "latitude": float,
        "description": object,
    }
    assert NNameLocEtc.node_only_specified == False


def test_init():
    with pytest.raises(TypeError):
        Graph()
