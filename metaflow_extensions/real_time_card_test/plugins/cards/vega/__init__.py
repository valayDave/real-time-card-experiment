import os
import json
from metaflow.cards import MetaflowCard


ABS_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ABS_DIR_PATH, "base.html")


class VegaCard(MetaflowCard):
    ALLOW_USER_COMPONENTS = True
    RUNTIME_UPDATABLE = True

    type = "vega"

    def render(self, task, data):
        with open(TEMPLATE_PATH) as f:
            txt = f.read().replace("TITLE", "Charting (final) %s" % task.pathspec)
            return txt.replace("INITIAL_DATA", json.dumps(data.get("user", {})))

    def render_runtime(self, task, data):
        with open(TEMPLATE_PATH) as f:
            txt = f.read().replace("TITLE", "Charting (runtime) %s" % task.pathspec)
            txt = txt.replace("DISABLE", "")
            return txt.replace("INITIAL_DATA", json.dumps(data.get("user", {})))

    def refresh(self, task, data):
        return data["user"]


class TimeoutCard(MetaflowCard):
    RUNTIME_UPDATABLE = True
    type = "timeout"

    def render_runtime(self, task, data):
        import time

        time.sleep(60)
        return "<h1>Timeout Card In Runtime<h1>"

    def render(self, task, data):
        import time

        time.sleep(60)
        return "<h1>Timeout Card<h1>"


CARDS = [VegaCard, TimeoutCard]
