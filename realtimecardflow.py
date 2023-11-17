from metaflow import card, current, FlowSpec, step
from metaflow.cards import Markdown, Image, Table, MetaflowCardComponent, VegaChart, ProgressBar
import os
import time
import re
import math
import random
from datetime import datetime


def get_charts_in_a_table():
    from charts import line_chart_spec

    train_spec_epoch, train_data_epoch = line_chart_spec(
        title="Train Loss Per Epoch",
        xtitle="Epoch",
        ytitle="Loss",
        x_name="epoch",
        y_name="loss",
        width=300,
        height=200,
        with_params=False,
    )
    val_spec_epoch, val_data_epoch = line_chart_spec(
        title="Validation Loss Per Epoch",
        xtitle="Epoch",
        ytitle="Loss",
        x_name="epoch",
        y_name="loss",
        width=300,
        height=200,
        with_params=False,
    )
    train_spec_step, train_data_step = line_chart_spec(
        title="Train Loss Per Step",
        xtitle="Step",
        ytitle="Loss",
        x_name="step",
        y_name="loss",
        width=300,
        height=200,
        with_params=False,
    )
    val_spec_step, val_data_step = line_chart_spec(
        title="Validation Loss Per Step",
        xtitle="Step",
        ytitle="Loss",
        x_name="step",
        y_name="loss",
        width=300,
        height=200,
        with_params=False,
    )

    train_epoch_chart = VegaChart(train_spec_epoch, data=train_data_epoch)
    val_epoch_chart = VegaChart(val_spec_epoch, data=val_data_epoch)
    train_step_chart = VegaChart(train_spec_step, data=train_data_step)
    val_step_chart = VegaChart(val_spec_step, data=val_data_step)

    data_objects = (train_data_epoch, val_data_epoch, train_data_step, val_data_step)
    charts_objects = (
        train_epoch_chart,
        val_epoch_chart,
        train_step_chart,
        val_step_chart,
    )
    return (
        Table(
            [
                [
                    VegaChart(train_spec_epoch, data=train_data_epoch),
                    VegaChart(val_spec_epoch, data=val_data_epoch),
                ],
                [
                    VegaChart(train_spec_step, data=train_data_step),
                    VegaChart(val_spec_step, data=val_data_step),
                ],
            ],
            headers=["Train", "Validation"],
        ),
        data_objects,
        charts_objects,
    )

class RealtimeCardFlow(FlowSpec):
    @card
    @step
    def start(self):
        self.iter_values = list(range(10))
        self.next(self.pre_native_chart)

    @card(type="blank")
    @step
    def pre_native_chart(self):
        from charts import line_chart_spec, update_data_object, get_charts

        # Create the Chart
        import random

        charts_table, data_objects, chart_objects = get_charts_in_a_table()
        spec, data_object = line_chart_spec()
        chart_from_spec = VegaChart(spec, data=data_object)
        current.card.append(Markdown("# Charts In A Table"))
        current.card.append(charts_table)
        current.card.append(Markdown("# Vanilla Vega Spec Chart"))
        current.card.append(chart_from_spec, id="spec_chart_comp")
        current.card.append(Markdown("# Altair Chart"))
        for ctitle, c in get_charts():
            current.card.append(Markdown(f"{ctitle}"))
            chart = VegaChart.from_altair_chart(c)
            print(chart._spec)
            current.card.append(chart)

        current.card.refresh()

        train_data_epoch, val_data_epoch, train_data_step, val_data_step = data_objects
        (
            train_epoch_chart,
            val_epoch_chart,
            train_step_chart,
            val_step_chart,
        ) = chart_objects
        epochs = 10
        for i in range(100):
            current.card.components["spec_chart_comp"].update(
                data=update_data_object(
                    data_object, {"u": i, "v": random.random() * 100}
                )
            )
            train_step_chart.update(
                data=update_data_object(
                    train_data_step, {"step": i, "loss": random.random() * 100}
                )
            )
            val_step_chart.update(
                data=update_data_object(
                    val_data_step, {"step": i, "loss": random.random() * 100}
                )
            )
            if i % epochs == 0:
                train_epoch_chart.update(
                    data=update_data_object(
                        train_data_epoch, {"epoch": i, "loss": random.random() * 100}
                    )
                )
                val_epoch_chart.update(
                    data=update_data_object(
                        val_data_epoch, {"epoch": i, "loss": random.random() * 100}
                    )
                )
            current.card.refresh()
            time.sleep(1)

        self.next(self.native_progressbar)

    @card(type="blank")
    @step
    def native_progressbar(self):
        native_progress_bar = ProgressBar(
            max=100,
            label="Native Progress Bar",
            value=0,
            unit="percent",
            metadata="0 iter/s",
        )
        prog_bar_1 = ProgressBar(
            max=1000,
            label="Progress Bar 1",
            value=0,
            unit="percent",
            metadata="0 iter/s",
        )
        prog_bar_2 = ProgressBar(
            max=1000,
            label="Progress Bar 2",
            value=0,
            unit="percent",
            metadata="0 iter/s",
        )
        prog_bar_3 = ProgressBar(
            max=1000,
            label="Progress Bar 3",
            value=0,
            unit="percent",
            metadata="0 iter/s",
        )
        prog_bar_4 = ProgressBar(
            max=1000,
            label="Progress Bar 4",
            value=0,
            unit="percent",
            metadata="0 iter/s",
        )
        table = Table(
            [[prog_bar_1, prog_bar_2], [prog_bar_3, prog_bar_4]],
        )
        current.card.append(
            Markdown("# Progress Bar Directly To `current.card.append`")
        )
        current.card.append(native_progress_bar)
        current.card.append(Markdown("# Progress Bar In A Table"))
        current.card.append(table)
        current.card.refresh()
        n = 100
        print("Starting to measure progress...")
        for i in range(n):
            iter_per_second = i / n
            native_progress_bar.update(i, metadata="%.2f iter/s" % iter_per_second)
            for pb in [prog_bar_1, prog_bar_2, prog_bar_3, prog_bar_4]:
                pb.update(i * 10, metadata="%.2f iter/s" % iter_per_second)

            current.card.refresh()
            print(f"iteration {i}/{n}")
            time.sleep(1)
        self.next(self.component_card, foreach="iter_values")

    @card(type="blank", id="card2")
    @card(type="default", id="card1")
    @step
    def component_card(self):
        card_map = current.card
        import uuid

        current_id = uuid.uuid4().hex
        print("Appending Components to cards")
        current.card["card1"].append(
            Markdown("## [%s] Initial Content In card" % current_id), id="markdown1"
        )
        current.card["card1"].append(
            Table([[1, 2, 3], [4, 5, 6]], headers=["a", "b", "c"])
        )
        n = 500
        for i in range(n):
            current.card["card1"].components["markdown1"].update(
                f"## [{current_id}] Content updated {i*10}/{n*10} markdown1"
            )
            current.card["card1"].refresh()
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
            current.card.refresh({"value": i})
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
