from metaflow import card, current, FlowSpec, step, Parameter
from metaflow.cards import (
    Markdown,
    Image,
    Table,
    MetaflowCardComponent,
    VegaChart,
    ProgressBar,
)
import os
import time
import re
import math
import random
from datetime import datetime
import requests
from card_testing_scenarios import (
    table_and_images_test,
    charting_tests,
    progress_bar_tests,
    multi_card_markdown_test,
    frequent_refresh_test
)


class RealtimeCardFlow(FlowSpec):
    sleep_cycles = Parameter("sleep-cycles", default=20)

    @card
    @step
    def start(self):
        self.iter_values = list(range(2))
        self.next(self.component_card)

    @card(type="blank", id="card2", refresh_interval=2)
    @card(type="default", id="card1",save_errors=False, refresh_interval=2)
    @step
    def component_card(self):
        multi_card_markdown_test(sleep_cycles=30)
        self.next(self.timeout_race_condition)
    
    @card(type="refresh_timeout_card", options={"timeout": 10}, timeout=30, save_errors=False)
    @step
    def timeout_race_condition(self):
        """
        - There is a case where we could have a async process and another non async process run in parallel. 
        - This is something we are not okay with because the async one (render_runtime) can override the values of the sync process (render). 
        - When we call the final render+refresh, we will wait for any async process to finish complete execution and ensure that both methods/processes complete execution.
        - This test and it's associated card will try to validate this case. 
        """
        current.card.refresh({"value": 0})
        time.sleep(3)
        # Sleep for 3 seconds (a time which is smaller than the time the card takes to render in the async process)
        # In this case, the main render should wait for the async render to finish, and then render the card
        self.next(self.timeout_card_test)
    
    @card(type="test_timeout_card", options={"timeout": 20}, timeout=2)
    @step
    def timeout_card_test(self):
        self.next(self.frequent_refresh_test)

    @card(type="blank", refresh_interval=2)
    @step
    def frequent_refresh_test(self):
        frequent_refresh_test(sleep_cycles=self.sleep_cycles)
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

    @card(type="vega", save_errors=False)
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
