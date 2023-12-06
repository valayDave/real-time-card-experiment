from metaflow.cards import Markdown, Table
from metaflow.plugins.cards.card_modules.basic import DefaultComponent
from functools import wraps
import threading
import multiprocessing
from datetime import datetime
from metaflow import current
import time

class Profiler:
    def __init__(self, filename, interval):
        from nn_card import LineChart
        self.filename = filename
        self.interval = interval
        self.latest_reading = Markdown("*Initializing profiler...*")
        self.charts = {
            "cpu_chart": LineChart(
                title="CPU Utilization",
                xtitle="Time",
                ytitle="CPU Usage",
                x_name="time",
                y_name="cpu",
                width=600,
                height=400,
                x_axis_temporal=True,
            ),
            "memory_chart": LineChart(
                ytitle="Memory Usage",
                xtitle="Time",
                x_name="time",
                y_name="memory",
                title="Memory Utilization",
                width=600,
                height=400,
                x_axis_temporal=True,
            ),
            "disk_chart": LineChart(
                ytitle="Disk Usage",
                xtitle="Time",
                x_name="time",
                y_name="disk",
                title="Disk Utilization",
                width=600,
                height=400,
                x_axis_temporal=True,
            ),
            "process_chart": LineChart(
                ytitle="Number of Running Processes",
                xtitle="Time",
                x_name="time",
                y_name="process",
                title="Number of Running Processes",
                width=600,
                height=400,
                x_axis_temporal=True,
            ),
            "load_chart": LineChart(
                ytitle="Load Average",
                xtitle="Time",
                x_name="time",
                y_name="load",
                title="Load Average",    
                width=600,
                height=400,
                x_axis_temporal=True,

            ),
            "uptime_chart": LineChart(
                ytitle="System Uptime",
                xtitle="Time",
                x_name="time",
                y_name="uptime",
                title="System Uptime",
                width=600,
                height=400,
                x_axis_temporal=True,
            ),
        }

    def collect_data(self):
        import psutil
        import os
        import time
        import json

        while True:
            data = {
                "CPU Usage": psutil.cpu_percent(interval=1),
                "Memory Usage": psutil.virtual_memory().percent,
                "Disk Usage": psutil.disk_usage("/").percent,
                "Number of Running Processes": len(psutil.pids()),
                "Load Average": os.getloadavg(),
                "System Uptime": time.time() - psutil.boot_time(),
            }
            with open(self.filename, "w") as file:
                json.dump(data, file)
            time.sleep(self.interval)

    def _safely_read_file(self):
        import json

        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = None
        except json.decoder.JSONDecodeError:
            data = None
        return data

    def update_card(self):
        import json
        from metaflow.cards import Markdown

        while True:
            data = self._safely_read_file()
            if data is None:
                time.sleep(self.interval)
                continue
            table_data = "\n".join(
                f"| {key} | {value} |" for key, value in data.items()
            )
            table_md = f"| Metric | Value |\n| --- | --- |\n{table_data}"
            current.card["system_profile"].components["profiler_table"].update(table_md)
            current_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            self.latest_reading.update(
                "*Latest Reading on: %s*" % current_timestamp,
            )
            self.charts["cpu_chart"].update(
                dict(cpu=data["CPU Usage"], time=current_timestamp)
            )
            self.charts["memory_chart"].update(
                dict(memory=data["Memory Usage"], time=current_timestamp)
                # data=data["Memory Usage"], labels=current_timestamp
            )
            self.charts["disk_chart"].update(
                dict(disk=data["Disk Usage"], time=current_timestamp)
                # data=data["Disk Usage"], labels=current_timestamp
            )
            self.charts["process_chart"].update(
                dict(process=data["Number of Running Processes"], time=current_timestamp)
                # data=data["Number of Running Processes"], labels=current_timestamp
            )
            self.charts["load_chart"].update(
                dict(load=data["Load Average"][0], time=current_timestamp)
                # data=data["Load Average"][0], labels=current_timestamp
            )
            self.charts["uptime_chart"].update(
                dict(uptime=data["System Uptime"], time=current_timestamp)
                # data=data["System Uptime"], labels=current_timestamp
            )
            current.card["system_profile"].refresh()
            time.sleep(self.interval)


class profiler:
    def __init__(self, with_card=True, interval=0.5):
        self.with_card = with_card
        self.interval = interval

    def __call__(self, f):
        @wraps(f)
        def func(s):
            prof = Profiler("system_data.txt", interval=self.interval)
            sidecar_process = multiprocessing.Process(target=prof.collect_data)
            sidecar_process.start()
            current.card["system_profile"].append(
                Markdown("# Profiler Card for System Metrics (%s)" % current.pathspec)
            )
            current.card["system_profile"].append(
                prof.latest_reading,
            )
            current.card["system_profile"].append(
                Markdown("Initializing cpu profile..."), id="profiler_table"
            )
            for chart_id, chart in prof.charts.items():
                current.card["system_profile"].append(
                    Markdown("## %s Chart" % chart.spec["title"])
                )
                current.card["system_profile"].append(chart, id=chart_id)

            update_thread = threading.Thread(target=prof.update_card, daemon=True)
            update_thread.start()

            try:
                f(s)
            finally:
                sidecar_process.terminate()

        if self.with_card:
            from metaflow import card

            return card(type="blank", id="system_profile", refresh_interval=self.interval)(func)
        else:
            return func
