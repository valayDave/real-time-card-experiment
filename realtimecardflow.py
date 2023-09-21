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
        self.next(self.component_card)

    @card(type="default", id="card1")
    @step
    def component_card(self):
        # current.card['card1'].append(Markdown("## Initial Content In card"), id="markdown1")
        progress_bar = ProgressBar(100, label="progress1")

        progress_bar.update(10)
        current.card['card1'].append(progress_bar, id="progress1")
        
        current.card['card1'].append(
            Table([[1,2,3], [4,5,6]], headers=["a", "b", "c"])
        )
        n = 100
        print("Starting to measure progress...")
        for i in range(n):
            # current.card['card1'].components['markdown1'].update(f"## Content updated {i*10}/{n*10} markdown1")
            current.card["card1"].components["progress1"].update(i)
            current.card['card1'].refresh()
            time.sleep(1)
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
