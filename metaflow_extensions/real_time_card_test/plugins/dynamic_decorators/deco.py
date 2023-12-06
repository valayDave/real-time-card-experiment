import os
import sys
from metaflow.decorators import StepDecorator
from metaflow.exception import MetaflowException
from metaflow.graph import DAGNode
import uuid


class DynamicCardDecorator(StepDecorator):
    name = "dynamic_card"

    allow_multiple = True

    defaults = {"id": None}

    ID_PREFIX = "my_card_"

    _first_time_init = {}

    @classmethod
    def _get_first_time_init(cls, step_name):
        return cls._first_time_init.get(step_name, None)

    @classmethod
    def _set_first_time_init(cls, step_name, value):
        cls._first_time_init[step_name] = value

    def _get_card_id(self):
        if self.attributes["id"] is None:
            return self._get_uuid()
        else:
            return self.ID_PREFIX + self.attributes["id"]

    def _get_uuid(self):
        return self.ID_PREFIX + (str(uuid.uuid4()).replace("-", "")[:5])

    def _card_decorators_already_attached(self, step):
        already_attached_decorators = []
        for decorator in step.decorators:
            if decorator.name == "card":
                if self.ID_PREFIX in decorator.attributes["id"]:
                    already_attached_decorators.append(decorator.attributes["id"])

        return already_attached_decorators

    def _get_step(self, flow, step_name):
        for step in flow:
            if step.name == step_name:
                return step
        return None

    def _first_time_init_check(self, step_dag_node):
        """
        This is where you can have some custom logic that specifies
        how you want to check if the decorator was attached from a "parent decorator".
        In the below case, we are using the card_id to check if the decorator was already attached.
        If the card-id has been created with a special prefix, then we know that the decorator was already attached.
        """
        return len(self._card_decorators_already_attached(step_dag_node)) == 0

    def step_init(
        self, flow, graph, step_name, decorators, environment, flow_datastore, logger
    ):
        """
        This `step_init` function is an example to show how users can dynamically add card decorators to steps.
        In this example we piggyback on where `step_init` is called in the lifecycle and the core logic
        tries to ensure that the dynamcially added decorators are added only once.

        `step_init` is executed multiple times in the lifecycle, specifically:
        1. When the flow is being deployed. (eg. `python myflow.py argo-workflows create` or `python myflow.py airflow create`)
        2. When the step is being executed. (eg. `python myflow.py run`)

        Since `step_init` is executed multiple times we need to ensure that the decorators are added only once.
        To prevent duplicating decorators, we implement some custom logic to check if the decorators
        have already been added. This logic is generally heuristic based since we currently don't have any
        liniage of where decorators actually ended up being added from.

        This logic helps avoid multiple additions during the 'step_init' calls,
        which can happen both during deployment and step execution. The logic is also
        developed to handle the case where `allow_multiple` is set to true for a decorator.
        """

        from metaflow import decorators as _decorators

        step_dag_node = self._get_step(flow, step_name)
        if self._get_first_time_init(step_name) is None:
            if self._first_time_init_check(step_dag_node):
                self._set_first_time_init(step_name, True)
                _decorators._attach_decorators_to_step(
                    step_dag_node, ["card:type=default,id=%s" % self._get_card_id()]
                )
            else:
                self._set_first_time_init(step_name, False)
        elif self._get_first_time_init(step_name) == True:
            _decorators._attach_decorators_to_step(
                step_dag_node, ["card:type=default,id=%s" % self._get_card_id()]
            )
