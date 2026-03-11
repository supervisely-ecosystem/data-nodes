import inspect
import pkgutil

import numpy as np

from src.compute.Layer import Layer

if not hasattr(np, "sctypes"):
    np.sctypes = {
        "int": [np.int8, np.int16, np.int32, np.int64],
        "uint": [np.uint8, np.uint16, np.uint32, np.uint64],
        "float": [np.float16, np.float32, np.float64, np.longdouble],
        "complex": [np.complex64, np.complex128, np.clongdouble],
        "others": [np.bool_, np.object_, np.str_, np.bytes_, np.void],
        "datetime": [np.datetime64],
        "timedelta": [np.timedelta64],
    }

from src.compute.layers import data, processing, save


def register_layers(package, type):
    prefix = package.__name__ + "."
    registered_classes = set()

    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        module = __import__(modname, fromlist="dummy")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Layer) and obj != Layer:
                if obj not in registered_classes:
                    Layer.register_layer(obj, type)
                    registered_classes.add(obj)


register_layers(data, "data")
register_layers(processing, "processing")
register_layers(save, "save")
