import os
import json
from metaflow.cards import MetaflowCard
from metaflow.plugins.cards.card_modules import chevron as pt

ABS_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ABS_DIR_PATH, "base.html")


class ComponentBasedCard(MetaflowCard):
    ALLOW_USER_COMPONENTS = True
    RUNTIME_UPDATABLE = True

    RELOAD_POLICY = MetaflowCard.RELOAD_POLICY_ONCHANGE

    type = "component_card"

    def __init__(self, options={}, components=[], graph=None):
        self._components = components

    def render(self, task):
        with open(TEMPLATE_PATH) as f:
            return pt.render(
                f.read(),
                {
                    "COMPONENT_DATA": json.dumps(self._components),
                    "title": "JSON Viewer Card (Final) %s" % task.pathspec,
                },
            )

    def render_runtime(self, task, data):
        import json

        with open(TEMPLATE_PATH) as f:
            return pt.render(
                f.read(),
                {
                    "COMPONENT_DATA": json.dumps(self._components),
                    "title": "JSON Viewer Card (in-progress) %s" % task.pathspec,
                },
            )

    # The refresh method will get called
    # in the card CLI when there are data updates
    # So this method needs to return the data that will
    # get stored for the data updates
    def refresh(self, task, data):
        return data["components"]

    def reload_content_token(self, task, data):
        if task.finished:
            return "final"
        else:
            return "runtime"

class RefershTimeoutCard(MetaflowCard):
    type = "refresh_timeout_card"

    ALLOW_USER_COMPONENTS = True

    RUNTIME_UPDATABLE = True

    RELOAD_POLICY = MetaflowCard.RELOAD_POLICY_ONCHANGE

    def __init__(self, options={"timeout": 50}, **kwargs):
        super().__init__()
        self._timeout = 10
        if "timeout" in options:
            self._timeout = options["timeout"]
    
    def refresh(self, task, data):
        return data["user"]

    def reload_content_token(self, task, data):
        if task.finished:
            return "final"
        else:
            return "runtime"
    
    def save_file(self, data, fn):
        import os
        with open(os.path.join(ABS_DIR_PATH,fn), 'w') as f:
            f.write(data)
        
    def render_runtime(self, task, data):
        import time
        time.sleep(self._timeout)
        self.save_file("%s At Render Runtime" % task.pathspec, "runtime.txt")
        return "%s At Render Runtime" % task.pathspec

    def render(self, task):
        import time
        time.sleep(self._timeout)
        self.save_file("%s At Task Complete" % task.pathspec, "result.txt")
        return "%s At Task Complete" % task.pathspec


CARDS = [ComponentBasedCard, RefershTimeoutCard]
