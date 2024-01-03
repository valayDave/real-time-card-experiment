try:
    import altair as alt
    import pandas as pd
except ImportError:
    alt = None
    pd = None
import numpy as np

def update_spec_data(spec, data):
    spec["data"]["values"].append(data)
    return spec

def update_data_object(data_object, data):
    data_object["values"].append(data)
    return data_object


def line_chart_spec(
    title=None,
    x_name="u",
    y_name="v",
    xtitle=None,
    ytitle=None,
    width=600,
    height=400,
    with_params=True,
    x_axis_temporal=False,
):
    parameters = [
        {
            "name": "interpolate",
            "value": "linear",
            "bind": {
                "input": "select",
                "options": [
                    "basis",
                    "cardinal",
                    "catmull-rom",
                    "linear",
                    "monotone",
                    "natural",
                    "step",
                    "step-after",
                    "step-before",
                ],
            },
        },
        {
            "name": "tension",
            "value": 0,
            "bind": {"input": "range", "min": 0, "max": 1, "step": 0.05},
        },
        {
            "name": "strokeWidth",
            "value": 2,
            "bind": {"input": "range", "min": 0, "max": 10, "step": 0.5},
        },
        {
            "name": "strokeCap",
            "value": "butt",
            "bind": {"input": "select", "options": ["butt", "round", "square"]},
        },
        {
            "name": "strokeDash",
            "value": [1, 0],
            "bind": {
                "input": "select",
                "options": [[1, 0], [8, 8], [8, 4], [4, 4], [4, 2], [2, 1], [1, 1]],
            },
        },
    ]
    parameter_marks = {
        "interpolate": {"expr": "interpolate"},
        "tension": {"expr": "tension"},
        "strokeWidth": {"expr": "strokeWidth"},
        "strokeDash": {"expr": "strokeDash"},
        "strokeCap": {"expr": "strokeCap"},
    }
    spec = {
        "title": title if title else "Line Chart",
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        # "width": width,
        # "height": height,
        "params": parameters if with_params else [],
        "data": {
            "name": "values",
            "values": [

            ]
        },
        "mark": {
            "type": "line",
            "tooltip": True,
            **(parameter_marks if with_params else {}),
        },
        "selection": {
            "grid": {
                "type": "interval", 
                "bind": "scales"
            }
        },
        "encoding": {
            "x": {
                "field": x_name,
                "title": xtitle if xtitle else x_name,
                **({"timeUnit":"seconds"} if x_axis_temporal else {}),
                **({"type":"quantitative"} if not x_axis_temporal else {}),
            },
            "y": {
                "field": y_name,
                "type": "quantitative",
                "title": ytitle if ytitle else y_name,
            },
        },
    }
    data = {"values": []}
    return spec, data


def altair_line_chart_spec():
    import altair as alt
    import numpy as np
    import pandas as pd

    x = np.arange(100)
    source = pd.DataFrame({"x": x, "f(x)": np.sin(x / 5)})

    chart = alt.Chart(source).mark_line().encode(x="x", y="f(x)")

    return chart, source


def altair_interactive_charts():
    from vega_datasets import data

    cars = data.cars.url

    brush = alt.selection_interval()

    points = (
        alt.Chart(cars)
        .mark_point()
        .encode(x="Horsepower:Q", y="Miles_per_Gallon:Q", color="Origin:N")
        .add_params(brush)
        .properties(width=600, height=400)
    )

    bars = (
        alt.Chart(cars)
        .mark_bar()
        .encode(x="count()", y="Origin:N", color="Origin:N")
        .transform_filter(brush)
    )

    return (points & bars), None


def line_chart():
    data = pd.DataFrame(
        {
            "x": pd.date_range("2023-01-01", periods=100),
            "y": np.random.randn(100).cumsum(),
        }
    )
    chart = alt.Chart(data).mark_line().encode(x="x", y="y")
    return chart


def bar_chart():
    data = {"category": ["A", "B", "C", "D", "E"], "value": [3, 7, 2, 5, 6]}
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_bar().encode(x="category", y="value")
    return chart


def scatter_plot():
    x = np.random.rand(100)
    y = np.random.rand(100)
    data = pd.DataFrame({"x": x, "y": y})
    chart = alt.Chart(data).mark_circle().encode(x="x", y="y")
    return chart


def area_chart():
    data = [(1, 3), (2, 6), (3, 4), (4, 10)]
    df = pd.DataFrame(data, columns=["x", "y"])
    chart = alt.Chart(df).mark_area().encode(x="x", y="y")
    return chart


def heatmap():
    # Sample data for heatmap
    data = {
        "row": ["Row1", "Row1", "Row2", "Row2"],
        "column": ["Col1", "Col2", "Col1", "Col2"],
        "value": [10, 20, 30, 40],
    }
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_rect().encode(x="column:O", y="row:O", color="value:Q")
    return chart


def pie_chart():
    data = {"category": ["A", "B", "C", "D"], "values": [23, 17, 35, 29]}
    df = pd.DataFrame(data)
    chart = (
        alt.Chart(df)
        .mark_arc()
        .encode(
            theta=alt.Theta(field="values", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
        )
    )
    return chart


from typing import List, Tuple
from metaflow.cards import Table


def get_charts() -> List[Tuple[str, alt.Chart]]:
    return [
        ("# Altair Line Chart", line_chart()),
        ("# Altair Bar Chart", bar_chart()),
        ("# Altair Scatter Plot", scatter_plot()),
        ("# Altair Area Chart", area_chart()),
        ("# Altair Heatmap", heatmap()),
        ("# Altair Pie Chart", pie_chart()),
        ("# Altair Interactive Charts", altair_interactive_charts()[0]),
    ]


# Example usage
# chart = line_chart()
# chart.show()
