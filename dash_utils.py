"""Useful wrapper functions for plotly dash.

The syntax for some dash components gets a little verbose, and arranging things
on an html page is a pain when you need divs everywhere to make things work.
These wrappers make the syntax for dcc components a bit more intuitive, and
wrap everything in a div with some default styling. They also include some
default values, so that a placeholder component can be added without needing to
specify any arguments at all.

"""

from typing import List, Dict, Union

import dash_core_components as dcc
import dash_html_components as html


def dcc_dropdown_div(
    title: str = "Dropdown",
    id: str = "dropdown",
    value: str = "-",
    opts: Union[List[str], Dict[str, str]] = None,
    width: str = "300px",
    style: dict = {
        "display": "inline-block",
        "position": "relative",
    },
    clearable: bool = False,
    searchable: bool = False,
    **kwargs
):
    """More intuitive dcc.Dropdown wrapped in an html.Div.

    Defaults are specified so that a placeholder dropdown can be created
    without setting any arguments.

    Args:
        title (str): Default "Dropdown". Text to put above the dropdown as a
            label.
        id (str): Default "dropdown". The html id for the dcc.Dropdown object.
        value (str): Default "-". Default value for the dropdown. This should
            match a key in the options dict.
        opts (list or dict): If a dict, keys are the "value"s from the
            dcc.Dropdown options list of dicts, and values are the "label"s. If
            a list, use the same values for "label"s and "value"s. This makes
            it less verbose to specify the options. For example,
            ``options=[{"label": "Age (first to now)", "value": "Age"}]`` is
            instead specified as ``options={"Age": "Age (first to now)"}``. The
            default ``None`` will first check if [the proper] options dict is
            in **kwargs, and then will use the value argument as the only
            option.
        width (str): Add "width" key to style dict. If this is None or is
            specified in the style dict, this argument isn't used.
        style (dict): Html style of the div.
        clearable (bool): dcc.Dropdown option. This arg is here to change the
            default to False.
        searchable (bool): dcc.Dropdown option. This arg is here to change the
            default to False.
        **kwargs: Keyword arguments passed to dcc.Dropdown.

    Returns:
        dash.dash_html_components.Div: This div contains two elements, the
        title and a dash.dash_core_components.Dropdown object.

    """
    if opts is not None:
        if isinstance(opts, list):
            options = [{"label": x, "value": x} for x in opts]
        elif isinstance(opts, dict):
            options = [{"label": v, "value": k} for k, v in opts.items()]
    elif "options" in kwargs.keys():
        options = kwargs["options"]
        kwargs = kwargs.pop("options")
    else:
        options = [{"label": value, "value": value}]

    if ("width" not in style.keys()) and (width is not None):
        style["width"] = width

    return html.Div(
        [
            html.Label(title),
            dcc.Dropdown(
                id=id,
                options=options,
                value=value,
                clearable=clearable,
                searchable=searchable,
                **kwargs
            ),
        ],
        style=style,
    )


def dcc_input_div(
    title: str,
    style: dict = {"font-size": "1em"},
    inline: bool = False,
    **kwargs,
):
    """Set default html properties for input boxes."""
    dcc_input = dcc.Input(
        style={"font-size": "1em"},
        **kwargs
    )
    if inline:
        return html.Div([title, dcc_input], style=style)
    return html.Div([title, html.Br(), dcc_input], style=style)


def dcc_range_slider_div(*args):
    """Set default htmls properties for sliders."""
    return html.Div(
        args,
        style={
            "width": "325px",
            "display": "inline-block",
            "position": "relative",
        },
    )


def message_graph(text: str, font_size: int = 18) -> dict:
    """Return an empty plotly figure with a message.

    Args:
        text (str): The message to display.
        font_size (int): The font size of the message.

    Returns:
        dict: A plotly figure dict.

    """
    return {
        "layout": {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": text,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": font_size},
                }
            ],
        }
    }
