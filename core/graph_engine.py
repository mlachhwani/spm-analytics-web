import plotly.graph_objects as go
import pandas as pd


# =================================================
# GRAPH 1 — Speed vs Time with Signals
# =================================================
def plot_speed_vs_time(rtis_df: pd.DataFrame, signal_df: pd.DataFrame):
    from core.signal_mapper import map_signals_to_time

    fig = go.Figure()

    # ---- Speed line ----
    fig.add_trace(
        go.Scatter(
            x=rtis_df["logging_time"],
            y=rtis_df["speed"],
            mode="lines",
            name="Speed (kmph)",
        )
    )

    y_max = rtis_df["speed"].max() + 10

    # ---- Map signals to nearest RTIS point ----
    mapped_signals = map_signals_to_time(signal_df, rtis_df)

    # ---- Vertical signal markers ----
    for sig in mapped_signals:
        fig.add_vline(
            x=sig["logging_time"],
            line_dash="dot",
            line_color="grey",
            opacity=0.35,
        )

    # ---- Hoverable signal markers ----
    if mapped_signals:
        fig.add_trace(
            go.Scatter(
                x=[s["logging_time"] for s in mapped_signals],
                y=[y_max] * len(mapped_signals),
                mode="markers",
                marker=dict(size=8, color="red"),
                name="Signals",
                text=[
                    f"{s['emoji']} {s['signal_name']}<br>Time: {s['logging_time']}"
                    for s in mapped_signals
                ],
                hoverinfo="text",
            )
        )

    fig.update_layout(
        title="Speed vs Time with Signals",
        xaxis_title="Time",
        yaxis_title="Speed (kmph)",
        hovermode="x unified",
    )

    return fig


# =================================================
# GRAPH 2 — Speed vs Section (Map View with Emojis)
# =================================================
def plot_speed_on_map(rtis_df: pd.DataFrame, signal_df: pd.DataFrame):
    from core.signal_mapper import map_signals_to_time

    fig = go.Figure()

    # ---- Train trajectory (NO color array on line – HF safe) ----
    fig.add_trace(
        go.Scattermapbox(
            lat=rtis_df["latitude"],
            lon=rtis_df["longitude"],
            mode="lines",
            line=dict(width=4, color="blue"),
            text=[
                f"Speed: {s} kmph<br>Time: {t}"
                for s, t in zip(rtis_df["speed"], rtis_df["logging_time"])
            ],
            hoverinfo="text",
            name="Train",
        )
    )

    # ---- Map signals to coordinates + time ----
    mapped_signals = map_signals_to_time(signal_df, rtis_df)

    if mapped_signals:
        fig.add_trace(
            go.Scattermapbox(
                lat=[s["latitude"] for s in mapped_signals],
                lon=[s["longitude"] for s in mapped_signals],
                mode="text",
                text=[s["emoji"] for s in mapped_signals],
                textfont=dict(size=18),
                hovertext=[
                    f"{s['emoji']} {s['signal_name']}<br>Time: {s['logging_time']}"
                    for s in mapped_signals
                ],
                hoverinfo="text",
                name="Signals",
            )
        )

    fig.update_layout(
        title="Speed vs Section (Map View)",
        mapbox=dict(
            style="open-street-map",
            zoom=9,
            center=dict(
                lat=rtis_df["latitude"].mean(),
                lon=rtis_df["longitude"].mean(),
            ),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
    )

    return fig


# =================================================
# GRAPH 3 — Pre-Stop Speed Analysis (±2000 m)
# =================================================
def plot_pre_stop_analysis(
    rtis_df: pd.DataFrame,
    stop_event: pd.Series,
    window_m: int = 2000,
):
    stop_time = stop_event["stop_start_time"]

    stop_idx = rtis_df[rtis_df["logging_time"] == stop_time].index.min()
    if pd.isna(stop_idx):
        return None

    cumulative = 0.0
    indices = []

    # ---- Walk backwards until 2000 m covered ----
    for i in range(stop_idx, -1, -1):
        dist = rtis_df.loc[i, "dist_from_speed"]
        if pd.isna(dist):
            continue

        cumulative += dist
        indices.append(i)

        if cumulative >= window_m:
            break

    if not indices:
        return None

    window_df = rtis_df.loc[sorted(indices)].copy()
    window_df["cum_dist"] = window_df["dist_from_speed"].cumsum()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=window_df["cum_dist"],
            y=window_df["speed"],
            mode="lines+markers",
            name="Speed",
        )
    )

    fig.add_vline(
        x=window_df["cum_dist"].iloc[-1],
        line_color="red",
        line_width=2,
    )

    fig.update_layout(
        title=f"Pre-Stop Speed Analysis ⛔ {stop_event['signal_name']} @ {stop_time}",
        xaxis_title="Distance before stop (meters)",
        yaxis_title="Speed (kmph)",
    )

    return fig
