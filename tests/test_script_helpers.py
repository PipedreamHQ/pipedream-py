from pipedreamhq.script_helpers import (steps, export)
import os


def test_steps():
    os.environ["PIPEDREAM_STEPS"] = '{"foo": true}'
    assert steps() == {"foo": True}
