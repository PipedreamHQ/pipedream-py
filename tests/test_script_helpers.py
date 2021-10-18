# autopep8: off
# this needs to go before importing script_helpers
import os
os.environ["PIPEDREAM_STEPS"] = '{"foo": true}'

from pipedreamhq.script_helpers import (steps, export, reload_steps)
# autopep8: on


def test_steps():
    assert steps == {"foo": True}
