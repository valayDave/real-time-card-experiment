from metaflow import card, current, FlowSpec, step, Parameter
from metaflow.cards import Markdown, Image, Table, MetaflowCardComponent, VegaChart, ProgressBar
import os
import time
import re
import math
import random
from datetime import datetime
import requests
from card_testing_scenarios import table_and_images_test, charting_tests, progress_bar_tests, multi_card_markdown_test

class RealtimeCardFlow(FlowSpec):

    sleep_cycles = Parameter('sleep-cycles', default=20)

    @card
    @step
    def start(self):
        self.iter_values = list(range(2))
        self.next(self.image_table_tests)
    
    @card(type="blank")
    @step
    def image_table_tests(self):
        table_and_images_test(sleep_cycles=self.sleep_cycles)
        self.next(self.pre_native_chart)

    @card(type="blank")
    @step
    def pre_native_chart(self):
        charting_tests(sleep_cycles=self.sleep_cycles)
        self.next(self.native_progressbar)

    @card(type="blank")
    @step
    def native_progressbar(self):
        progress_bar_tests(sleep_cycles=self.sleep_cycles)
        self.next(self.component_card, foreach="iter_values")

    @card(type="blank", id="card2")
    @card(type="default", id="card1")
    @step
    def component_card(self):
        multi_card_markdown_test(sleep_cycles=self.sleep_cycles)
        self.next(self.join)

    @step
    def join(self, inputs):
        print("Joining")
        self.next(self.progress_bar)

    @card(type="progress")
    @step
    def progress_bar(self):
        n = self.sleep_cycles
        print("Starting to measure progress...")
        for i in range(n):
            current.card.refresh({"value": i})
            print(f"iteration {i}/{n}")
            time.sleep(1)
        self.next(self.chart)

    @card(type="vega")
    @step
    def chart(self):
        values = []
        n = self.sleep_cycles
        print("Starting to chart...")
        for i in range(n):
            val = math.sin(i * 0.1) + random.random() * 0.1 - 0.05
            values.append({"time": datetime.now().isoformat(), "val": val})
            current.card.refresh({"values": values})
            print(f"iteration {i}/{n} val {val}")
            time.sleep(1)
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    RealtimeCardFlow()
