"""Helpers for the pipedream scripting environment"""
import os
import json
import functools

steps = json.loads(os.environ.get("PIPEDREAM_STEPS", "null"))


def export(name, value):
    with open(os.environ.get("PIPEDREAM_EXPORTS"), "a") as f:
        f.write(name + ":json=" + json.dumps(value) + "\n")
