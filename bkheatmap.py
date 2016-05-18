import argparse
import math
import os

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, gridplot, output_file, save
import matplotlib as mpl
from matplotlib import cm
import numpy as np
import pandas as pd
import scipy.spatial.distance as dist
import scipy.cluster.hierarchy as hier

__version__ = "0.1.4"

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--palette", default="Spectral_r",
                        help="default: %(default)s")
    parser.add_argument("--width", type=int, default=400,
                        help="default: %(default)d")
    parser.add_argument("--height", type=int, default=400,
                        help="default: %(default)d")
    parser.add_argument("--scale", default="row",
                        help="default: %(default)s")
    parser.add_argument("--metric", default="euclidean",
                        help="default: %(default)s")
    parser.add_argument("--method", default="single",
                        help="default: %(default)s")
    parser.add_argument("table")
    return parser

def calc_zscore(df, scale):
    if scale == "row":
        df = df.T
        df = (df - df.mean()) / df.std(ddof=0)
        df = df.T
    elif scale == "column":
        df = (df - df.mean()) / df.std(ddof=0)
    return df

def cluster(df, metric="euclidean", method="single", row=True, column=True):
    row_linkmat, col_linkmat = None, None
    if row:
        distmat = dist.pdist(df, metric)
        row_linkmat = hier.linkage(distmat, method)
        df = df.iloc[hier.leaves_list(row_linkmat), :]
    if column:
        df = df.T
        distmat = dist.pdist(df, metric)
        col_linkmat = hier.linkage(distmat, method)
        df = df.iloc[hier.leaves_list(col_linkmat), :].T
    return df, row_linkmat, col_linkmat

def assign_color(df, value_var, colormap):
    vmax = df[value_var].abs().max()
    vmin = vmax * -1
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    df["color"] = df.apply(lambda s: mpl.colors.rgb2hex(
                           cm.get_cmap(colormap)(norm(s[value_var]))),
                           axis=1)
    return df

def assign_cat_color(df, cat_var, colormap):
    color = {}
    norm = mpl.colors.Normalize(vmin=0, vmax=len(df[cat_var].unique())-1)
    for i, cat in enumerate(df[cat_var].unique()):
        color[cat] = mpl.colors.rgb2hex(cm.get_cmap(colormap)(norm(i)))
    df["color"] = df.apply(lambda s: color[s[cat_var]], axis=1)
    return df

def get_colorbar_source(df, value_var, colormap):
    vmax = df[value_var].abs().max()
    vmin = vmax * -1
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    value = np.linspace(vmin, vmax, num=50)
    color = []
    for v in value:
        color.append(mpl.colors.rgb2hex(cm.get_cmap(colormap)(norm(v))))
    return ColumnDataSource(data=dict(value=value, color=color))

def bkheatmap(df, prefix, scale="row", metric="euclidean", method="single",
              width=400, height=400, palette="Spectral_r"):
    df.index.name = "row"
    zscore = calc_zscore(df, scale=scale)
    zscore = zscore.dropna()
    zscore, rlm, clm = cluster(zscore, metric=metric, method=method)

    coldict = dict((t[1], t[0]) for t in enumerate(zscore.columns.tolist()))
    rowdict = dict((t[1], t[0]) for t in enumerate(zscore.index.tolist()))
    tidy_df = pd.melt(zscore.reset_index(), id_vars=["row"],
                      var_name="column", value_name="zscore")
    tidy_df["row_id"] = tidy_df.apply(lambda s: rowdict[s["row"]], axis=1)
    tidy_df["column_id"] = tidy_df.apply(lambda s: coldict[s["column"]], axis=1)
    tidy_df["value"] = tidy_df.apply(lambda s: df[s["column"]][s["row"]], axis=1)
    tidy_df = assign_color(tidy_df, "zscore", palette)

    source = ColumnDataSource(data=tidy_df)
    TOOLS = "pan,box_zoom,wheel_zoom,reset,hover"

    heatmap = figure(x_range=(-0.5, max(coldict.values()) + 0.5),
                     y_range=(-0.5, max(rowdict.values()) + 0.5),
                     plot_width=width, plot_height=height,
                     toolbar_location="above", tools=TOOLS, logo=None,
                     min_border_left=0, min_border_right=0,
                     min_border_top=0, min_border_bottom=0)

    heatmap.grid.grid_line_color = None
    heatmap.axis.visible = None
    heatmap.outline_line_color = None

    heatmap.rect("column_id", "row_id", 1, 1, source=source,
                 color="color", line_color=None, alpha=1)

    heatmap.select_one(HoverTool).tooltips = [
        ("row", "@row"),
        ("column", "@column"),
        ("value", "@value"),
        ("z-score", "@zscore")
    ]

    row, row_id = zip(*rowdict.items())
    row_group = []
    row_name = []
    if all(s.count(":") for s in row):
        for s in row:
            rg, rn = s.split(":")[-2:] # only one-level grouping
            row_group.append(rg)
            row_name.append(rn)
    else:
        row_name = row

    rowlabel = figure(plot_width=200, plot_height=heatmap.plot_height,
                     x_range=(0, 1), y_range=heatmap.y_range, title=None,
                     min_border_left=0, min_border_right=0,
                     min_border_top=0, min_border_bottom=0,
                     toolbar_location=None, webgl=True)
    rowlabel.text(0.05, "row_id", "row_name",
                 source=ColumnDataSource(data=dict(row_name=row_name,
                                                   row_id=row_id)),
                 text_align="left", text_baseline="middle",
                 text_font_size="5pt", text_color="#a8a8a8")
    rowlabel.axis.visible = None
    rowlabel.grid.grid_line_color = None
    rowlabel.outline_line_color = None

    column, column_id = zip(*coldict.items())
    column_group = []
    column_name = []
    if all(s.count(":") for s in column):
        for s in column:
            cg, cn = s.split(":")[-2:] # only one-level grouping
            column_group.append(cg)
            column_name.append(cn)
    else:
        column_name = column

    collabel = figure(plot_width=heatmap.plot_width, plot_height=200,
                     x_range=heatmap.x_range, y_range=(-1, 0), title=None,
                     min_border_left=0, min_border_right=0,
                     min_border_top=0, min_border_bottom=0,
                     toolbar_location=None, webgl=True)
    collabel.text("column_id", -0.05, "column_name",
                 source=ColumnDataSource(data=dict(column_name=column_name,
                                                   column_id=column_id)),
                 text_align="right", text_baseline="middle",
                 text_font_size="5pt", text_color="#a8a8a8",
                 angle=math.pi/3)
    collabel.axis.visible = None
    collabel.grid.grid_line_color = None
    collabel.outline_line_color = None

    col_dendro = hier.dendrogram(clm, no_plot=True)
    coldendro = figure(plot_width=heatmap.plot_width, plot_height=180,
                     x_range=heatmap.x_range, title=None,
                     min_border_left=0, min_border_right=0,
                     min_border_top=0, min_border_bottom=0,
                     toolbar_location=None, webgl=True)

    col_height = 0.09 * (df.shape[0] * width) / (df.shape[1] * height)
    if column_group:
        coldendro.multi_line(list(np.asarray(col_dendro["icoord"])/10 - 0.5),
                           list(np.asarray(col_dendro["dcoord"]) + col_height/2),
                           line_color="#a8a8a8", line_width=1)

        groupdict = {}
        groupdict["column_id"] = column_id
        groupdict["column_group"] = column_group
        groupdf = pd.DataFrame(groupdict)
        groupdf = assign_cat_color(groupdf, "column_group", "Paired")
        coldendro.rect("column_id", 0, width=1, height=col_height,
                     fill_color="color", line_color=None,
                     source=ColumnDataSource(data=groupdf))
    else:
        coldendro.multi_line(list(np.asarray(col_dendro["icoord"])/10 - 0.5),
                           list(np.asarray(col_dendro["dcoord"])),
                           line_color="#a8a8a8", line_width=1)

    coldendro.axis.visible = None
    coldendro.grid.grid_line_color = None
    coldendro.outline_line_color = None

    row_dendro = hier.dendrogram(rlm, orientation="left", no_plot=True)
    rowdendro = figure(plot_width=200, plot_height=heatmap.plot_height,
                     y_range=heatmap.y_range, title=None,
                     min_border_left=0, min_border_right=0,
                     min_border_top=0, min_border_bottom=0,
                     toolbar_location=None, webgl=True)

    if row_group:
        rowdendro.multi_line(list(np.asarray(row_dendro["dcoord"])*-1 - 0.15),
                           list(np.asarray(row_dendro["icoord"])/10 - 0.5),
                           line_color="#a8a8a8", line_width=1)

        groupdict = {}
        groupdict["row_id"] = row_id
        groupdict["row_group"] = row_group
        groupdf = pd.DataFrame(groupdict)
        groupdf = assign_cat_color(groupdf, "row_group", "Set3")
        rowdendro.rect(0, "row_id", width=0.3, height=1,
                     fill_color="color", line_color=None,
                     source=ColumnDataSource(data=groupdf))
    else:
        rowdendro.multi_line(list(np.asarray(row_dendro["dcoord"])*-1),
                           list(np.asarray(row_dendro["icoord"])/10 - 0.5),
                           line_color="#a8a8a8", line_width=1)

    rowdendro.axis.visible = None
    rowdendro.grid.grid_line_color = None
    rowdendro.outline_line_color = None

    empty = figure(plot_width=rowdendro.plot_width,
                        plot_height=coldendro.plot_height, title=None,
                        toolbar_location=None)
    # Plot a circle to escape NO_DATA_RENDERERS error
    empty.circle(x=0, y=0, color=None)
    empty.axis.visible = None
    empty.grid.grid_line_color = None
    empty.outline_line_color = None

    colorbar = figure(y_range=(-0.5, 0.5), x_axis_location="above",
                           plot_width=rowdendro.plot_width,
                           plot_height=coldendro.plot_height, title=None,
                           min_border_top=70, min_border_bottom=70,
                           toolbar_location=None)
    colorbar.rect(x="value", y=0, fill_color="color",
                       line_color=None, width=1, height=1,
                       source=get_colorbar_source(tidy_df, "zscore", palette))
    colorbar.axis.axis_line_color = None
    colorbar.axis.major_tick_in = 0
    colorbar.xaxis.axis_label = "z-score"
    colorbar.xaxis.axis_label_text_color = "#a8a8a8"
    colorbar.xaxis.axis_label_text_font_size = "12pt"
    colorbar.xaxis.major_label_text_color = "#a8a8a8"
    colorbar.xaxis.major_tick_line_color = "#a8a8a8"
    colorbar.yaxis.major_tick_line_color = None
    colorbar.yaxis.major_label_text_color = None
    colorbar.axis.minor_tick_line_color = None
    colorbar.grid.grid_line_color = None
    colorbar.outline_line_color = None

    output_file("{0}.bkheatmap.html".format(prefix),
                title="{0} Bokeh Heatmap".format(prefix))
    save(gridplot([[colorbar, coldendro, None],
                   [rowdendro, heatmap, rowlabel],
                   [empty, collabel, None]]))

def main():
    parser = get_parser()
    args = parser.parse_args()
    prefix = os.path.splitext(os.path.basename(args.table))[0]
    df = pd.read_table(args.table, index_col=0)
    bkheatmap(df, prefix=prefix, scale=args.scale,
              metric=args.metric, method=args.method,
              width=args.width, height=args.height,
              palette=args.palette)

if __name__ == "__main__":
    exit(main())
