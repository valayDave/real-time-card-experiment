from metaflow.cards import Markdown, Image, Table, MetaflowCardComponent, VegaChart, ProgressBar
import time
import math
import random
from datetime import datetime
import requests



def get_random_image():
    endpoint = "https://picsum.photos/200/300"
    response = requests.get(endpoint)
    # Get the response as bytes
    image_bytes = response.content
    return image_bytes
    

def get_image_table_frozen():
    images = []
    for i in range(3):
        images.append([Image(src=get_random_image()) for j in range(3)])
    return Table(data=images, disable_updates=True)

def get_image_table_dynamic():
    images = []
    for i in range(3):
        images.append([Image(src=get_random_image(), disable_updates=False) for j in range(3)])
    return Table(data=images), [j for i in images for j in i]


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


def multi_card_markdown_test(card1="card1", card2="card2", sleep_cycles=100):
    """
    This test validates following:
    1. Multiple cards with markdown components
    2. Updating markdown components
    3. Safely calling update on components which may not exist. 
    """
    from metaflow import current
    import uuid
    current_id = uuid.uuid4().hex

    def _refresh_all():
        for c in [card1, card2]:
            current.card[c].refresh()

    current.card[card1].append(
        Markdown("## [%s] Initial Content In card" % current_id),
        id="markdown1"
    )
    current.card[card2].append(
        Table([[1, 2, 3], [4, 5, 6]], headers=["a", "b", "c"])
    )
    current.card[card2].append(
        Markdown("## [%s] Initial Content In card2" % current_id),
        id="markdown2"
    )
    _refresh_all()
    n = sleep_cycles
    for i in range(sleep_cycles):
        current.card[card1].components["markdown1"].update(
            f"## [{current_id}] Content updated {i*10}/{n*10} markdown1"
        )
        current.card[card2].components["markdown2"].update(
            f"## [{current_id}] Content updated {i*10}/{n*10} markdown2"
        )
        current.card[card2].components["markdown1"].update(
            f"## [{current_id}] Content updated {i*10}/{n*10} markdown1"
        )
        _refresh_all()
        time.sleep(1)
    current.card[card2].append(
        Markdown("## [%s] Final Content In card2" % current_id),
        id = "markdown1"
    )

def table_and_images_test(sleep_cycles=30):
    """
    This test validates following: 
    1. Table with images which are frozen and nothing is shipped over the wire
    2. Table with images which are dynamic and updates are shipped over the wire on refresh for those images
    3. An image which is dynamic and updates are shipped over the wire on refresh
    4. An image which is static and nothing is shipped over the wire on refresh and nothing breaks when refresh is called. 
    """
    from metaflow import current
    current.card.append(Markdown("# Image Table Tests"))
    current.card.append(Markdown("## Image Table Which Is Frozen In Time\n No Updates will be shipped to this table on refresh"))
    current.card.append(get_image_table_frozen())
    current.card.append(Markdown("## Image Table Which Is Dynamic\n Updates will be shipped to this table on refresh"))
    table, images = get_image_table_dynamic()
    current.card.append(table)
    current.card.append(Markdown("## Updating Image"))
    current.card.append(Image(src=get_random_image(), disable_updates=False), id="updating_image")
    current.card.append(Markdown("## Staic Image"))
    current.card.append(Image(src=get_random_image()), id="static_image")
    current.card.refresh()
    for _ in range(sleep_cycles):
        for i in images:
            i.update(bytes=get_random_image())
        current.card.components["updating_image"].update(bytes=get_random_image())
        # Trying to update `static_image` shouldnot break anything.
        current.card.components["static_image"].update(bytes=get_random_image()) 
        current.card.refresh()
        time.sleep(1)


def charting_tests(sleep_cycles=100):
    """
    Different testing scenarios with Charting: 
    1. Vanilla Vega Spec Chart
    2. Altair Chart
    3. Charts inside a table
    4. Updating the charts
    """
    from charts import line_chart_spec, update_data_object, get_charts
    from metaflow import current
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
    for i in range(sleep_cycles):
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

def frequent_refresh_test(sleep_cycles=100):
    from metaflow import current
    current.card.append(Markdown("# Frequent Refresh Test"))
    progresbar = ProgressBar(
        max=sleep_cycles,
        label="Progress Bar",
        value=0,
        unit="percent",
        metadata="0 iter/s",
    )
    time_track = "## Time Tracking\n"
    time_tracking_markdown = Markdown(time_track)
    current.card.append(progresbar)
    current.card.append(time_tracking_markdown)
    current.card.refresh()
    n = sleep_cycles
    print("Starting to measure progress...")
    for i in range(sleep_cycles):
        iter_per_second = i / n
        progresbar.update(i, metadata="%.2f iter/s" % iter_per_second)
        time_track += f"- iteration {i}/{n} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        time_tracking_markdown.update(
            time_track
        )
        current.card.refresh()
        print(f"iteration {i}/{n}")
        time.sleep(1)

def progress_bar_tests(sleep_cycles=100):
    """
    These tests validate following:
    1. Adding Progress Bar directly to `current.card.append`
    2. Adding Progress Bar in a table
    3. Updating the progress bar
    """
    from metaflow import current
    native_progress_bar = ProgressBar(
        max=sleep_cycles,
        label="Native Progress Bar",
        value=0,
        unit="percent",
        metadata="0 iter/s",
    )
    prog_bar_1 = ProgressBar(
        max=sleep_cycles*10,
        label="Progress Bar 1",
        value=0,
        unit="percent",
        metadata="0 iter/s",
    )
    prog_bar_2 = ProgressBar(
        max=sleep_cycles*10,
        label="Progress Bar 2",
        value=0,
        unit="percent",
        metadata="0 iter/s",
    )
    prog_bar_3 = ProgressBar(
        max=sleep_cycles*10,
        label="Progress Bar 3",
        value=0,
        unit="percent",
        metadata="0 iter/s",
    )
    prog_bar_4 = ProgressBar(
        max=sleep_cycles*10,
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
    n = sleep_cycles
    print("Starting to measure progress...")
    for i in range(sleep_cycles):
        iter_per_second = i / n
        native_progress_bar.update(i, metadata="%.2f iter/s" % iter_per_second)
        for pb in [prog_bar_1, prog_bar_2, prog_bar_3, prog_bar_4]:
            pb.update(i * 10, metadata="%.2f iter/s" % iter_per_second)
        current.card.refresh()
        print(f"iteration {i}/{n}")
        time.sleep(1)