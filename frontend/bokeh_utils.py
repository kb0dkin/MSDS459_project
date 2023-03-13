from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.palettes import Category10
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
import pandas as pd
import random


def get_bokeh_items(guitar_list, review_list):

    p = []

    # Number of Models per Manufacturer
    c = 0; p.append([])
    manu_list = list(set([guitar.manufacturer for guitar in guitar_list]))
    counts = {}
    for manu in manu_list:
        num_models = sum(guitar.manufacturer == manu for guitar in guitar_list)
        counts[manu] = num_models
    # sort the dictionary by value, descending
    counts = {k: v for k, v in sorted(counts.items(), key=lambda item: item[1], reverse=True)}
    p[c] = figure(
        x_range=list(counts.keys()),
        height=350,
        sizing_mode="stretch_width"
    )
    p[c].vbar(x=list(counts.keys()), top=list(counts.values()), width=0.5)
    p[c].xgrid.grid_line_color = None
    p[c].y_range.start = 0
    p[c].xaxis.major_label_orientation = 3.1416 / 2

    # Pie Chart for Number of Strings
    c += 1; p.append([])
    num_strings_list = list(set([guitar.num_strings for guitar in guitar_list]))
    counts = {}
    for num_strings in num_strings_list:
        num_models = sum(guitar.num_strings == num_strings for guitar in guitar_list)
        counts[num_strings] = num_models
    # convert number to strings and None to 'Unknown'
    counts = {str(k) if k is not None else 'Unknown': v for k, v in counts.items()}
    data = pd.Series(counts).reset_index(name='value').rename(columns={'index': 'num_strings'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * 3.1416
    data['color'] = Category10[len(counts)]
    p[c] = figure(height=350, toolbar_location=None, tools="hover",
               tooltips="@num_strings: @value", x_range=(-0.5, 1.0))
    p[c].wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='num_strings', source=data)
    p[c].axis.axis_label = None
    p[c].axis.visible = False
    p[c].grid.grid_line_color = None

    # Pie Chart for Scale Length
    c += 1; p.append([])
    scale_length_list = list(set([guitar.scale_length for guitar in guitar_list]))
    counts = {}
    for scale_length in scale_length_list:
        num_models = sum(guitar.scale_length == scale_length for guitar in guitar_list)
        counts[scale_length] = num_models
    counts = {k if k is not None else 0: v for k, v in counts.items()} # convert None to 0 for now
    # bin the scale lengths and convert to strings
    counts_binned = {}
    for key, value in counts.items():
        rounded_key = round(key)
        key_range = f"{rounded_key-1}\"-{rounded_key}\""
        counts_binned[key_range] = counts_binned.get(key_range, 0) + value
    counts_binned = {k if k != '-1\"-0\"' else 'Unknown': v for k, v in counts_binned.items()} # convert '-1-0' to 'Unknown'
    counts_binned = dict(sorted(counts_binned.items()))
    data = pd.Series(counts_binned).reset_index(name='value').rename(columns={'index': 'scale_length'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * 3.1416
    data['color'] = Category10[len(counts_binned)]
    p[c] = figure(height=350, toolbar_location=None, tools="hover",
                tooltips="@scale_length: @value", x_range=(-0.5, 1.0))
    p[c].wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='scale_length', source=data)
    p[c].axis.axis_label = None
    p[c].axis.visible = False
    p[c].grid.grid_line_color = None


    # Extract the components
    script = []
    div = []
    for i in range(len(p)):
        script.append([])
        div.append([])
        script[i], div[i] = components(p[i])

    return script, div