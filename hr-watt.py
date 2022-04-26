##
## Python program will run on selection.
##
import numpy as np
import pandas as pd
import tempfile
import pathlib
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def main():
    activity_unique_id = str(int(GC.activityMetrics()['Checksum']))
    activity_prefix = "GC_" + activity_unique_id + "_"
    temp_directory = pathlib.Path(tempfile.gettempdir())
    path_to_render = None
    for file_path in temp_directory.iterdir():
        if file_path.name.startswith(activity_prefix):
            path_to_render = file_path
            break

    if not path_to_render:
        temp_file = tempfile.NamedTemporaryFile(mode="w+t", prefix=activity_prefix, suffix=".html", delete=False)
        run(temp_file)
        path_to_render = pathlib.Path(temp_file.name)
    GC.webpage(path_to_render.as_uri())


def run(temp_file):
    ## Define temporary file
    ## Convert seconds to time format
    secs = GC.series(GC.SERIES_SECS)
    def format_seconds_to_hhmmss(seconds):
        hours = seconds // (60*60)
        seconds %= (60*60)
        minutes = seconds // 60
        seconds %= 60
        return "%02i:%02i:%02i" % (hours, minutes, seconds)

    ## Daten für das erste Diagramm
    xx1 = np.asarray(GC.series(GC.SERIES_WATTS))
    yy1 = np.asarray(GC.series(GC.SERIES_HR))

    xx1Filter = xx1[(xx1 > 0) & (yy1 > 30)]
    yy1Filter = yy1[(xx1 > 0) & (yy1 > 30)]

    ## Daten für das zweite Diagramm
    xx = [format_seconds_to_hhmmss(i) for i in secs]
    xx2 = np.asarray(GC.series(GC.SERIES_SECS))
    yy2 = np.asarray(GC.series(GC.SERIES_WATTS))
    yy3 = np.asarray(GC.series(GC.SERIES_HR))

    ## Farben der Linien festlegen
    yy1c = "#ffaa00"
    yy2c = "#ff0000"

    ## Für die aktuelle ausgewählte Aktivität den CP holen
    activity = GC.activityMetrics()
    secLen = len(GC.series((GC.SERIES_SECS)))
    cp_column= pd.DataFrame(GC.athleteZones(date=activity["date"], sport="bike"))
    cp_value = cp_column['cp'][0]
    ## Horizontale Linie für das 1. Diagramm
    avgHR = activity["Average_Heart_Rate"]
    PowerMax = np.amax(GC.series((GC.SERIES_WATTS)))
    ## Vertikale Linie für das 1. Diagramm
    avgPower = activity["Average_Power"]
    HrMax = np.amax(GC.series((GC.SERIES_HR)))
    HrMin = np.amin(GC.series((GC.SERIES_HR)))

    fig = make_subplots(
        rows=2,
        cols=1,
        horizontal_spacing=0,
        vertical_spacing=0.15,
        subplot_titles=("HR VS Power", "Power and HR over Time"),
        specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
    )
    #fig.append_trace
    fig.add_trace(go.Scatter(
        x=xx1Filter,
        y=yy1Filter,
        mode="markers",
        marker=dict(size=3),
        name='HR',
        line = dict(shape = 'linear', color =yy2c, width= 1.2),
        hovertemplate =
        '<b>HR</b>: %{y:.2f} bpm'+
        '<br><b>Power</b>: %{x} watts',
    ), row=1, col=1, secondary_y=False)

    fig.add_trace(go.Scatter(
        x=xx,
        y=yy2,
        name='Power',
        line = dict(shape = 'linear', color =yy1c, width= 1.2),
        fill="tozeroy",
        hovertemplate =
        '<b>Power</b>: %{y:.2f} watts'+
        '<br><b>HR</b>: %{text} bpm'+
        '<br><b>Duration</b>: %{x}',
        text = ['{}'.format(i) for i in yy3],
    ), row=2, col=1, secondary_y=False)

    fig.add_trace(go.Scatter(
        x=xx,
        y=yy3,
        name='HR',
        hovertemplate =
        '<b>Power</b>: %{text} watts'+
        '<br><b>HR</b>: %{y:.2f} bpm'+
        '<br><b>Duration</b>: %{x}',
        text = ['{}'.format(i) for i in yy2],
        line = dict(shape = 'linear', color =yy2c, width= 1.2)
    ), row=2, col=1,  secondary_y=True)

    ## Line für durchschnittliche Herzfrequenz
    fig.add_shape(
        xref='x',
        yref='y',
        type='line',
        x0=0,
        y0=avgHR,
        x1=PowerMax,
        y1=avgHR,
        line=dict(
            color="#ffaa00",
            width=1.5,
            dash="dash",
       ), row=1, col=1
    )

    ## Line für durchschnittliche Leistung
    fig.add_shape(
        xref='x',
        yref='y',
        type='line',
        x0=avgPower,
        y0=HrMin,
        x1=avgPower,
        y1=HrMax,
        line=dict(
            color="#ffaa00",
            width=1.5,
            dash="dash",
       ), row=1, col=1
    )

    ## Line für CP Wert
    fig.add_shape(
        xref='x',
        yref='y2',
        type='line',
        x0=0,
        y0=cp_value,
        x1=secLen,
        y1=cp_value,
        line=dict(
            color="#ffaa00",
            width=1.5,
            dash="dash",
       ), row=2, col=1
    )

    ## Anmerkung für durchschnittliche Herzfrequenz
    fig.add_annotation(
        xref="x",
        yref="y",
        x=0,
        y=avgHR+5,
        xshift = 50,
        text='<b>Avg HR = </b>:'+str(np.round(avgHR)),
        showarrow=False,
        font=dict(
            family="Noto Sans",
            size=10,
        ), row=1, col=1
    )

    ## Anmerkung für durchschnittliche Leistung
    fig.add_annotation(
        xref="x",
        yref="y",
        x=avgPower,
        y=HrMin+5,
        xshift = 50,
        text='<b>Avg Power = </b>:'+str(np.round(avgPower)),
        showarrow=False,
        font=dict(
            family="Noto Sans",
            size=10,
        ), row=1, col=1
    )

    ## Anmerkung für die CP Linie sodas der CP Wert und Text angezeit wird.
    fig.add_annotation(
        xref="x",
        yref="y2",
        x=0,
        y=cp_value+30,
        xshift = 50,
        text='<b>Critical Power =  </b>'+str(cp_value),
        showarrow=False,
        font=dict(
            family="Noto Sans",
            size=10,
        ), row=2, col=1
    )

    ## Update xaxis properties
    ## Erstes Diagramm
    fig.update_xaxes(title_text="Watts", row=1, col=1)
    ## Zweites Diagramm
    fig.update_xaxes(title_text="Time",
        showgrid=True,
        showline=True,
        showticklabels=True,
        linecolor='white',
        linewidth=2,
        tickmode='auto',
        nticks=10,
        ticks="inside",
        tickwidth=2,
        ticklen=10,
        tickcolor='white',
        showspikes=True,
        spikecolor="white",
        spikesnap="hovered data",
        spikemode="across",
        spikethickness=1.5,row=2, col=1)

    ## Update yaxis properties
    fig.update_yaxes(title_text="BPM", row=1, col=1)
    fig.update_yaxes(title_text="Watts", secondary_y=False, showgrid=False, row=2, col=1)
    fig.update_yaxes(title_text="BPM", secondary_y=True, showgrid=False, row=2, col=1)

    ## Globale Änderung der y Achse
    fig.update_yaxes(
        title_standoff=5,
        titlefont=dict(
            family='Noto Sans',
            size=12
        ),
        tickfont=dict(
            family='Noto Sans',
            size=12
        )
    )

    ## Update layout properties
    fig.update_layout(
        template='plotly_dark',
        hoverlabel_align = 'left',
        margin=dict(l=15, r=5, t=55, b=5),
        legend_title="Legend Title",
        legend=dict(
            orientation="h",
            #yanchor="top",
            y=1.05,
            #xanchor="left",
            x=0
        ),
    )

    plotly.offline.plot(fig, auto_open=False, filename=temp_file.name)


main()
