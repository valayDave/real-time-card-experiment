from charts import line_chart_spec, update_spec_data
from metaflow import current
from metaflow.cards import (
    VegaChart,
    MetaflowCardComponent,
    Table,
    Markdown,
    ProgressBar,
)
from metaflow.plugins.cards.card_modules.components import with_default_component_id
from tensorflow import keras  # pylint: disable=import-error
from keras import callbacks  # pylint: disable=import-error


class LineChart(MetaflowCardComponent):
    REALTIME_UPDATABLE = True

    def __init__(
        self, title, xtitle, ytitle, x_name, y_name, width, height, with_params=False, x_axis_temporal=False
    ):
        super().__init__()

        self.spec, _ = line_chart_spec(
            title=title,
            xtitle=xtitle,
            ytitle=ytitle,
            x_name=x_name,
            y_name=y_name,
            width=width,
            height=height,
            with_params=with_params,
            x_axis_temporal=x_axis_temporal,
        )

    def update(self, data):  # Can take a diff
        self.spec = update_spec_data(self.spec, data)

    @with_default_component_id
    def render(self):
        vega_chart = VegaChart(self.spec,)
        vega_chart.component_id = self.component_id
        return vega_chart.render()


def get_charts_in_table(width_per_chart=600, height_per_chart=400):
    from collections import defaultdict
    import itertools

    chart_types = ["train", "val"]
    epoch_step = ["step", "epoch"]
    metric_types = ["loss", "accuracy"]
    infinite_defaultdict = lambda: defaultdict(infinite_defaultdict)
    chart_dict = infinite_defaultdict()
    for chart_type, epoch_or_step, metric_type in itertools.product(
        chart_types, epoch_step, metric_types
    ):
        chart = LineChart(
            title=f"{chart_type} {epoch_or_step} {metric_type}",
            xtitle=epoch_or_step,
            ytitle=metric_type,
            x_name=epoch_or_step,
            y_name=metric_type,
            width=width_per_chart,
            height=height_per_chart,
            with_params=False,
        )
        chart_dict[chart_type][epoch_or_step][metric_type] = chart

    components = [
        Markdown("## Loss For Train, Val"),
        Table(
            [
                [
                    Markdown("### Training"),
                    chart_dict["train"]["step"]["loss"],
                ],
                [
                    Markdown("### Validation"),
                    chart_dict["val"]["epoch"]["loss"],
                ]
            ],
        ),
        Markdown("## Accuracy For Train, Val"),
        Table(
            [
                [
                    Markdown("### Training"),
                    chart_dict["train"]["step"]["accuracy"],
                ],
                [
                    Markdown("### Validation"),
                    chart_dict["val"]["epoch"]["accuracy"],
                ]
            ],
        ),
    ]

    return components, chart_dict


def get_progress_bar_table(
    max_epochs,
    max_steps,
):
    epoch_progress_bar = ProgressBar(
        max=max_epochs,
        label="Epoch",
    )
    step_progress_bar = ProgressBar(
        max=max_steps,
        label="Step",
    )
    components = [
        Markdown("## Training Progess"),
        Table(
            [
                [
                    epoch_progress_bar,
                    step_progress_bar,
                ],
            ],
            headers=["Epoch", "Step"],
        ),
    ]
    progress_bars = {
        "epoch": epoch_progress_bar,
        "step": step_progress_bar,
    }
    return components, progress_bars


class MetaflowCardUpdates(callbacks.Callback):
    def __init__(self, card_id=None, log_every_n_steps=1):
        super().__init__()
        self.card_id = card_id
        self.current_epoch = 0
        self.log_every_n_steps = log_every_n_steps
        

    def curret_total_steps(self, steps):
        return self.current_epoch * self.params["steps"] + steps

    def on_train_begin(self, logs=None):
        self.setup_card()
        self.setup_components()

    def setup_components(self):
        progress_components, self.progress_bars = get_progress_bar_table(
            max_epochs=self.params["epochs"],
            max_steps=self.params["steps"] * self.params["epochs"],
        )
        chart_components, self.charts = get_charts_in_table()
        self.card.extend(progress_components)
        self.card.extend(chart_components)
        self.card.refresh()

    def setup_card(self):
        if self.card_id is None:
            self.card = current.card
        else:
            self.card = current.card[self.card_id]

    def on_train_batch_begin(self, batch, logs=None):
        self.progress_bars["step"].update(self.curret_total_steps(batch))
        self.card.refresh()

    def on_train_batch_end(self, batch, logs=None):
        if batch % self.log_every_n_steps != 0:
            return
        self.charts["train"]["step"]["loss"].update(
            {
                "step": self.curret_total_steps(batch),
                "loss": logs["loss"],
            }
        )
        self.charts["train"]["step"]["accuracy"].update(
            {
                "step": self.curret_total_steps(batch),
                "accuracy": logs["accuracy"],
            }
        )
        self.card.refresh()

    def on_epoch_begin(self, epoch, logs=None):
        self.current_epoch = epoch
        self.progress_bars["epoch"].update(epoch)
        self.card.refresh()

    def on_epoch_end(self, epoch, logs=None):
        self.charts["val"]["epoch"]["loss"].update(
            {
                "epoch": epoch,
                "loss": logs["val_loss"],
            }
        )
        self.charts["val"]["epoch"]["accuracy"].update(
            {
                "epoch": epoch,
                "accuracy": logs["val_accuracy"],
            }
        )
        self.card.refresh()


def get_callback():
    return MetaflowCardUpdates(
        log_every_n_steps = 100,
    )
