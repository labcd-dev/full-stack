"""
PDF Report Generator for System Trimming Results

Generates professional, journal-grade academic publication reports with automatic
section numbering, table rules, and robust math notation translation.
"""

import numpy as np
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# Greek letter mapping for sanitization
GREEK_TO_ENGLISH = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa",
    "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "ο": "omicron",
    "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "υ": "upsilon",
    "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    "Î±": "alpha", "Î²": "beta", "Î³": "gamma", "Î´": "delta", "Îµ": "epsilon",
    "Î¶": "zeta", "Î·": "eta", "Î¸": "theta", "Î¹": "iota", "Îº": "kappa",
    "Î»": "lambda", "Î¼": "mu", "Î½": "nu", "Î¾": "xi", "Î¿": "omicron",
    "Ï€": "pi", "Ï": "rho", "Ïƒ": "sigma", "Ï„": "tau", "Ï…": "upsilon",
    "Ï†": "phi", "Ï‡": "chi", "Ïˆ": "psi", "Ï‰": "omega"
}

# Scientific & Math Unicode mapping to prevent any "?" signs
UNICODE_TO_ASCII = {
    # Non-breaking hyphens and typographical dashes (Fixes Thermal‑Mechanical)
    "‑": "-", "–": "-", "—": "-", "\u00A0": " ",
    # Smart quotes
    "‘": "'", "’": "'", "“": '"', "”": '"',
    # Superscripts (Fixes m³, 10⁶, 10⁻⁴)
    "⁰": "^0", "¹": "^1", "²": "^2", "³": "^3", "⁴": "^4",
    "⁵": "^5", "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9",
    "⁺": "^+", "⁻": "^-", "ⁿ": "^n",
    # Subscripts (Fixes I₃, 0₃×₁)
    "₀": "_0", "₁": "_1", "₂": "_2", "₃": "_3", "₄": "_4",
    "₅": "_5", "₆": "_6", "₇": "_7", "₈": "_8", "₉": "_9",
    # Differential overdots / calculus notations (Fixes ẋ1, ẋ2, ẋ3)
    "ẋ": "x_dot", "ẏ": "y_dot", "ż": "z_dot",
    # Mathematical operators
    "±": "+/-", "×": "x", "÷": "/", "≈": "~=", "≠": "!=",
    "≤": "<=", "≥": ">=", "·": "*", "√": "sqrt", "∞": "inf"
}


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to compute total page count and draw academic headers/footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.HexColor("#444444"))

        # Running Academic Header (Skipped on Cover/Page 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "TECHNICAL MANUSCRIPT: THERMAL-MECHANICAL SYSTEM ANALYSIS & CONTROL")
            self.setStrokeColor(colors.HexColor("#BBBBBB"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Running Academic Footer (All pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential - Automated Computational Engineering Core")
        self.setStrokeColor(colors.HexColor("#BBBBBB"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)

        self.restoreState()


def sanitize_text(text):
    """Replace Greek letters, math symbols, and problematic characters with clean ASCII equivalents."""
    if not isinstance(text, str):
        text = str(text)

    # 1. Map Greek Letters
    for greek, english in GREEK_TO_ENGLISH.items():
        text = text.replace(greek, english)

    # 2. Map Scientific Unicode Math/Hyphens
    for unicode_char, ascii_rep in UNICODE_TO_ASCII.items():
        text = text.replace(unicode_char, ascii_rep)

    # 3. Graceful degradation: Encode using 'ignore' to completely avoid any visual '?'
    return text.encode('ascii', 'ignore').decode('ascii')


def format_llm_text(text):
    """Sanitize and format LLM output for reportlab by converting newlines to <br/>."""
    if not text:
        return ""
    safe_text = sanitize_text(text)
    return safe_text.replace('\n', '<br/>')


def format_number(value, precision=6):
    """Format a numeric value with specified precision."""
    try:
        if isinstance(value, complex):
            real = value.real
            imag = value.imag
            if abs(imag) < 1e-10:
                return f"{real:.{precision}f}"
            sign = "+" if imag >= 0 else "-"
            return f"{real:.{precision}f} {sign} {abs(imag):.{precision}f}j"
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return str(value)


def format_matrix_for_table(matrix, max_cols=5, precision=2):
    """Convert a matrix to a list of formatted string rows for table display."""
    if matrix is None:
        return None
    try:
        matrix = np.array(matrix)
    except (TypeError, ValueError):
        return None

    rows, cols = matrix.shape if len(matrix.shape) == 2 else (1, len(matrix))
    if len(matrix.shape) == 1:
        matrix = matrix.reshape(1, -1)

    formatted_rows = []
    for row in matrix:
        formatted_row = [format_number(val, precision) for val in row]
        formatted_rows.append(formatted_row)
    return formatted_rows


# =============================================================================
# 📊 FIX 2: DISTINCT STYLE FOR MATRICES AND VECTORS (Math Bracket Notation)
# =============================================================================
def create_matrix_table(matrix_data, styles, col_width=None):
    """Create a matrix block styled with mathematical left/right brackets."""
    if not matrix_data:
        return Paragraph("Not available", styles['Normal'])

    num_cols = len(matrix_data[0]) if matrix_data else 0
    if col_width is None:
        available_width = 6.5 * inch
        col_width = min(available_width / max(num_cols, 1), 1.2 * inch)

    table = Table(matrix_data, colWidths=[col_width] * num_cols)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        # Distinct layout: No inner grids, just strong outer left and right vertical bounds
        ('LINEBEFORE', (0, 0), (0, -1), 1.5, colors.black),  # Left matrix bracket
        ('LINEAFTER', (-1, 0), (-1, -1), 1.5, colors.black), # Right matrix bracket
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


# =============================================================================
# 📋 FIX 1: REGULAR TABLE STYLE MATCHING THE IMAGE (Clean Boxed Grid)
# =============================================================================
def create_key_value_table(data, styles):
    """Create a table for key-value pairs matching the requested image grid style."""
    if not data:
        return None

    table_data = [[sanitize_text(str(k)), sanitize_text(str(v))] for k, v in data]
    table = Table(table_data, colWidths=[2.5 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        # Clean plain line grid matching user's image snippet
        ('GRID', (0, 0), (-1, -1), 0.75, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


def putting_long_string_on_two_line(original_input):
    original_input = list(str(original_input))
    enhanced_input = ""
    for idx, ch in enumerate(original_input):
        enhanced_input += str(ch)
        if idx % 43 == 0 and idx != 0:
            enhanced_input += "\n"  # or maybe "\\n" if literal '\n' is needed
    return str(enhanced_input)


def generate_pdf_report(result, config, controller_graph, response_graph=None, output_path=None, narratives=None):
    """Generate a highly professional, academic-grade scientific PDF report."""
    if narratives is None:
        narratives = {}

    if output_path is None:
        system_name = config.get("system_name", "system")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in system_name)
        safe_name = safe_name.strip("_").lower() or "system"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{safe_name}_report_{timestamp}.pdf"

    # Strict academic margins
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch
    )

    styles = getSampleStyleSheet()

    # Academic Typography Definitions (Times-Roman Core)
    styles.add(ParagraphStyle(name='ReportTitle', fontName='Times-Bold', fontSize=20, leading=24, spaceAfter=8,
                              alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='AuthorBlock', fontName='Times-Roman', fontSize=10, leading=14, spaceAfter=22,
                              alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='SectionHeader', fontName='Times-Bold', fontSize=13, leading=16, spaceBefore=18,
                              spaceAfter=8, textColor=colors.black))
    styles.add(ParagraphStyle(name='SubSection', fontName='Times-BoldItalic', fontSize=11, leading=14, spaceBefore=12,
                              spaceAfter=6, textColor=colors.black))
    styles.add(ParagraphStyle(name='InfoText', fontName='Times-Roman', fontSize=10, leading=14, spaceAfter=4))
    styles.add(ParagraphStyle(name='NarrativeText', fontName='Times-Roman', fontSize=10, leading=14, spaceBefore=4,
                              spaceAfter=10, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='AbstractText', fontName='Times-Roman', fontSize=10, leading=14, leftIndent=24,
                              rightIndent=24, spaceAfter=20, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='CaptionStyle', fontName='Times-Italic', fontSize=9, leading=12, spaceBefore=6,
                              spaceAfter=6, alignment=TA_CENTER))

    story = []

    # Dynamic Automatic Indexing Closures
    section_idx = 0

    def next_section(title_text):
        nonlocal section_idx
        section_idx += 1
        return f"{section_idx}. {title_text}"

    table_idx = 0

    def next_table_caption(caption_text):
        nonlocal table_idx
        table_idx += 1
        return f"Table {table_idx}: {caption_text}."

    figure_idx = 0

    def next_figure_caption(caption_text):
        nonlocal figure_idx
        figure_idx += 1
        return f"Fig. {figure_idx}. {caption_text}."

    system = result.get("system", {})
    equilibrium = result.get("equilibrium", {})
    linearized = result.get("linearized", {})
    stability = result.get("stability", {})
    diagnostics = result.get("diagnostics", {})
    system_name = sanitize_text(config.get("system_name", "Unknown System"))
    state_vars = [sanitize_text(v) for v in system.get("state_variables", [])]
    input_vars = [sanitize_text(v) for v in system.get("input_variables", [])]

    # ==========================================================================
    # Document Header & Title Section
    # ==========================================================================
    story.append(Paragraph(f"System Trimming and Dynamic Stability Report: {system_name}", styles['ReportTitle']))

    author_html = (
        "<b>Automated Core Engineering Analysis Engine</b><br/>"
        "Department of Aerospace & Computational Engineering Systems<br/>"
        f"<i>Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
    )
    story.append(Paragraph(author_html, styles['AuthorBlock']))

    # Journal style Bold-Italic Abstract block
    if narratives.get('executive_summary'):
        abstract_body = format_llm_text(narratives['executive_summary'])
        story.append(Paragraph(f"<b><i>Abstract</i>—{abstract_body}</b>", styles['AbstractText']))

    # ==========================================================================
    # Section 1: System Information
    # ==========================================================================
    story.append(Paragraph(next_section("System Structure & Parameterization"), styles['SectionHeader']))
    if narratives.get('system_intro'):
        story.append(Paragraph(format_llm_text(narratives['system_intro']), styles['NarrativeText']))

    sys_info = [
        ("Number of States (n_states)", system.get("n_states", "N/A")),
        ("Number of Inputs (n_inputs)", system.get("n_inputs", "N/A")),
        ("State Space Vector Variables", ", ".join(state_vars) if state_vars else "N/A"),
        ("Control Input Vector Variables", ", ".join(input_vars) if input_vars else "N/A"),
    ]
    if "operating_conditions" in config:
        operating_conditions = putting_long_string_on_two_line(config["operating_conditions"])
        sys_info.append(("Operating Boundary Thresholds", sanitize_text(operating_conditions)))
    if "params" in config:
        params = putting_long_string_on_two_line(config["params"])
        sys_info.append(("Assigned Physical Parameters", sanitize_text(params)))

    table = create_key_value_table(sys_info, styles)
    if table:
        # Academic standard: Table captions are placed ABOVE the data element
        story.append(Paragraph(next_table_caption("System specifications, structural dimensions, and state bounds"),
                               styles['CaptionStyle']))
        story.append(table)
    story.append(Spacer(1, 15))

    # ==========================================================================
    # Section 2: Equilibrium (Trim Point)
    # ==========================================================================
    story.append(Paragraph(next_section("Equilibrium & Static Trim Analysis"), styles['SectionHeader']))
    if narratives.get('equilibrium_analysis'):
        story.append(Paragraph(format_llm_text(narratives['equilibrium_analysis']), styles['NarrativeText']))

    x_e = equilibrium.get("x_e")
    u_e = equilibrium.get("u_e")

    if x_e:
        story.append(Paragraph(f"{section_idx}.1 State Vector Steady-State Trim Equilibrium", styles['SubSection']))
        eq_data = list(zip(state_vars, x_e)) if state_vars else [(f"x[{i}]", v) for i, v in enumerate(x_e)]
        eq_table_data = [[sanitize_text(var), format_number(val, 6)] for var, val in eq_data]
        eq_table = Table(eq_table_data, colWidths=[2.5 * inch, 3.5 * inch])
        eq_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(Paragraph(next_table_caption("Converged state equilibrium vector evaluations (x_e)"),
                               styles['CaptionStyle']))
        story.append(eq_table)
        story.append(Spacer(1, 10))

    if u_e:
        story.append(Paragraph(f"{section_idx}.2 Control Actuation Equilibrium Input", styles['SubSection']))
        ueq_data = list(zip(input_vars, u_e)) if input_vars else [(f"u[{i}]", v) for i, v in enumerate(u_e)]
        ueq_table_data = [[sanitize_text(var), format_number(val, 6)] for var, val in ueq_data]
        ueq_table = Table(ueq_table_data, colWidths=[2.5 * inch, 3.5 * inch])
        ueq_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(
            Paragraph(next_table_caption("Sustaining input equilibrium vector values (u_e)"), styles['CaptionStyle']))
        story.append(ueq_table)

    story.append(Spacer(1, 15))

    # ==========================================================================
    # Section 3: Linearized Model Matrices
    # ==========================================================================
    story.append(Paragraph(next_section("Small-Signal Linearized State-Space Formulation"), styles['SectionHeader']))
    if narratives.get('linearization_analysis'):
        story.append(Paragraph(format_llm_text(narratives['linearization_analysis']), styles['NarrativeText']))

    matrices = [
        ("System State Transition Matrix (A)", linearized.get("A")),
        ("Control Input Coupling Matrix (B)", linearized.get("B")),
        ("State Matrix Output Mapping (C)", linearized.get("C")),
        ("Direct Input Feedthrough Matrix (D)", linearized.get("D")),
    ]
    for name, matrix in matrices:
        matrix_data = format_matrix_for_table(matrix, precision=4)
        if matrix_data:
            matrix_table = create_matrix_table(matrix_data, styles)
            story.append(Paragraph(next_table_caption(f"Linearized space component: {name}"), styles['CaptionStyle']))
            if len(matrix_data) <= 6:
                story.append(KeepTogether([matrix_table]))
            else:
                story.append(matrix_table)
        else:
            story.append(Paragraph(f"Matrix {name} not available", styles['InfoText']))
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 10))

    # ==========================================================================
    # Section 4: Stability Analysis
    # ==========================================================================
    story.append(Paragraph(next_section("Dynamic Stability & Eigenvalue Assessment"), styles['SectionHeader']))
    if narratives.get('stability_analysis'):
        story.append(Paragraph(format_llm_text(narratives['stability_analysis']), styles['NarrativeText']))

    classification = stability.get("classification", "N/A")
    story.append(
        Paragraph(f"<b>System Characterization Profile:</b> {sanitize_text(classification)}", styles['InfoText']))
    story.append(Spacer(1, 8))

    eigenvalues = stability.get("eigenvalues", [])
    if eigenvalues:
        story.append(Paragraph(f"{section_idx}.1 Pole-Zero Configuration Modality", styles['SubSection']))
        pole_data = []
        for idx, ev in enumerate(eigenvalues):
            label = f"Pole {idx + 1}"
            try:
                if isinstance(ev, complex):
                    value_str = f"{ev.real:.4f} + {ev.imag:.4f}j"
                    mag_str = f"{abs(ev):.4f}"
                elif isinstance(ev, (int, float)):
                    value_str = f"{float(ev):.4f}"
                    mag_str = f"{abs(float(ev)):.4f}"
                else:
                    ev_val = complex(str(ev).replace(' ', ''))
                    value_str = f"{ev_val.real:.4f} + {ev_val.imag:.4f}j" if ev_val.imag else f"{ev_val.real:.4f}"
                    mag_str = f"{abs(ev_val):.4f}"
            except (TypeError, ValueError):
                value_str = sanitize_text(str(ev))
                mag_str = "N/A"
            pole_data.append([label, value_str, mag_str])

        pole_table = Table([["Pole Index", "Complex Numerical Value", "Absolute Magnitude |λ|"]] + pole_data,
                           colWidths=[1.5 * inch, 3.2 * inch, 1.8 * inch])
        pole_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(
            Paragraph(next_table_caption("Computed system poles and corresponding frequency spectrum properties"),
                      styles['CaptionStyle']))
        story.append(pole_table)

    story.append(Spacer(1, 15))

    # ==========================================================================
    # Section 5: Diagnostics
    # ==========================================================================
    story.append(Paragraph(next_section("Trimming Optimization Solver Diagnostics"), styles['SectionHeader']))

    diag_items = []
    if "converged" in diagnostics:
        diag_items.append(
            ("Numerical Convergence Status", "Succeeded / Verified" if diagnostics["converged"] else "Failed"))
    if "feasible" in diagnostics:
        diag_items.append(
            ("Feasibility Check", "Feasible Zone" if diagnostics["feasible"] else "Violated"))
    if "timestamp" in diagnostics:
        diag_items.append(("Execution Timestamp", sanitize_text(str(diagnostics["timestamp"]))))
    if "iterations" in diagnostics:
        diag_items.append(("Numerical Solver Step Iterations", str(diagnostics["iterations"])))
    if "residual" in diagnostics:
        diag_items.append(("Objective Boundary Residual Loss", format_number(diagnostics["residual"], 8)))

    if diag_items:
        diag_table = create_key_value_table(diag_items, styles)
        story.append(Paragraph(
            next_table_caption("Optimization diagnostics, mathematical residuals, and solver step parameters"),
            styles['CaptionStyle']))
        story.append(diag_table)
    else:
        story.append(Paragraph("No optimization diagnostic records provided.", styles['InfoText']))

    # ==========================================================================
    # Section 6: Performance Analysis
    # ==========================================================================
    visualizations = [("Closed-Loop Time Response Simulation", response_graph)]

    has_visuals = any(path and os.path.exists(path) for _, path in visualizations)
    if has_visuals:
        story.append(PageBreak())
        story.append(Paragraph(next_section("Closed-Loop Transient Performance Analysis"), styles['SectionHeader']))

        if narratives.get('performance_analysis'):
            story.append(Paragraph(format_llm_text(narratives['performance_analysis']), styles['NarrativeText']))
            story.append(Spacer(1, 10))

        for title, img_path in visualizations:
            if img_path and os.path.exists(img_path):
                story.append(Paragraph(f"Transient Evaluation: {title}", styles['SubSection']))
                try:
                    from reportlab.lib.utils import ImageReader
                    img_reader = ImageReader(img_path)
                    orig_w, orig_h = img_reader.getSize()

                    max_width = 6.5 * inch
                    scale_factor = min(max_width / orig_w, 1.0)
                    render_w = orig_w * scale_factor
                    render_h = orig_h * scale_factor

                    if render_h > 4.5 * inch:
                        scale_factor = (4.5 * inch) / render_h
                        render_w *= scale_factor
                        render_h *= scale_factor

                    img_flowable = Image(img_path, width=render_w, height=render_h)
                    img_flowable.hAlign = 'CENTER'

                    # Academic standard: Figure captions are placed BELOW the graphic elements
                    story.append(KeepTogether([
                        img_flowable,
                        Spacer(1, 4),
                        Paragraph(next_figure_caption(f"Time-domain simulation response mapping for {title}"),
                                  styles['CaptionStyle']),
                        Spacer(1, 15)
                    ]))
                except Exception as img_err:
                    story.append(Paragraph(f"<i>Error rendering response visualization matrix: {img_err}</i>",
                                           styles['InfoText']))
                    story.append(Spacer(1, 10))

    # ==========================================================================
    # Section 7: Controller Loop Architecture
    # ==========================================================================
    visualizations = []
    for title, img_path in controller_graph.items():
        visualizations.append((title, img_path))

    has_visuals = any(path and os.path.exists(path) for _, path in visualizations)
    if has_visuals:
        story.append(PageBreak())
        story.append(
            Paragraph(next_section("Cascaded Control Architecture Optimization Design"), styles['SectionHeader']))

        if narratives.get('controller_architecture'):
            story.append(Paragraph(format_llm_text(narratives['controller_architecture']), styles['NarrativeText']))
            story.append(Spacer(1, 10))

        for title, img_path in visualizations:
            if img_path and os.path.exists(img_path):
                story.append(Paragraph(f"Architecture Schematic: {title}", styles['SubSection']))
                try:
                    from reportlab.lib.utils import ImageReader
                    img_reader = ImageReader(img_path)
                    orig_w, orig_h = img_reader.getSize()

                    max_width = 6.5 * inch
                    scale_factor = min(max_width / orig_w, 1.0)
                    render_w = orig_w * scale_factor
                    render_h = orig_h * scale_factor

                    if render_h > 4.5 * inch:
                        scale_factor = (4.5 * inch) / render_h
                        render_w *= scale_factor
                        render_h *= scale_factor

                    img_flowable = Image(img_path, width=render_w, height=render_h)
                    img_flowable.hAlign = 'CENTER'

                    # Academic standard: Figure captions are placed BELOW the graphic elements
                    story.append(KeepTogether([
                        img_flowable,
                        Spacer(1, 4),
                        Paragraph(next_figure_caption(f"Control loop signal path block schematic layout: {title}"),
                                  styles['CaptionStyle']),
                        Spacer(1, 15)
                    ]))
                except Exception as img_err:
                    story.append(Paragraph(f"<i>Error embedding controller architectural graph: {img_err}</i>",
                                           styles['InfoText']))
                    story.append(Spacer(1, 10))

    # ==========================================================================
    # Section 8: Conclusion
    # ==========================================================================
    if narratives.get('conclusion'):
        story.append(Spacer(1, 15))
        story.append(Paragraph(next_section("Concluding Remarks and Verification Syntheses"), styles['SectionHeader']))
        story.append(Paragraph(format_llm_text(narratives['conclusion']), styles['NarrativeText']))

    # ==========================================================================
    # Build PDF with dynamic dynamic total-page calculation canvas
    # ==========================================================================
    try:
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"Academic PDF technical report successfully saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error compiling academic PDF report: {e}")
        raise


def generate_simple_report(result, config, output_path):
    """Alias for generate_pdf_report for backwards compatibility."""
    return generate_pdf_report(result, config, output_path=output_path)