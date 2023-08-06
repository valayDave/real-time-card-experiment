from metaflow import card, current, FlowSpec, step
import os
import time
import math
import random
from datetime import datetime

class RealtimeCardFlow(FlowSpec):

    @card
    @step
    def start(self):
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
