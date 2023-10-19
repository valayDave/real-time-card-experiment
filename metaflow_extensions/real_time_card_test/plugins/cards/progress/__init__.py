import os
import json
from metaflow.cards import MetaflowCard


ABS_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ABS_DIR_PATH, "base.html")


class ProgressCard(MetaflowCard):

    ALLOW_USER_COMPONENTS = True
    RUNTIME_UPDATABLE = True
    RELOAD_POLICY = MetaflowCard.RELOAD_POLICY_NEVER

    type = "progress"

    def render(self, task):
        with open(TEMPLATE_PATH) as f:
            txt = f.read().replace("TITLE", "Progress (final) %s" % task.pathspec)
            return txt.replace("PROGRESS", "100")

    def render_runtime(self, task, data):
        with open(TEMPLATE_PATH) as f:
            txt = f.read().replace("TITLE", "Progress (runtime) %s" % task.pathspec)
            txt = txt.replace("DISABLE", "")
            return txt.replace("PROGRESS", str(data['user']['value']))

    def refresh(self, task, data):
        return data['user']

CARDS = [ProgressCard]
