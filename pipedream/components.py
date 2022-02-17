import abc
import time
import datetime
import traceback
from collections import OrderedDict


class Context:
    def __init__(self):
        self._observations = []

    def _add_observation(self, observation):
        observation["ts"] = int(round(time.time() * 1000))
        self._observations.append(observation)

    def emit(self, event, eventName=""):
        self._add_observation({
            "k": "emit",
            "en": eventName,
            "e": event})


class PropInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'set_runtime_data') and
                callable(subclass.set_runtime_data) and
                hasattr(subclass, 'to_configurable_prop') and
                callable(subclass.to_configurable_prop) and
                NotImplemented)

    @abc.abstractmethod
    def set_runtime_data(self, property_name, context, prop):
        """provide runtime data to prop"""
        raise NotImplementedError

    @abc.abstractmethod
    def to_configurable_prop(self, name, type_):
        """convert to configurable prop spec"""
        return {"name": name, "type": type_}


class Component:
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance._props = OrderedDict()
        return instance

    def __setattr__(self, key, value):
        if key != '_props' and isinstance(value, PropInterface):
            self._props[key] = value
        object.__setattr__(self, key, value)


class Db(PropInterface):
    def set_runtime_data(self, property_name, context, prop):
        self.__context = context
        self.__db = prop["$db"]
        self.__property_name = property_name

    def to_configurable_prop(self, name):
        return super().to_configurable_prop(name, "$.service.db")

    def get(self, key):
        retval = self.__db.get(key)
        self.__context._add_observation({
            "k": "db.get",
            "pn": self.__property_name,
            "key": key,
            "ret": retval
        })
        return retval

    def set(self, key, val):
        self.__context._add_observation({
            "k": "db.set",
            "pn": self.__property_name,
            "key": key,
            "val": val
        })
        self.__db[key] = val


class StringProp(PropInterface):
    def __init__(self, **kwargs):
        self._options = kwargs.get("options")

    # The prop will get replaced by it's value directly, so no implementation
    def set_runtime_data(self, property_name, context, prop):
        pass

    def to_configurable_prop(self, name):
        prop = super().to_configurable_prop(name, "string")
        if callable(self._options):
            prop['remoteOptions'] = True
        elif isinstance(self._options, list):
            prop['options'] = self._options
        return prop

    def options(self, component):
        return self._options(component)


class Http(PropInterface):
    def set_runtime_data(self, property_name, context, prop):
        self.endpoint = prop["endpoint"]
        self.__context = context

    def to_configurable_prop(self, name):
        return super().to_configurable_prop(name, "$.interface.http")

    def respond(self, config):
        self.__context._add_observation({
            "k": "http.respond",
            "config": config
        })

# XXX: Maybe should expose it's schedule?


class Timer(PropInterface):
    def __init__(self, **kwargs):
        self._cron = kwargs.get("cron")
        self._interval_seconds = kwargs.get("interval_seconds")

    def set_runtime_data(self, property_name, context, prop):
        pass

    def to_configurable_prop(self, name):
        return {**super().to_configurable_prop(name, "$.interface.timer"),
                "cron": self._cron,
                "intervalSeconds": self._interval_seconds
                }


def serialize_exception(e, cellId=None):
    rv = {
        "code": type(e).__name__,
        "message": str(e),
        "stack": traceback.format_tb(e.__traceback__),
        "ts": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
        "cellId": cellId
    }
    try:
        rv["output"] = e.output.decode("utf-8")
    except AttributeError:
        pass
    return rv
