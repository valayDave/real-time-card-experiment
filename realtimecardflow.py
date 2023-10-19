from metaflow import card, current, FlowSpec, step
from metaflow.cards import Markdown, Image, Table, MetaflowCardComponent
import os
import time
import math
import random
from datetime import datetime

class ProgressBar(MetaflowCardComponent):
    type = "progressBar"

    REALTIME_UPDATABLE = True

    def __init__(
        self, max, label=None, value=0, unit=None
    ):
        self._label = label
        self._max = max
        self._value = value
        self._unit = unit

    def update(self, new_value):
        self._value = new_value

    def render(self):
        data = {
            "type": self.type,
            "id": self.id,
            "max": self._max,
            "value": self._value,
        }
        if self._label:
            data["label"] = self._label
        if self._unit:
            data["unit"] = self._unit
        return data


class RealtimeCardFlow(FlowSpec):

    @card
    @step
    def start(self):
        self.iter_values = list(range(10))
        self.next(self.component_card, foreach="iter_values")

    @card(type="blank", id="card2")
    @card(type="default", id="card1")
    @step
    def component_card(self):
        card_map = current.card
        import uuid
        current_id = uuid.uuid4().hex
        
        current.card['card1'].append(Markdown("## [%s] Initial Content In card" % current_id), id="markdown1")
        current.card['card1'].append(
            Table([[1,2,3], [4,5,6]], headers=["a", "b", "c"])
        )
        n = 500
        for i in range(n):
            current.card['card1'].components['markdown1'].update(
                f"## [{current_id}] Content updated {i*10}/{n*10} markdown1"
            )
            current.card['card1'].refresh()
            time.sleep(1)
        self.next(self.join)
    
    @step
    def join(self, inputs):
        print("Joining")
        self.next(self.progress_bar)

    @card(type="progress")
    @step
    def progress_bar(self):
        n = 100
        print("Starting to measure progress...")
        for i in range(n):
            current.card.refresh({'value': i})
            print(f"iteration {i}/{n}")
            time.sleep(1)
        self.next(self.chart)

    @card(type="vega")
    @step
    def chart(self):
        values = []
        n = 100
        print("Starting to chart...")
        for i in range(n):
            val =  math.sin(i * 0.1) + random.random() * 0.1 - 0.05
            values.append({'time': datetime.now().isoformat(), 'val': val})
            current.card.refresh({'values': values})
            print(f"iteration {i}/{n} val {val}")
            time.sleep(1)
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    RealtimeCardFlow()
