from metaflow import FlowSpec, step, card, current
from profiler_decorator import profiler
import time


class SystemProfileFlow(FlowSpec):
    @profiler(interval=1)
    @step
    def start(self):
        for i in range(200):
            print(i)
            time.sleep(0.5)
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    SystemProfileFlow()
