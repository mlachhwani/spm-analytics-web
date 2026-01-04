import os
from core.rtis_loader import load_rtis_file
from core.signal_mapper import build_signal_context
from core.section_loader import load_section_data
from core.stop_detector import detect_signal_stops
from core.violation_engine import evaluate_speed_violations
from core.graph_engine import (
    plot_speed_vs_time,
    plot_speed_on_map,
    plot_pre_stop_analysis,
)

OUTPUT_HTML = "../web/index.html"

def main():
    # ---- LOAD DATA ----
    rtis_df = load_rtis_file("../data/sample_rtis.csv")
    rtis_df["cum_distance"] = rtis_df["dist_from_speed"].cumsum()

    section_context = load_section_data("NGP-RIG", "DOWN")
    signal_df = build_signal_context(section_context)

    stop_events_df = detect_signal_stops(rtis_df, signal_df)

    violation_df = evaluate_speed_violations(
        rtis_df,
        signal_df,
        stop_events_df,
        train_type="COACHING",
    )

    # ---- GRAPHS ----
    fig_time = plot_speed_vs_time(rtis_df, signal_df)
    fig_map = plot_speed_on_map(rtis_df, signal_df)

    html_parts = []
    html_parts.append(fig_time.to_html(full_html=False))
    html_parts.append(fig_map.to_html(full_html=False))

    for _, stop in stop_events_df.iterrows():
        fig_pre = plot_pre_stop_analysis(rtis_df, stop)
        if fig_pre:
            html_parts.append(fig_pre.to_html(full_html=False))

    # ---- FINAL HTML ----
    html = f"""
    <html>
    <head>
        <title>SPM Driving Behaviour Analysis</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>🚆 RTIS Driving Behaviour Analysis</h1>
        {''.join(html_parts)}
    </body>
    </html>
    """

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ Dashboard generated:", OUTPUT_HTML)

if __name__ == "__main__":
    main()
