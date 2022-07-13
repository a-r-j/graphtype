"""Modified from dataenforce: https://github.com/CedricFR/dataenforce"""

import inspect
from functools import wraps
from typing import Generic, NewType, _tp_cache, _TypingEmpty, get_type_hints

import networkx as nx
import numpy as np

try:
    from typing import GenericMeta  # Python 3.6
except ImportError:  # Python 3.7

    class GenericMeta(type):
        pass


def validate(f):
    signature = inspect.signature(f)
    hints = get_type_hints(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        for argument_name, value in bound.arguments.items():
            hint = hints[argument_name]
            if argument_name in hints and isinstance(hint, DatasetMeta):

                if not isinstance(value, nx.Graph):
                    raise TypeError(f"{value} is not a nx.Graph")

                if hint.graph:
                    columns = value.graph
                    if (
                        hint.graph_only_specified
                        and columns.keys() != hint.graph_columns
                    ):
                        raise TypeError(
                            f"{argument_name} graph attributes do not match required set {hint.graph_columns}"
                        )

                    if (
                        not hint.graph_only_specified
                        and not hint.graph_columns.issubset(columns)
                    ):
                        raise TypeError(
                            f"{argument_name} is missing some graph attributes from {hint.graph_columns}"
                        )
                    if hint.graph_dtypes:
                        dtypes = {k: type(v) for k, v in value.graph.items()}
                        for colname, dt in hint.graph_dtypes.items():
                            if not np.issubdtype(dtypes[colname], np.dtype(dt)):
                                raise TypeError(
                                    f"{dtypes[colname]} is not a subtype of {dt} for graph attribute {colname}"
                                )
                if hint.node:
                    for n, d in value.nodes(data=True):
                        if hint.node_only_specified and d.keys() != hint.node_columns:
                            raise TypeError(
                                f"{argument_name} node attributes do not match required set {hint.node_columns} on node {n}"
                            )

                        if not hint.node_only_specified and not hint.columns.issubset(
                            d
                        ):
                            raise TypeError(
                                f"{argument_name} is missing some node attributes from {hint.node_columns} on node {n}"
                            )
                        if hint.node_dtypes:
                            dtypes = {k: type(v) for k, v in d.items()}
                            for colname, dt in hint.node_dtypes.items():
                                if not np.issubdtype(dtypes[colname], np.dtype(dt)):
                                    raise TypeError(
                                        f"{dtypes[colname]} is not a subtype of {dt} for node attribute {colname} on node {n}"
                                    )
                    if len(value.nodes) == 0:
                        raise TypeError(f"Graph {argument_name} has no nodes")

                if hint.edge:
                    for u, v, d in value.edges(data=True):
                        if hint.edge_only_specified and d.keys() != hint.edge_columns:
                            raise TypeError(
                                f"{argument_name} edge atributes do not match required set {hint.edge_columns} on edge {u}-{v}"
                            )

                        if (
                            not hint.edge_only_specified
                            and not hint.edge_columns.issubset(d)
                        ):
                            raise TypeError(
                                f"{argument_name} is missing some edge attributes from {hint.edge_columns} on edge {u}-{v}"
                            )
                        if hint.edge_dtypes:
                            dtypes = {k: type(v) for k, v in d.items()}
                            for colname, dt in hint.edge_dtypes.items():
                                if not np.issubdtype(dtypes[colname], np.dtype(dt)):
                                    raise TypeError(
                                        f"{dtypes[colname]} is not a subtype of {dt} for edge attribute {colname} on edge {u}-{v}"
                                    )
                    if len(value.edges) == 0:
                        raise TypeError(f"Graph {argument_name} has no edges.")
        return f(*args, **kwargs)

    return wrapper


def _resolve_type(t):
    """Adapted from dataenforce contib by @martijnentink:
    https://github.com/CedricFR/dataenforce/pull/5"""
    # support for NewType in type hinting
    if hasattr(t, "__supertype__"):
        return _resolve_type(t.__supertype__)
    # support for typing.List and typing.Dict
    if hasattr(t, "__origin__"):
        return _resolve_type(t.__origin__)
    return t


def _get_columns_dtypes(p):
    columns = set()
    dtypes = {}
    if isinstance(p, str):
        columns.add(p)
    elif isinstance(p, slice):
        columns.add(p.start)
        stop_type = _resolve_type(p.stop)
        if not inspect.isclass(stop_type):
            raise TypeError(
                f"Column type hints must be classes, error with {repr(stop_type)}"
            )
        dtypes[p.start] = stop_type
    elif isinstance(p, (list, set)):
        for el in p:
            subcolumns, subdtypes = _get_columns_dtypes(el)
            columns |= subcolumns
            dtypes.update(subdtypes)
    elif isinstance(p, DataMeta):
        columns |= _get_columns_dtypes(p)[0]
        dtypes.update(_get_columns_dtypes(p)[1])
    else:
        raise TypeError(
            "Dataset[col1, col2, ...]: each col must be a string, list or set."
        )
    return columns, dtypes


class DatasetMeta(GenericMeta):
    """Metaclass for Dataset (internal)."""

    def __new__(metacls, name, bases, namespace, **kargs):
        return super().__new__(metacls, name, bases, namespace)

    @_tp_cache
    def __getitem__(self, parameters):
        if hasattr(self, "__origin__") and (
            self.__origin__ is not None or self._gorg is not Graph
        ):
            return super().__getitem__(parameters)
        if parameters == ():
            return super().__getitem__((_TypingEmpty,))

        meta = DatasetMeta(self.__name__, self.__bases__, {})

        meta.graph = False
        meta.node = False
        meta.edge = False

        if isinstance(parameters, DataMeta):
            parameters = [parameters]
        for p in parameters:
            if p.name == "graph":
                meta.graph_columns = p.columns
                meta.graph_dtypes = p.dtypes
                meta.graph_only_specified = p.only_specified
                meta.graph = True
            elif p.name == "node":
                meta.node_columns = p.columns
                meta.node_dtypes = p.dtypes
                meta.node_only_specified = p.only_specified
                meta.node = True
            elif p.name == "edge":
                meta.edge_columns = p.columns
                meta.edge_dtypes = p.dtypes
                meta.edge_only_specified = p.only_specified
                meta.edge = True
        return meta


class DataMeta(GenericMeta):
    def __new__(metacls, name, bases, namespace, **kargs):
        return super().__new__(metacls, name, bases, namespace)

    @_tp_cache
    def __getitem__(self, parameters):
        if hasattr(self, "__origin__") and (
            self.__origin__ is not None
            or self._gorg is not (NodeData or EdgeData or GraphData)
        ):
            return super().__getitem__(parameters)
        if parameters == ():
            return super().__getitem__((_TypingEmpty,))

        if not isinstance(parameters, tuple):
            parameters = (parameters,)
        parameters = list(parameters)

        only_specified = True
        if parameters[-1] is ...:
            only_specified = False
            parameters.pop()

        columns, dtypes = _get_columns_dtypes(parameters)
        meta = DataMeta(self.__name__, self.__bases__, {})
        meta.name = self.name
        meta.only_specified = only_specified
        meta.columns = columns
        meta.dtypes = dtypes
        return meta


class Graph(nx.Graph, extra=Generic, metaclass=DatasetMeta):
    """Defines type Dataset to serve as column name & type enforcement for nx.Graph."""

    __slots__ = ()
    graph = False
    node = False
    edge = False

    def __new__(cls, *args, **kwds):
        if not hasattr(cls, "_gorg") or cls._gorg is Graph:
            raise TypeError(
                "Type Dataset cannot be instantiated; " "use nx.Graph() instead"
            )
        return _generic_new(nx.Graph, cls, *args, **kwds)


class NodeData(dict, extra=Generic, metaclass=DataMeta):
    """Defines type Dataset to serve as column name & type enforcement for nx.Graph."""

    __slots__ = ()
    name = "node"

    def __new__(cls, *args, **kwds):
        if not hasattr(cls, "_gorg") or cls._gorg is NodeData:
            raise TypeError(
                "Type Dataset cannot be instantiated; " "use nx.Graph() instead"
            )
        return _generic_new(dict, cls, *args, **kwds)


class GraphData(dict, extra=Generic, metaclass=DataMeta):
    """Defines type Dataset to serve as column name & type enforcement for nx.Graph."""

    __slots__ = ()
    name = "graph"

    def __new__(cls, *args, **kwds):
        if not hasattr(cls, "_gorg") or cls._gorg is GraphData:
            raise TypeError(
                "Type Dataset cannot be instantiated; " "use nx.Graph() instead"
            )
        return _generic_new(dict, cls, *args, **kwds)


class EdgeData(dict, extra=Generic, metaclass=DataMeta):
    """Defines type Dataset to serve as column name & type enforcement for nx.Graph."""

    __slots__ = ()
    name = "edge"

    def __new__(cls, *args, **kwds):
        if not hasattr(cls, "_gorg") or cls._gorg is EdgeData:
            raise TypeError(
                "Type Dataset cannot be instantiated; " "use nx.Graph() instead"
            )
        return _generic_new(dict, cls, *args, **kwds)
