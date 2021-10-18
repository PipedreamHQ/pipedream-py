"""Helpers for the pipedream scripting environment"""
import os
import json
import functools


def export(name, value):
    with open(os.environ.get("PIPEDREAM_EXPORTS"), "a") as f:
        f.write(name + ":json=" + json.dumps(value))


@functools.lru_cache
def steps():
    return json.loads(os.environ.get("PIPEDREAM_STEPS"))
