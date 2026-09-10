"""
Generates a docx listing the advantages and disadvantages of the project:
"A Fuzzy Inference System for Real-Time Water Potability Classification"

Run from project root: python docs/generate_pros_cons.py
Output: outputs/Advantages_Disadvantages.docx
"""
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Calibri"
GREEN = RGBColor(0x1E, 0x7A, 0x34)
RED = RGBColor(0xB4, 0x23, 0x23)


def set_font(run, size=11, bold=False, italic=False, name=FONT, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = name
    if color:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rFonts = rpr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rpr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), name)


def add_heading(doc, text, level=1, size=None, center=False, color=None):
    h = doc.add_heading(level=level)
    r = h.add_run(text)
    set_font(r, size=size or {1: 16, 2: 13.5, 3: 12}.get(level, 12), bold=True, color=color)
    if center:
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    return h


def add_para(doc, text, size=11, bold=False, italic=False, center=False, justify=True, space_after=8):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_font(r, size=size, bold=bold, italic=italic)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.2
    return p


def add_point(doc, bold_lead, rest, size=10.7, mark="+", mark_color=GREEN):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.15
    r0 = p.add_run(f"{mark}  ")
    set_font(r0, size=size, bold=True, color=mark_color)
    r1 = p.add_run(f"{bold_lead} ")
    set_font(r1, size=size, bold=True)
    r2 = p.add_run(rest)
    set_font(r2, size=size)
    return p


def add_table(doc, rows, col_widths=None, caption=None, fontsize=9.5):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(val))
            set_font(run, size=fontsize, bold=(r_idx == 0))
            if col_widths:
                cell.width = Inches(col_widths[c_idx])
    if caption:
        p = doc.add_paragraph()
        r = p.add_run(caption)
        set_font(r, size=9.5, italic=True)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(16)
        p.paragraph_format.space_before = Pt(4)
    else:
        add_para(doc, "", space_after=10)
    return t


def create_pros_cons():
    doc = Document()
    section = doc.sections[0]
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    title = doc.add_heading(level=0)
    tr = title.add_run("Advantages and Disadvantages")
    set_font(tr, size=20, bold=True)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_para(doc, "A Fuzzy Inference System for Real-Time Water Potability Classification "
                   "from Low-Cost Multi-Sensor Data", size=12.5, italic=True, center=True, space_after=20)

    add_para(doc, "This document sets out, honestly and without overselling, what the project's design "
                   "gains by using a WHO/BIS-grounded Mamdani Fuzzy Inference System (FIS) instead of a "
                   "hard-threshold classifier or a black-box machine-learning model, and what it gives up "
                   "in exchange. The points below are grouped by theme and are drawn directly from the "
                   "system's actual design and the benchmark results already gathered for this project, "
                   "rather than from generic fuzzy-logic literature.", italic=True, space_after=20)

    # ══════════════════════════════════════════════════════════════
    add_heading(doc, "Advantages", level=1, color=GREEN)

    add_heading(doc, "1. Interpretability & Trust", level=2)
    add_point(doc, "Fully traceable decisions —",
              "every one of the 45 rules in the rule base is written as a human-readable IF-THEN "
              "statement and is derived from a specific WHO (2022) or BIS IS 10500:2012 limit, so any "
              "classification can be explained by naming the exact rule(s) that fired, unlike Random "
              "Forest, KNN or SVM, none of which offer this natively.")
    add_point(doc, "No cliff-edge boundaries —",
              "overlapping membership functions mean a reading just inside a safe limit and a reading "
              "just outside it produce a smoothly graded output rather than a sudden binary flip, which "
              "better reflects the physical reality that water quality degrades gradually.")
    add_point(doc, "Visible reasoning in real time —",
              "the dashboard's “active rules” panel and live membership-degree charts let an operator "
              "see, moment to moment, not just what the system decided but why — a transparency property "
              "no black-box model in the comparison provides.")

    add_heading(doc, "2. Technical Performance", level=2)
    add_point(doc, "Zero-shot, no training data required —",
              "the rule base is authored directly from published standards, so the system works on day "
              "one without needing a labelled training set for the specific deployment context, unlike "
              "the ML baselines, which must be trained (or retrained) on representative labelled data.")
    add_point(doc, "Competitive on real-world data —",
              "on the independent Kaggle water-potability dataset, the FIS reached 60.43% accuracy, ahead "
              "of Random Forest (59.61%) and KNN (54.40%) and only just behind SVM (61.22%) — despite "
              "having never seen that dataset's labels, unlike the three ML models that were trained "
              "directly on it.")
    add_point(doc, "Joint, multi-parameter reasoning —",
              "rules combine several sensors at once (e.g. turbidity, TDS and DO together), so the system "
              "can flag water as unsafe due to a combination of moderately elevated parameters, not only "
              "due to any single reading crossing a limit.")
    add_point(doc, "Fast enough for live use —",
              "centroid-of-area defuzzification over a 1,000-point discretization completes well within "
              "the project's roughly 1 Hz sensor sampling rate, so the dashboard updates in real time "
              "without any perceptible inference lag.")

    add_heading(doc, "3. Cost & Deployability", level=2)
    add_point(doc, "Low hardware cost —",
              "the full sensor array (pH, turbidity, TDS, DO, temperature) totals roughly ₹5,350, orders "
              "of magnitude cheaper than laboratory-grade water-testing instrumentation.")
    add_point(doc, "No cloud or GPU dependency —",
              "inference runs on ordinary CPU hardware; an ESP32 microcontroller handles signal "
              "acquisition, so the system does not depend on an internet connection or paid inference "
              "service to operate.")
    add_point(doc, "Physically grounded corrections included —",
              "temperature-compensation formulas for pH (Nernstian drift) and dissolved oxygen "
              "(Benson-Krause saturation) are built into preprocessing, improving reading fidelity without "
              "any extra hardware cost.")

    add_heading(doc, "4. Usability", level=2)
    add_point(doc, "Complete real-time dashboard —",
              "live gauges, sensor cards, trend charts, membership visualizations, a manual slider-driven "
              "inference mode and six demonstration scenarios make the system usable and demonstrable "
              "even without live hardware connected.")

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════
    add_heading(doc, "Disadvantages / Limitations", level=1, color=RED)

    add_heading(doc, "1. Accuracy Trade-off", level=2)
    add_point(doc, "Lower raw accuracy than trained ML models —",
              "on the synthetic, oracle-labelled dataset the FIS reached 75.3% accuracy versus 99.5% for "
              "Random Forest, 95.7% for SVM and 92.3% for KNN. This gap is structural: the ML models were "
              "trained directly against the same hard-threshold oracle used to generate the labels, so "
              "they can effectively memorize its exact boundaries, while the FIS deliberately does not "
              "reproduce them exactly.", mark="-", mark_color=RED)
    add_point(doc, "Uneven per-class performance on real data —",
              "despite a competitive 60.43% accuracy on the Kaggle dataset, the FIS's macro-F1 there is "
              "only 37.67%, well below Random Forest (46.20%) and KNN (49.40%). Accuracy alone hides this: "
              "the FIS is comparatively weak on at least one class in real-world conditions.", mark="-", mark_color=RED)
    add_point(doc, "Deliberately conservative bias —",
              "the FIS achieves perfect recall (1.00) on the NON-POTABLE class but only 0.59 precision on "
              "the POTABLE class in the synthetic benchmark, meaning it is more prone to flagging "
              "genuinely safe water as marginal than the ML baselines are.", mark="-", mark_color=RED)

    add_heading(doc, "2. Design & Maintenance Burden", level=2)
    add_point(doc, "Manually authored rule base —",
              "all 45 rules were hand-written from domain standards rather than learned automatically, "
              "so there is no formal guarantee of completeness or consistency; input combinations not "
              "explicitly anticipated by a rule author could fall into gaps in rule coverage.", mark="-", mark_color=RED)
    add_point(doc, "Hand-tuned membership functions —",
              "the breakpoints of each membership function are reasoned approximations of WHO/BIS limits, "
              "not fitted to measured data, so they may not be optimally calibrated for a specific real "
              "deployment site without manual re-tuning.", mark="-", mark_color=RED)
    add_point(doc, "No automatic learning from new data —",
              "unlike the ML baselines, the FIS cannot improve itself as more field data becomes "
              "available; any correction requires a person to edit the rule base or membership functions "
              "directly.", mark="-", mark_color=RED)

    add_heading(doc, "3. Validation Gaps", level=2)
    add_point(doc, "No field validation yet —",
              "the system has been evaluated only on a self-generated synthetic dataset and one public "
              "Kaggle dataset; it has not yet been tested against real physical water samples or "
              "cross-checked against expert human assessments in the field.", mark="-", mark_color=RED)
    add_point(doc, "Benchmark asymmetry —",
              "on the synthetic dataset, the FIS (which needs no training) was evaluated on the full "
              "5,000-sample set while the ML models were evaluated only on a held-out 20% test split, so "
              "the headline numbers are not a perfectly like-for-like comparison.", mark="-", mark_color=RED)

    add_heading(doc, "4. Hardware & Deployment Limitations", level=2)
    add_point(doc, "Low-cost sensor drift and durability —",
              "the DFRobot Gravity-series sensors used are not laboratory-grade; they are expected to "
              "need periodic recalibration in real deployments, a process not yet demonstrated in this "
              "project.", mark="-", mark_color=RED)
    add_point(doc, "Partial temperature compensation —",
              "temperature correction is currently applied only to the pH and dissolved-oxygen readings; "
              "the turbidity and TDS sensors are not compensated, even though both can be somewhat "
              "temperature-sensitive in practice.", mark="-", mark_color=RED)
    add_point(doc, "Host-computer dependency —",
              "in the current implementation, the ESP32 handles only signal acquisition, while "
              "preprocessing and FIS inference run on a separate host computer; a fully standalone, "
              "edge-only deployment has not yet been realized.", mark="-", mark_color=RED)
    add_point(doc, "Single-point sensing —",
              "the system monitors one physical location at a time, with only a 60-second rolling trend "
              "window; it does not yet aggregate readings across multiple monitoring points or perform "
              "longer-horizon historical trend analysis.", mark="-", mark_color=RED)

    add_heading(doc, "5. Computational Overhead", level=2)
    add_point(doc, "Heavier defuzzification —",
              "centroid-of-area defuzzification requires numerical integration over a discretized output "
              "range on every inference cycle, which is more computationally demanding than simpler "
              "defuzzification schemes (e.g. a Sugeno-style weighted average) — a non-issue at the "
              "project's ~1 Hz sampling rate, but a consideration if the sampling rate were increased "
              "substantially.", mark="-", mark_color=RED)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════
    add_heading(doc, "Summary Comparison", level=1)
    add_table(doc, [
        ["Aspect", "Advantage", "Disadvantage"],
        ["Interpretability", "Every decision traceable to a named, standards-grounded rule",
         "Rule base is manually authored; no formal coverage guarantee"],
        ["Accuracy (synthetic data)", "Reasonable at 75.3%",
         "Well below RF/SVM/KNN (92-99.5%), which were fit to the labelling oracle"],
        ["Accuracy (real-world Kaggle data)", "Best-or-near-best of the 4 methods (60.43%)",
         "Macro-F1 is comparatively low (37.67%), showing class imbalance in performance"],
        ["Cost", "~Rs. 5,350 total hardware, no cloud/GPU needed", "Low-cost sensors drift and need recalibration"],
        ["Adaptability", "Works zero-shot with no training data", "Cannot self-improve from new field data"],
        ["Real-time capability", "Fast enough at ~1 Hz for a live dashboard", "Defuzzification is heavier than simpler methods"],
        ["Deployment maturity", "Full working prototype with live dashboard",
         "Not yet field-validated; still host-computer-dependent"],
    ], col_widths=[1.6, 2.5, 2.5], caption="Table 1. Advantages and disadvantages by aspect.")

    add_heading(doc, "Overall Assessment", level=1)
    add_para(doc, "On balance, the project's central design bet — trading a measurable amount of raw "
                   "classification accuracy for full rule-level interpretability and standards "
                   "traceability — is defensible specifically because water potability is a safety- and "
                   "trust-sensitive decision, where being able to justify a verdict matters as much as the "
                   "verdict's raw accuracy. That said, the limitations above are real and unresolved: the "
                   "rule base and membership functions have not been tuned or validated against real field "
                   "data or expert assessment, the sensors' long-term reliability is untested, and the "
                   "system is not yet a standalone edge device. These are reasonable next steps rather than "
                   "flaws in the underlying approach, and are already noted as future work elsewhere in the "
                   "project's documentation.")

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/Advantages_Disadvantages.docx"
    try:
        doc.save(out_path)
    except PermissionError:
        out_path = "outputs/Advantages_Disadvantages_new.docx"
        doc.save(out_path)
    print(f"[*] Advantages/Disadvantages document saved to {out_path}")


if __name__ == "__main__":
    create_pros_cons()
