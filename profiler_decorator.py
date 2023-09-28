from metaflow.cards import Markdown, Table
from metaflow.plugins.cards.card_modules.basic import DefaultComponent
from functools import wraps
import threading
import multiprocessing
from datetime import datetime
from metaflow import current
import time


class LineChartComponent(DefaultComponent):
    type = "lineChart"

    REALTIME_UPDATABLE = True

    def __init__(
        self,
        data=None,
        labels=None,
        max_size=None,
        x_axis_title=None,
        y_axis_title=None,
    ):
        super().__init__(title=None, subtitle=None)
        self.data = data or []
        self.labels = labels or []
        self.max_size = max_size
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title

    def update(self, data=None, labels=None, **kwargs):
        if data is not None:
            self.data.append(data)
            if self.max_size is not None:
                self.data = self.data[-self.max_size :]
        if labels is not None:
            self.labels.append(labels)
            if self.max_size is not None:
                self.labels = self.labels[-self.max_size :]

    def render(self):
        datadict = super().render()
        config = {
            "type": "line",
            "data": {
                "labels": [],
                "datasets": [
                    {
                        "backgroundColor": "#FF6384",
                        "borderColor": "#FF6384",
                        "data": [],
                    }
                ],
            },
            "options": {
                "plugins": {                
                    "legend": {
                        "display": False
                    }
                }
            },
        }
        
        def _check_and_add_title(title, key):
            if title is None:
                return
            if "scales" not in config["options"]:
                config["options"]["scales"] = {}
            
            config["options"]["scales"][key] = {
                "title": {
                    "display": True,
                    "text": title,
                }
            }

        _check_and_add_title(self.x_axis_title, "x",)
        _check_and_add_title(self.y_axis_title, "y",)
        datadict.update({"data": self.data, "labels": self.labels, "config": config})
        if self.id is not None:
            datadict["id"] = self.id
        return datadict


class Profiler:
    def __init__(self, filename, interval):
        self.filename = filename
        self.interval = interval
        self.latest_reading = Markdown("*Initializing profiler...*")
        self.charts = {
            "cpu_chart": LineChartComponent(max_size=100, y_axis_title="CPU Usage", x_axis_title="Time"),
            "memory_chart": LineChartComponent(max_size=100, y_axis_title="Memory Usage", x_axis_title="Time"),
            "disk_chart": LineChartComponent(max_size=100, y_axis_title="Disk Usage", x_axis_title="Time"),
            "process_chart": LineChartComponent(max_size=100, y_axis_title="Number of Running Processes", x_axis_title="Time"),
            "load_chart": LineChartComponent(max_size=100, y_axis_title="Load Average", x_axis_title="Time"),
            "uptime_chart": LineChartComponent(max_size=100, y_axis_title="System Uptime", x_axis_title="Time"),
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
                data=data["CPU Usage"], labels=current_timestamp
            )
            self.charts["memory_chart"].update(
                data=data["Memory Usage"], labels=current_timestamp
            )
            self.charts["disk_chart"].update(
                data=data["Disk Usage"], labels=current_timestamp
            )
            self.charts["process_chart"].update(
                data=data["Number of Running Processes"], labels=current_timestamp
            )
            self.charts["load_chart"].update(
                data=data["Load Average"][0], labels=current_timestamp
            )
            self.charts["uptime_chart"].update(
                data=data["System Uptime"], labels=current_timestamp
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
                    Markdown("## %s Chart" % chart.y_axis_title)
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

            return card(type="blank", id="system_profile")(func)
        else:
            return func
