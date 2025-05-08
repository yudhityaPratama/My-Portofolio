from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
from faicons import icon_svg
from shinywidgets import render_plotly
from state_choices import STATE_CHOICES

from shiny import reactive
from shiny.express import input, render, ui

# The directory containing this file
app_dir = Path(__file__).parent


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


# ---------------------------------------------------------------------
# Reactive calculations to read data
# ---------------------------------------------------------------------
@reactive.calc
def listings_df():
    return pd.read_csv(app_dir / "listings.csv")


@reactive.calc
def list_price_df():
    return pd.read_csv(app_dir / "list_price.csv")


@reactive.calc
def for_sale_df():
    return pd.read_csv(app_dir / "for_sale.csv")


# ---------------------------------------------------------------------
# Reactive calculations to filter data by date range
# N.B. since the reading of data happens in an *upstream* reactive calculation,
# the data will be read only once and then filtered as needed
# ---------------------------------------------------------------------
@reactive.calc
def listings_filtered():
    return filter_by_date(listings_df(), input.date_range())


@reactive.calc
def list_price_filtered():
    return filter_by_date(list_price_df(), input.date_range())


@reactive.calc
def for_sale_filtered():
    return filter_by_date(for_sale_df(), input.date_range())


# ---------------------------------------------------------------------
# Start building the UI
# ---------------------------------------------------------------------

ui.page_opts(title="US Housing App", id="page")

with ui.sidebar():
    ui.input_select(
        "state",
        "Filter by state",
        choices=STATE_CHOICES,
    )
    ui.input_slider(
        "date_range",
        "Filter by date range",
        min=string_to_date("2018-04-30"),
        max=string_to_date("2024-04-30"),
        value=[string_to_date(x) for x in ["2018-04-30", "2024-04-30"]],
    )

with ui.layout_column_wrap():
    with ui.value_box(showcase=icon_svg("dollar-sign")):
        "Latest Median List Price"

        @render.ui
        def price():
            df = list_price_filtered()
            df = df[df["StateName"] == input.state()]
            last_value = df.iloc[-1, -1]
            return f"${last_value:,.0f}"

    with ui.value_box(showcase=icon_svg("house")):
        "Latest Home Inventory Change"

        @render.ui
        def change():
            df = for_sale_filtered()
            df = df[df["StateName"] == input.state()]
            last_value = df.iloc[-1, -1]
            second_last_value = df.iloc[-2, -1]
            percent_change = (last_value - second_last_value) / second_last_value * 100
            sign = "+" if percent_change > 0 else ""
            return f"{sign}{percent_change:.2f}%"


with ui.navset_card_underline(title="Median List Price"):

    with ui.nav_panel(" Plot", icon=icon_svg("chart-line")):

        @render_plotly
        def list_price_plot():
            df = list_price_filtered()
            if input.state() == "United States":
                df = df[df["StateName"] != "United States"]
            else:
                df = df[df["StateName"] == input.state()]

            fig = px.line(df, x="Date", y="Value", color="StateName")
            fig.update_xaxes(title_text="")
            fig.update_yaxes(title_text="")
            return fig

    with ui.nav_panel(" Table", icon=icon_svg("table")):

        @render.data_frame
        def list_price_table():
            return render.DataGrid(list_price_df())


with ui.navset_card_underline(title="Home Inventory"):

    with ui.nav_panel(" Plot", icon=icon_svg("chart-line")):

        @render_plotly
        def for_sale_plot():
            df = for_sale_filtered()
            if input.state() == "United States":
                df = df[df["StateName"] != "United States"]
            else:
                df = df[df["StateName"] == input.state()]

            fig = px.line(df, x="Date", y="Value", color="StateName")
            fig.update_xaxes(title_text="")
            fig.update_yaxes(title_text="")
            return fig

    with ui.nav_panel(" Table", icon=icon_svg("table")):

        @render.data_frame
        def for_sale_table():
            return render.DataGrid(for_sale_df())


with ui.navset_card_underline(title="New Listings"):

    with ui.nav_panel(" Plot", icon=icon_svg("chart-line")):

        @render_plotly
        def listings_plot():
            df = listings_filtered()
            if input.state() == "United States":
                df = df[df["StateName"] != "United States"]
            else:
                df = df[df["StateName"] == input.state()]

            fig = px.line(df, x="Date", y="Value", color="StateName")
            fig.update_xaxes(title_text="")
            fig.update_yaxes(title_text="")
            return fig

    with ui.nav_panel(" Table", icon=icon_svg("table")):

        @render.data_frame
        def listings_table():
            return render.DataGrid(listings_df())
