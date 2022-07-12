# graphtype

Type hinting for networkx Graphs

## Installation

```python
pip install graphtype
```

## Usage

There are two parts in graphtype: the type-hinting part, and the validation. You can use type-hinting with the provided class to indicate attributes graphs should possess, and the validation decorator to additionally ensure the format is respected in every function call.

### Type-Hinting `Graph`

```python
from graphtype import Graph

def do_something_to_graph(g: Graph)
    pass
```

### Type-Hinting Graph Attributes `GraphData`

```python
from graphtype import Graph, GraphData


def do_something_to_graph(g: Graph[GraphData["name"]])
    pass

# Each node must have a "name" attribute

def do_something_to_graph(g: Graph[GraphData["name": str]])
    pass

# type(g.graph["name"]) == str must be True
```

### Type-Hinting Graph Attributes `NodeData`

```python
from graphtype import Graph, NodeData

def do_something_to_graph(g: Graph[NodeData["feature"]])
    pass

# Each node must have a "feature" attribute

def do_something_to_graph(g: Graph[NodeData["feature": np.ndarray]])
    pass

# for n, d in g.nodes(data=True):
#   type(d["feature"]) == np.ndarray must be True
```

### Type-Hinting Graph Attributes `NodeData`

```python
from graphtype import Graph, EdgeData

def do_something_to_graph(g: Graph[EdgeData["feature"]])
    pass

# Each edge must have a "feature" attribute

def do_something_to_graph(g: Graph[EdgeData["feature": pd.DataFrame]])
    pass

# for u, v, d in g.edges(data=True):
#   type(d["feature"]) == pd.DataFrame must be True
```

## Enforcing: `@validate`

The `@validate` decorator ensures that input `Graphs` have the right format when the function is called, otherwise raises `TypeError`.

```python
@validate
def func(g: Graph[NodeData["feature1": pd.DataFrame, "feature2": int],
                  EdgeData["length": float, "counts": np.ndarray],
                  GraphData["name": str]],
         h: Graph[NodeData["feature1": pd.DataFrame, "feature2": int]],
         ):
    pass
```

This package is heavily inspired by [Dataenforce](https://github.com/CedricFR/dataenforce).
