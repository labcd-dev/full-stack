import time
from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from frontend_streamlit.ga_agent_ui.ga_agent_utils import drain_event_queue, empty_plot_data
from frontend_streamlit.mulo_designer_utils import show_performance_plots, generate_controller_name

# -- Colour palette ------------------------------------------------------------
_BLUE = "#2196F3"
_RED = "#F44336"
_GREEN = "#4CAF50"
_ORANGE = "#FF9800"
_PURPLE = "#9C27B0"
_TEAL = "#00BCD4"
_GRAY = "rgba(120,120,120,0.55)"
_RANGE_FILL = "rgba(33,150,243,0.13)"
_TEMPLATE = "plotly_white"


# -- Public entry-point --------------------------------------------------------

def display_project_page(run_by_ga_agent_ui: bool = True) -> None:
    """Display the project page with design results."""

    # -- Header ----------------------------------------------------------------
    col_title, col_btn = st.columns([6, 1])
    with col_title:
        rc = st.session_state.get("run_config", {})
        case_name = rc.get("case_study_file", "Unknown").replace(".json", "")
        if not run_by_ga_agent_ui:
            case_name = generate_controller_name()
        st.markdown(f"## 🎛️ {case_name} — Controller Tuning")
    with col_btn:
        st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
        st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
        if st.button("🏠 New Experiment", width = 'stretch'):
            st.session_state["mulo_designer_stage"] = "setup"
            _reset_and_go_home()
            return

    # -- Configuration badges --------------------------------------------------
    _render_config_badges()
    st.markdown("---")

    # -- Drain the queue and refresh plot_data ---------------------------------
    drain_event_queue()
    pd: Dict[str, Any] = st.session_state.plot_data

    # -- Live status bar -------------------------------------------------------
    _render_status_bar(pd)
    st.markdown("")

    # -- Main plots ----------------------------------------------------------------
    if not pd["cumulative_nfe"]:
        st.info("⏳  Waiting for the first generation result…")
    else:
        if run_by_ga_agent_ui:
            tab_cost, tab_metrics, tab_gains, tab_summary = st.tabs([
                "Baseline Cost",
                "Performance Metrics",
                "PID Gains",
                "LLM Summary",
            ])
        else:
            tab_performance, tab_cost, tab_metrics, tab_gains, tab_summary, tab_result = st.tabs([
                "Performance Result",
                "Baseline Cost",
                "Performance Metrics",
                "PID Gains",
                "LLM Summary",
                "Final Result",
            ])

            designer = st.session_state["designer"]

            with tab_performance:
                if designer.controller_designed:
                    show_performance_plots()
                else:
                    st.info("Results will appear here once available...")

            with tab_result:
                is_complete = designer.controller_index >= len(designer.controller_structure)
                idx = designer.controller_index
                text = f" Number {idx}" if not is_complete else ""

                if designer.controller_designed:
                    with st.expander(f"🐍 View Raw Python Code Output ({"Final " if is_complete else ""}Loop{text} Designed)"):
                        st.code(st.session_state["modified_code"])
                    with st.expander(f"📄 View Raw JSON Output ({"Final " if is_complete else ""}Loop{text} Designed)"):
                        st.json(st.session_state["modified_controller_structure"])
                else:
                    st.info("Results will appear here once available...")

        with tab_cost:
            st.plotly_chart(_build_cost_fig(pd), width = 'stretch')

        with tab_metrics:
            st.plotly_chart(_build_metrics_fig(pd), width = 'stretch')

        with tab_gains:
            st.plotly_chart(_build_gains_fig(pd), width = 'stretch')

        with tab_summary:
            if pd["attempt_summaries"]:
                st.plotly_chart(_build_summary_fig(pd), width = 'stretch')
            else:
                st.info("⏳  Waiting for the first attempt to complete…")

    # -- Auto-rerun while GA is running ----------------------------------------
    run_complete: bool = st.session_state.get("run_complete", False)
    if not run_complete:
        thread = st.session_state.get("run_thread")
        if thread and thread.is_alive():
            time.sleep(0.75)
            st.rerun()
        else:
            # Thread ended but never pushed run_complete (edge-case)
            drain_event_queue()
            st.session_state.run_complete = True
            st.rerun()
    else:
        # Final status message
        err = st.session_state.get("run_error")
        if err:
            st.error(f"❌ Run failed: {err}")
            with st.expander("📋 Traceback"):
                st.code(st.session_state.get("run_error_tb", ""), language="python")
        else:
            # st.success("✅ Optimisation complete!", icon="✅")
            st.session_state["mulo_designer_stage"] = "optimisation_complete"


# -- Internal helpers ----------------------------------------------------------

def _reset_and_go_home() -> None:
    for key in (
        "run_config", "event_queue", "plot_data", "run_thread",
        "run_complete", "final_state", "run_error", "run_error_tb",
    ):
        st.session_state.pop(key, None)
    st.session_state.plot_data = empty_plot_data()
    st.session_state.page = "home"
    st.rerun()


def _render_config_badges() -> None:
    rc = st.session_state.get("run_config", {})
    badges = [
        ("🤖 Model",         rc.get("llm_model", "—")),
        ("🔁 Max Attempts",  str(rc.get("max_attempts", "—"))),
        ("⏱ Wall Clock",    f"{rc.get('max_wall_clock', 0):.0f} s"),
        ("💰 Cost Budget",  f"${rc.get('max_cost_budget', 0):.3f}"),
        ("📝 Variant",       rc.get("prompt_variant", "—")),
    ]
    for col, (label, value) in zip(st.columns(len(badges)), badges):
        col.metric(label, value)


def _render_status_bar(pd: Dict[str, Any]) -> None:
    run_complete: bool = st.session_state.get("run_complete", False)
    err = st.session_state.get("run_error")

    if not run_complete:
        status_html = (
            '<div style="background:#FF9800;color:white;border-radius:6px;'
            'padding:6px 14px;text-align:center;font-weight:600;">🔄  Running…</div>'
        )
    elif err:
        status_html = (
            '<div style="background:#F44336;color:white;border-radius:6px;'
            'padding:6px 14px;text-align:center;font-weight:600;">❌  Failed</div>'
        )
    else:
        status_html = (
            '<div style="background:#4CAF50;color:white;border-radius:6px;'
            'padding:6px 14px;text-align:center;font-weight:600;">✅  Complete</div>'
        )

    nfe   = pd["cumulative_nfe"][-1]   if pd["cumulative_nfe"]   else None
    best  = pd["best_baseline_so_far"][-1] if pd["best_baseline_so_far"] else None
    att   = pd["attempt"][-1]          if pd["attempt"]           else None
    score = pd["success_score"][-1]    if pd["success_score"]     else None

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(status_html, unsafe_allow_html=True)
    c2.metric("Attempt",          att   if att   is not None else "—")
    c3.metric("Cumulative NFE",   f"{nfe:,}" if nfe is not None else "—")
    c4.metric("Best Baseline Cost", f"{best:.4f}" if best is not None else "—")
    c5.metric("Success Score",    f"{score}/100" if score is not None else "—")


# -- Shared plot utilities -----------------------------------------------------

def _attempt_nfe_extents(pd: Dict) -> Dict[int, Dict[str, int]]:
    """Return {attempt_num: {nfe_min, nfe_max}} from the generation series."""
    extents: Dict[int, Dict[str, int]] = {}
    for nfe, att in zip(pd["cumulative_nfe"], pd["attempt"]):
        if att not in extents:
            extents[att] = {"nfe_min": nfe, "nfe_max": nfe}
        else:
            extents[att]["nfe_max"] = max(extents[att]["nfe_max"], nfe)
    return extents


def _add_attempt_vlines(
    fig: go.Figure,
    pd: Dict,
    row: Optional[int] = None,
    col: Optional[int] = None,
) -> None:
    """Overlay dashed grey vertical lines at attempt-transition NFE values."""
    kwargs: Dict[str, Any] = {"line_dash": "dash", "line_color": _GRAY, "opacity": 0.7}
    if row is not None:
        kwargs["row"] = row
    if col is not None:
        kwargs["col"] = col
    for nfe in pd["attempt_boundaries_nfe"]:
        fig.add_vline(x=nfe, **kwargs)


# -- Plot 1 – Best Baseline Cost vs NFE ---------------------------------------

def _build_cost_fig(pd: Dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd["cumulative_nfe"],
        y=pd["best_baseline_so_far"],
        mode="lines",
        name="Best Baseline Cost",
        line=dict(color=_BLUE, width=2.5),
    ))
    # Target threshold
    fig.add_hline(
        y=0, line_dash="dash", line_color=_GREEN, opacity=0.8,
        annotation_text="Target ≤ 0",
        annotation_position="bottom right",
    )
    # Attempt boundaries
    for nfe in pd["attempt_boundaries_nfe"]:
        fig.add_vline(x=nfe, line_dash="dash", line_color=_GRAY, opacity=0.7)

    fig.update_layout(
        title="Best Baseline Cost vs Cumulative NFE",
        xaxis_title="Cumulative NFE",
        yaxis_title="Best Baseline Cost",
        template=_TEMPLATE,
        height=300,
        margin=dict(l=64, r=40, t=52, b=48),
    )
    return fig


# -- Plot 2 – 2×2 Metrics -----------------------------------------------------

def _build_metrics_fig(pd: Dict) -> go.Figure:
    metrics  = ["mse",  "settling_time", "overshoot", "control_effort"]
    labels   = ["MSE",  "Settling Time", "Overshoot", "Control Effort"]
    colors   = [_BLUE,  _ORANGE,         _PURPLE,     _TEAL]
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    case_data = st.session_state.get("run_config", {}).get("case_data", {})
    targets: Dict[str, float] = case_data.get("fixed_targets", {})

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=labels,
        horizontal_spacing=0.10,
        vertical_spacing=0.20,
    )
    for metric, label, color, (r, c) in zip(metrics, labels, colors, positions):
        fig.add_trace(
            go.Scatter(
                x=pd["cumulative_nfe"],
                y=pd[metric],
                mode="lines",
                name=label,
                line=dict(color=color, width=2),
                showlegend=False,
            ),
            row=r, col=c,
        )
        target_val = targets.get(metric)
        if target_val is not None:
            fig.add_hline(
                y=target_val,
                line_dash="dash",
                line_color=_RED,
                opacity=0.75,
                annotation_text=f"Target={target_val}",
                annotation_position="top right",
                row=r, col=c,
            )
        for nfe in pd["attempt_boundaries_nfe"]:
            fig.add_vline(x=nfe, line_dash="dash", line_color=_GRAY,
                          opacity=0.5, row=r, col=c)

    fig.update_layout(
        title="Performance Metrics vs Cumulative NFE",
        template=_TEMPLATE,
        height=480,
        margin=dict(l=64, r=40, t=64, b=52),
    )
    for r, c in positions:
        fig.update_xaxes(title_text="NFE", row=r, col=c)
    return fig


# -- Plot 3 – 1×3 PID Gains with search-range shading -------------------------

def _build_gains_fig(pd: Dict) -> go.Figure:
    gains  = ["Kp",   "Ki",    "Kd"]
    colors = [_BLUE,  _ORANGE, _PURPLE]
    extents = _attempt_nfe_extents(pd)

    fig = make_subplots(rows=1, cols=3, subplot_titles=gains,
                        horizontal_spacing=0.08)

    for gi, (gain, color) in enumerate(zip(gains, colors), 1):
        # Shaded search-range rectangle per attempt
        for att_num, ext in extents.items():
            rng = pd["attempt_ranges"].get(att_num, {}).get(gain)
            if rng:
                lo, hi = rng
                fig.add_shape(
                    type="rect",
                    x0=ext["nfe_min"], x1=ext["nfe_max"],
                    y0=lo,            y1=hi,
                    fillcolor=_RANGE_FILL,
                    line_width=0,
                    row=1, col=gi,
                )
        # Gain trajectory
        fig.add_trace(
            go.Scatter(
                x=pd["cumulative_nfe"],
                y=pd[gain],
                mode="lines",
                name=gain,
                line=dict(color=color, width=2),
                showlegend=False,
            ),
            row=1, col=gi,
        )
        # Attempt boundaries
        for nfe in pd["attempt_boundaries_nfe"]:
            fig.add_vline(x=nfe, line_dash="dash", line_color=_GRAY,
                          opacity=0.55, row=1, col=gi)

    fig.update_layout(
        title="PID Gains vs Cumulative NFE  (shaded region = LLM search range per attempt)",
        template=_TEMPLATE,
        height=300,
        margin=dict(l=64, r=40, t=64, b=52),
    )
    for gi in range(1, 4):
        fig.update_xaxes(title_text="NFE", row=1, col=gi)
    return fig


# -- Plot 4 – 2×4 LLM Decision Summary ----------------------------------------

def _build_summary_fig(pd: Dict) -> go.Figure:
    summaries: List[Dict] = pd["attempt_summaries"]
    if not summaries:
        fig = go.Figure()
        fig.add_annotation(text="No attempt data yet", showarrow=False,
                           font=dict(size=14, color="gray"))
        return fig

    attempts = [s["attempt"] for s in summaries]

    subplot_titles = [
        "GA Config (Pop / Gens)",
        "Weights: MSE & Settling Time",
        "Weights: Overshoot & Ctrl Effort",
        "Budget Remaining (%)",
        "Success Score",
        "Search Range: Kp",
        "Search Range: Ki",
        "Search Range: Kd",
    ]
    fig = make_subplots(
        rows=2, cols=4,
        subplot_titles=subplot_titles,
        horizontal_spacing=0.08,
        vertical_spacing=0.26,
    )

    # -- (1,1) GA Config -------------------------------------------------------
    pops = [s["pop_size"] for s in summaries]
    gens = [s["num_gen"]  for s in summaries]
    fig.add_trace(go.Bar(name="Pop Size", x=attempts, y=pops,
                         marker_color=_BLUE,   showlegend=True,
                         legendgroup="cfg"),    row=1, col=1)
    fig.add_trace(go.Bar(name="Num Gens", x=attempts, y=gens,
                         marker_color=_ORANGE, showlegend=True,
                         legendgroup="cfg"),    row=1, col=1)

    # -- (1,2) Weights MSE & Settling Time -------------------------------------
    w_mse = [s["weights"].get("mse",           0) for s in summaries]
    w_st  = [s["weights"].get("settling_time", 0) for s in summaries]
    fig.add_trace(go.Bar(name="W-MSE", x=attempts, y=w_mse,
                         marker_color=_BLUE,   showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(name="W-ST",  x=attempts, y=w_st,
                         marker_color=_ORANGE, showlegend=False), row=1, col=2)

    # -- (1,3) Weights Overshoot & Control Effort ------------------------------
    w_os = [s["weights"].get("overshoot",      0) for s in summaries]
    w_ce = [s["weights"].get("control_effort", 0) for s in summaries]
    fig.add_trace(go.Bar(name="W-OS", x=attempts, y=w_os,
                         marker_color=_PURPLE, showlegend=False), row=1, col=3)
    fig.add_trace(go.Bar(name="W-CE", x=attempts, y=w_ce,
                         marker_color=_TEAL,   showlegend=False), row=1, col=3)

    # -- (1,4) Budget Remaining (%) --------------------------------------------
    t_pct = [s.get("time_remaining_pct", 0) for s in summaries]
    c_pct = [s.get("cost_remaining_pct", 0) for s in summaries]
    fig.add_trace(go.Scatter(name="Time %", x=attempts, y=t_pct,
                             mode="lines+markers",
                             line=dict(color=_BLUE),
                             showlegend=True, legendgroup="budget"),
                  row=1, col=4)
    fig.add_trace(go.Scatter(name="Cost %", x=attempts, y=c_pct,
                             mode="lines+markers",
                             line=dict(color=_RED, dash="dot"),
                             showlegend=True, legendgroup="budget"),
                  row=1, col=4)
    fig.update_yaxes(range=[0, 105], row=1, col=4)

    # -- (2,1) Success Score ---------------------------------------------------
    scores = [s.get("success_score", 0) for s in summaries]
    bar_colors = [
        _GREEN if sc == 100 else (_ORANGE if sc >= 50 else _RED)
        for sc in scores
    ]
    fig.add_trace(go.Bar(name="Score", x=attempts, y=scores,
                         marker_color=bar_colors, showlegend=False),
                  row=2, col=1)
    fig.add_hline(y=100, line_dash="dash", line_color=_GREEN,
                  opacity=0.6, row=2, col=1)
    fig.update_yaxes(range=[0, 110], row=2, col=1)

    # -- (2,2–4) Gain search-ranges --------------------------------------------
    for gi, gain in enumerate(["Kp", "Ki", "Kd"], 2):
        for s in summaries:
            att  = s["attempt"]
            rng  = s.get("param_ranges", {}).get(gain)
            if rng is None:
                continue
            lo, hi    = rng
            final_val = s.get("controller_gains", {}).get(gain, (lo + hi) / 2)

            # Thick vertical "bar" from lo→hi represents the search range
            fig.add_trace(
                go.Scatter(
                    x=[att, att], y=[lo, hi],
                    mode="lines",
                    line=dict(color="rgba(33,150,243,0.40)", width=12),
                    showlegend=False,
                ),
                row=2, col=gi,
            )
            # Diamond marker at final obtained gain
            fig.add_trace(
                go.Scatter(
                    x=[att], y=[final_val],
                    mode="markers",
                    marker=dict(size=11, color=_RED, symbol="diamond"),
                    showlegend=False,
                ),
                row=2, col=gi,
            )

    # -- Layout ----------------------------------------------------------------
    fig.update_layout(
        title="LLM Decision Summary per Attempt",
        barmode="group",
        template=_TEMPLATE,
        height=580,
        margin=dict(l=64, r=40, t=80, b=52),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.04,
            xanchor="right",  x=1,
        ),
    )
    for r in range(1, 3):
        for c in range(1, 5):
            fig.update_xaxes(title_text="Attempt", dtick=1, row=r, col=c)

    return fig
