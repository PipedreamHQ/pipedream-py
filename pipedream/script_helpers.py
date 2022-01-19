"""Helpers for the pipedream scripting environment"""
import os
import json
import functools

try:
    with open(os.environ.get("PIPEDREAM_STEPS"), "r") as f:
        steps = json.load(f)
except:
    steps = None


def export(name, value):
    with open(os.environ.get("PIPEDREAM_EXPORTS"), "a") as f:
        f.write(name + ":json=" + json.dumps(value) + "\n")
