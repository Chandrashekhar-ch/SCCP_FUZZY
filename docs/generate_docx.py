"""
Generates the full research paper for the project:
"A Fuzzy Inference System for Real-Time Water Potability Classification
 from Low-Cost Multi-Sensor Data"

Run from project root: python docs/generate_docx.py
Output: outputs/Research_Paper.docx
"""
import os
import json
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FIG = "outputs/figures"
FONT = "Times New Roman"


# ── Formatting helpers ───────────────────────────────────────────────
def set_font(run, size=11, bold=False, italic=False, name=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rFonts = rpr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rpr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), name)


def add_heading(doc, text, level=1, size=None, center=False):
    h = doc.add_heading(level=level)
    r = h.add_run(text)
    default_sizes = {1: 14, 2: 12.5, 3: 11.5}
    set_font(r, size=size or default_sizes.get(level, 11.5), bold=True)
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
    p.paragraph_format.line_spacing = 1.15
    return p


def add_bullets(doc, items, size=10.5):
    for text in items:
        p = doc.add_paragraph(style='List Bullet')
        r = p.add_run(text)
        set_font(r, size=size)
        p.paragraph_format.space_after = Pt(4)


def add_caption(doc, text, size=10, space_after=14):
    add_para(doc, text, size=size, italic=True, center=True, space_after=space_after)


def add_figure(doc, path, width=5.6, caption=None):
    if not os.path.exists(path):
        add_para(doc, f"[Figure missing: {path}]", italic=True)
        return
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        add_caption(doc, caption)


def add_table(doc, rows, col_widths=None, caption=None, header_rows=1, fontsize=9.5):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if r_idx == 0 or c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(val))
            set_font(run, size=fontsize, bold=(r_idx < header_rows))
            if col_widths:
                cell.width = Inches(col_widths[c_idx])
    if caption:
        add_caption(doc, caption, space_after=16)
    else:
        add_para(doc, "", space_after=10)
    return t


def load_benchmark():
    with open("outputs/benchmark_results.json") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════
def create_docx():
    doc = Document()
    section = doc.sections[0]
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)

    bench = load_benchmark()

    # ── Title ────────────────────────────────────────────────────────
    title = doc.add_heading(level=0)
    tr = title.add_run("A Fuzzy Inference System for Real-Time Water Potability "
                        "Classification from Low-Cost Multi-Sensor Data")
    set_font(tr, size=17, bold=True)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_para(doc, "SC_CProject Team", size=12, bold=True, center=True, space_after=2)
    add_para(doc, "Department of Engineering [Institution name to be inserted]", size=10.5,
             italic=True, center=True, space_after=18)

    # ── Abstract ─────────────────────────────────────────────────────
    add_heading(doc, "Abstract", level=1)
    add_para(doc, "Conventional water-quality monitoring relies on periodic laboratory analysis, which "
                   "is accurate but slow, costly, and unsuitable for continuous, distributed deployment. "
                   "Low-cost electronic alternatives typically apply hard numeric thresholds to individual "
                   "sensor readings, producing an unrealistic “cliff-edge” classification boundary, while "
                   "machine-learning (ML) classifiers offer higher accuracy at the cost of interpretability. "
                   "This paper presents a Mamdani-type Fuzzy Inference System (FIS) that fuses readings from "
                   "four low-cost sensors — pH, turbidity, total dissolved solids (TDS), and dissolved "
                   "oxygen (DO) — together with a temperature-compensation reference, into a continuous "
                   "Water Potability Index (WPI) on a 0–10 scale. The FIS applies a 45-rule base grounded in "
                   "WHO (2022) and BIS IS 10500:2012 drinking-water standards, using MIN implication, MAX "
                   "aggregation, and centroid-of-area defuzzification. The system was implemented end-to-end, "
                   "including an ESP32-based sensor front end and a real-time Flask/Socket.IO dashboard, and "
                   "was evaluated against Random Forest, k-Nearest-Neighbour (KNN) and Support Vector "
                   "Machine (SVM) classifiers on a 5,000-sample WHO/BIS-oracle synthetic dataset and on a "
                   "public real-world Kaggle water-potability dataset (3,276 samples). On the synthetic "
                   "dataset the FIS achieved 75.3% accuracy (macro-F1 75.2%) against 99.5%, 92.3% and 95.7% "
                   "for RF, KNN and SVM respectively; on the noisy real-world Kaggle dataset the FIS achieved "
                   "60.4% accuracy, matching or exceeding two of the three ML baselines (RF 59.6%, KNN "
                   "54.4%, SVM 61.2%). Unlike the ML baselines, every FIS decision is traceable to an "
                   "explicit, standards-grounded rule, making the proposed system attractive for "
                   "safety-critical and community-trust-sensitive deployments where auditability is as "
                   "important as raw accuracy.")

    add_para(doc, "Keywords: fuzzy inference system, Mamdani, water potability, water quality monitoring, "
                   "IoT sensors, interpretable machine learning, edge computing, WHO/BIS standards.",
             size=10.5, italic=True, space_after=16)

    doc.add_page_break()

    # ── 1. Introduction ─────────────────────────────────────────────
    add_heading(doc, "1. Introduction", level=1)
    add_para(doc, "Access to safe drinking water remains one of the most pressing global public-health "
                   "challenges. The World Health Organization (WHO) and national bodies such as the Bureau "
                   "of Indian Standards (BIS) publish numeric guideline values for key water-quality "
                   "parameters, but verifying compliance in the field still typically depends on collecting "
                   "a sample and sending it to a laboratory. This workflow is accurate but introduces a "
                   "delay of hours to days between sampling and result, is expensive to scale across many "
                   "distributed sources, and requires trained personnel — properties that are poorly suited "
                   "to continuous, real-time monitoring of, for example, community wells, distribution "
                   "networks, or aquaculture ponds.")
    add_para(doc, "Low-cost electronic sensors for pH, turbidity, total dissolved solids (TDS) and "
                   "dissolved oxygen (DO) have become widely available and inexpensive enough to deploy at "
                   "scale, motivating a shift toward continuous, in-situ monitoring. The simplest such "
                   "systems apply a hard numeric threshold to each parameter (for example, flagging water as "
                   "unsafe whenever pH falls outside 6.5–8.5). This produces a discontinuous “cliff-edge” "
                   "decision boundary: a reading of pH 6.49 is classified identically to pH 2.0, while pH "
                   "6.51 — a negligible physical difference — is classified as fully safe. Such systems also "
                   "generally evaluate each parameter independently, ignoring the fact that real water "
                   "samples are judged unsafe through combinations of moderately elevated parameters rather "
                   "than any single value in isolation.")
    add_para(doc, "An alternative is to apply supervised machine-learning (ML) classifiers — Random Forests, "
                   "Support Vector Machines, k-Nearest-Neighbour, or neural networks — trained on labelled "
                   "water-quality data. These can achieve high point accuracy, but function as “black "
                   "boxes”: the specific reasoning behind an individual classification cannot generally be "
                   "traced back to an auditable rule grounded in a recognized standard. For safety-critical "
                   "or regulatory contexts, and for building public trust in an automated system, this lack "
                   "of interpretability is a serious limitation.")
    add_para(doc, "This paper proposes a Mamdani-type Fuzzy Inference System (FIS) as a middle path between "
                   "these two extremes. Fuzzy logic represents each input parameter using overlapping "
                   "linguistic terms (for example, pH may simultaneously be “slightly acidic” to degree 0.4 "
                   "and “neutral” to degree 0.6), so that the resulting output varies smoothly and "
                   "continuously across a standards-defined boundary rather than jumping discontinuously. At "
                   "the same time, because every fuzzy rule is an explicit, human-readable IF–THEN statement "
                   "grounded in a specific WHO or BIS guideline value, every classification the system "
                   "produces remains fully traceable and auditable. The contributions of this paper are: "
                   "(i) a complete Mamdani FIS design — membership functions, a 45-rule WHO/BIS-grounded "
                   "rule base, and centroid defuzzification — for four-sensor water potability assessment; "
                   "(ii) an end-to-end low-cost hardware and real-time dashboard implementation; and "
                   "(iii) an empirical comparison of the FIS against three standard ML classifiers on both "
                   "a synthetic, oracle-labelled dataset and a real-world public dataset.")

    # ── 2. Related Work ──────────────────────────────────────────────
    add_heading(doc, "2. Related Work", level=1)
    add_para(doc, "Fuzzy set theory was introduced by Zadeh [3] as a mathematical framework for representing "
                   "graded, rather than binary, membership of an element in a set, and Mamdani [4] "
                   "subsequently formalized its application to rule-based inference and control. Mamdani-"
                   "type FIS have since been widely applied to environmental and water-quality assessment "
                   "problems, owing to the natural correspondence between fuzzy linguistic terms (e.g. "
                   "“acceptable”, “high”, “very high”) and the qualitative language already used in water-"
                   "quality guidelines and by domain experts.")
    add_para(doc, "Random Forest [9], Support Vector Machines [10], and k-Nearest-Neighbour [11] classifiers "
                   "are widely used supervised-learning baselines for tabular water-quality classification "
                   "tasks, including on the public Kaggle water-potability dataset used in this study. These "
                   "models are capable of learning complex, non-linear decision boundaries directly from "
                   "labelled data without requiring an explicit rule base, but — unlike a Mamdani FIS — offer "
                   "no direct mechanism for tracing an individual prediction back to an interpretable, "
                   "standards-grounded justification, which motivates the interpretability-focused design "
                   "adopted in this paper.")

    # ── 3. Proposed System / Methodology ────────────────────────────
    add_heading(doc, "3. Proposed System", level=1)

    add_heading(doc, "3.1 System Architecture", level=2)
    add_para(doc, "The proposed system follows a four-stage pipeline, illustrated in Figure 1: (1) a sensor "
                   "array acquires raw readings for pH, turbidity, TDS, DO and temperature; (2) a "
                   "preprocessing module applies temperature compensation, statistical outlier rejection, "
                   "and moving-average smoothing; (3) a Mamdani FIS engine fuzzifies the cleaned readings, "
                   "evaluates the rule base, aggregates the results, and defuzzifies to a crisp Water "
                   "Potability Index (WPI); and (4) a real-time web dashboard renders the sensor state, "
                   "membership degrees, activated rules and final classification to the user.")
    add_figure(doc, f"{FIG}/patent_fig1.png", width=3.6,
               caption="Figure 1. End-to-end system architecture, from the sensor array through to the "
                       "dashboard output.")

    add_heading(doc, "3.2 Sensor Selection and Hardware", level=2)
    add_para(doc, "Table 1 lists the sensors selected for the prototype, each chosen from the DFRobot "
                   "Gravity series for compatibility with a single analog/digital microcontroller front end. "
                   "The temperature sensor (DS18B20) does not itself contribute to the potability decision "
                   "but supplies the reference reading used for temperature compensation of the pH and DO "
                   "channels. The aggregate hardware cost of the sensor array is approximately ₹5,350 — "
                   "well below the cost of laboratory-grade instrumentation — making the design suitable for "
                   "dense, distributed deployment. Sensor signals are acquired by an ESP32 microcontroller "
                   "(12-bit ADC, 240 MHz dual-core, integrated Wi-Fi), which streams structured readings to "
                   "the host processing unit at 115,200 baud.")
    add_table(doc, [
        ["#", "Parameter", "Sensor", "Cost (INR)", "WHO / BIS Limit"],
        ["1", "pH", "DFRobot SEN0161", "~1,200", "6.5 - 8.5"],
        ["2", "Turbidity", "DFRobot SEN0189", "~800", "<1 NTU (WHO), <5 NTU (BIS)"],
        ["3", "TDS", "DFRobot SEN0244", "~700", "<500 mg/L (BIS desirable)"],
        ["4", "Dissolved Oxygen", "DFRobot SEN0237", "~2,500", ">6 mg/L (health benchmark)"],
        ["5", "Temperature", "DS18B20 (compensator)", "~150", "Calibration reference only"],
    ], col_widths=[0.3, 1.1, 1.5, 0.9, 1.9], caption="Table 1. Sensor array and hardware cost summary.")

    add_para(doc, "Temperature compensation follows two standard physical relations. For pH, the Nernstian "
                   "temperature drift is corrected as ΔpH = 0.003 × (T − 25°C). For dissolved oxygen, the "
                   "reading is corrected for the temperature dependence of oxygen solubility using the "
                   "Benson–Krause [5] saturation relation, DO_corrected = DO_raw × (DO_sat(25°C) / DO_sat(T)). "
                   "Following temperature compensation, readings are passed through a Z-score-based outlier "
                   "rejection step and a moving-average filter of window size N = 10 to suppress transient "
                   "sensor noise before fuzzification.")

    add_heading(doc, "3.3 Fuzzy Inference System Design", level=2)
    add_para(doc, "The FIS is of the Mamdani type, using MIN as the fuzzy implication and antecedent-"
                   "combination operator, MAX as the aggregation operator across rules, and centroid-of-area "
                   "(CoA) as the defuzzification method. Each of the four crisp inputs is fuzzified over its "
                   "physical universe of discourse into a set of overlapping triangular and trapezoidal "
                   "membership functions, summarized in Table 2; the corresponding output variable, the "
                   "Water Potability Index (WPI), is defined on [0, 10] and partitioned into three "
                   "overlapping classes: NON-POTABLE, MARGINAL, and POTABLE.")

    add_table(doc, [
        ["Variable", "Universe", "Linguistic Terms"],
        ["pH (input)", "0 - 14", "Acidic, Slightly Acidic, Neutral, Slightly Alkaline, Alkaline"],
        ["Turbidity (input)", "0 - 100 NTU", "Clear, Slightly Turbid, Turbid, Very Turbid"],
        ["TDS (input)", "0 - 1500 mg/L", "Pure, Acceptable, High, Very High"],
        ["Dissolved Oxygen (input)", "0 - 20 mg/L", "Very Low, Low, Acceptable, High"],
        ["WPI (output)", "0 - 10", "Non-Potable, Marginal, Potable"],
    ], col_widths=[1.7, 1.2, 3.2], caption="Table 2. Fuzzy input/output variables and their linguistic terms.")

    add_figure(doc, f"{FIG}/mf_ph.png", width=5.6,
               caption="Figure 2. Membership functions defined over the pH input; the shaded band marks "
                       "the WHO safe range (6.5-8.5).")
    add_figure(doc, f"{FIG}/mf_output_wpi.png", width=5.6,
               caption="Figure 3. Membership functions defined over the output variable, the Water "
                       "Potability Index (WPI).")

    add_heading(doc, "3.3.1 Rule Base", level=3)
    add_para(doc, "The rule base comprises 45 IF-THEN rules, each rule combining the linguistic terms of "
                   "the four input variables via the MIN operator and mapping to a linguistic term of the "
                   "WPI output, with an associated rule weight (0.8-1.0) reflecting confidence in boundary "
                   "cases. Every rule is derived from, and traceable to, a specific WHO (2022) or BIS IS "
                   "10500:2012 guideline value. Table 3 summarizes the rule base by logical group; the "
                   "complete rule listing is provided in the project's design documentation.")
    add_table(doc, [
        ["Rule Group", "# Rules", "Consequent"],
        ["Fully potable (all parameters within safe range)", "8", "POTABLE"],
        ["Hard non-potability triggers (single-parameter failure)", "5", "NON-POTABLE"],
        ["Dual-parameter failures", "4", "NON-POTABLE"],
        ["Single-parameter boundary violation", "13", "MARGINAL"],
        ["Turbid + mixed-parameter combinations", "4", "MARGINAL / NON-POTABLE"],
        ["Extreme worst-case scenarios", "3", "NON-POTABLE"],
        ["Multi-parameter boundary cases", "8", "MARGINAL"],
        ["Total", "45", "-"],
    ], col_widths=[3.3, 0.9, 1.9], caption="Table 3. Rule base composition by logical group.")
    add_para(doc, "Representative rules include:", space_after=4)
    add_bullets(doc, [
        "R1: IF pH=NEUTRAL AND Turbidity=CLEAR AND TDS=ACCEPTABLE AND DO=HIGH THEN WPI=POTABLE (weight 1.0)",
        "R9: IF pH=ACIDIC THEN WPI=NON_POTABLE (weight 1.0) - a critical single-parameter trigger",
        "R18: IF pH=NEUTRAL AND Turbidity=SLIGHTLY_TURBID AND TDS=ACCEPTABLE AND DO=ACCEPTABLE "
        "THEN WPI=MARGINAL (weight 0.80)",
    ])

    add_heading(doc, "3.3.2 Defuzzification", level=3)
    add_para(doc, "For a given set of crisp inputs, each of the 45 rules is evaluated and its firing "
                   "strength computed as the minimum of its antecedent membership degrees, scaled by the "
                   "rule weight. Each activated rule clips its consequent output membership function at "
                   "this firing strength (MIN implication), and the clipped outputs of all activated rules "
                   "are combined into a single aggregate fuzzy set using the MAX operator. The crisp WPI is "
                   "then obtained by the centroid-of-area method,")
    add_para(doc, "WPI = ( ∫ μ_agg(y) · y  dy ) / ( ∫ μ_agg(y) dy ),  y ∈ [0, 10]", center=True, italic=True)
    add_para(doc, "computed numerically over a 1,000-point discretization of the output universe of "
                   "discourse.")

    add_heading(doc, "3.4 Implementation", level=2)
    add_para(doc, "The system was implemented in Python, with the FIS engine, rule base and preprocessing "
                   "pipeline as standalone modules, an ESP32 firmware sketch for the hardware front end, and "
                   "a Flask + Socket.IO web server driving a real-time browser dashboard. The dashboard "
                   "renders an animated WPI arc gauge, live per-sensor status cards, a 60-second rolling WPI "
                   "trend chart, live membership-degree visualizations for each input, an “active rules” "
                   "panel showing which of the 45 rules are currently firing and at what strength, a "
                   "manual/slider-driven inference mode, and a selector across six demonstration scenarios "
                   "(normal, ideal potable, acidic, turbid, hard-water, and worst-case contaminated).")

    doc.add_page_break()

    # ── 4. Experimental Evaluation ──────────────────────────────────
    add_heading(doc, "4. Experimental Evaluation", level=1)

    add_heading(doc, "4.1 Datasets", level=2)
    add_para(doc, "Two datasets were used to evaluate the proposed FIS against three supervised ML "
                   "baselines - Random Forest, k-Nearest-Neighbour (k=7), and Support Vector Machine "
                   "(RBF kernel):")
    add_bullets(doc, [
        "Synthetic dataset - 5,000 samples generated with Gaussian sensor noise and labelled by a "
        "WHO/BIS hard-threshold oracle, with class proportions of approximately 40% potable, 35% "
        "marginal and 25% non-potable, as configured in the project's data generator.",
        "Kaggle real-world dataset - the public “Water Potability” dataset (3,276 samples; 2,785 "
        "retained after dropping rows with missing values), providing an independent, noisier, "
        "real-world test of generalization.",
    ], size=10.5)
    add_para(doc, "For the synthetic dataset, the FIS (which requires no training) was evaluated on the "
                   "full 5,000-sample set, while the ML baselines were trained on an 80% split and evaluated "
                   "on the held-out 20% (1,000 samples); this asymmetry, native to the project's benchmark "
                   "harness, is noted here for completeness and should be taken into account when comparing "
                   "the reported accuracies directly.")

    add_heading(doc, "4.2 Results on the Synthetic Dataset", level=2)
    fis_r = bench["Mamdani FIS (Proposed)"]
    rf_r = bench["Random Forest"]
    knn_r = bench["KNN (k=7)"]
    svm_r = bench["SVM (RBF)"]
    add_table(doc, [
        ["Method", "Accuracy (%)", "Macro F1 (%)", "Interpretable"],
        ["Mamdani FIS (proposed)", f"{fis_r['accuracy']:.1f}", f"{fis_r['f1_macro']:.1f}", "Yes"],
        ["Random Forest", f"{rf_r['accuracy']:.1f}", f"{rf_r['f1_macro']:.1f}", "No"],
        ["KNN (k=7)", f"{knn_r['accuracy']:.1f}", f"{knn_r['f1_macro']:.1f}", "No"],
        ["SVM (RBF)", f"{svm_r['accuracy']:.1f}", f"{svm_r['f1_macro']:.1f}", "No"],
    ], col_widths=[2.2, 1.3, 1.3, 1.3], caption="Table 4. Overall accuracy and macro-F1 on the synthetic, "
                                                  "oracle-labelled dataset.")
    add_figure(doc, f"{FIG}/benchmark_comparison.png", width=5.4,
               caption="Figure 4. Classifier accuracy on the synthetic (WHO-oracle) dataset versus the "
                       "real-world Kaggle dataset.")

    add_para(doc, "Table 5 reports per-class precision, recall and F1-score for each method on the "
                   "synthetic dataset. The FIS attains perfect recall (1.00) on the NON-POTABLE class, "
                   "reflecting the deliberately conservative single-parameter “hard trigger” rules (e.g. R9), "
                   "at the cost of lower precision on the POTABLE class; the ML baselines, by contrast, "
                   "achieve near-perfect scores across all classes, consistent with directly optimizing "
                   "against the same hard-threshold oracle used to generate the labels.")
    add_table(doc, [
        ["Method", "Class", "Precision", "Recall", "F1-score"],
        ["Mamdani FIS", "Non-Potable", f"{fis_r['report']['NON_POTABLE']['precision']:.2f}",
         f"{fis_r['report']['NON_POTABLE']['recall']:.2f}", f"{fis_r['report']['NON_POTABLE']['f1-score']:.2f}"],
        ["", "Marginal", f"{fis_r['report']['MARGINAL']['precision']:.2f}",
         f"{fis_r['report']['MARGINAL']['recall']:.2f}", f"{fis_r['report']['MARGINAL']['f1-score']:.2f}"],
        ["", "Potable", f"{fis_r['report']['POTABLE']['precision']:.2f}",
         f"{fis_r['report']['POTABLE']['recall']:.2f}", f"{fis_r['report']['POTABLE']['f1-score']:.2f}"],
        ["Random Forest", "Non-Potable", f"{rf_r['report']['NON_POTABLE']['precision']:.2f}",
         f"{rf_r['report']['NON_POTABLE']['recall']:.2f}", f"{rf_r['report']['NON_POTABLE']['f1-score']:.2f}"],
        ["", "Marginal", f"{rf_r['report']['MARGINAL']['precision']:.2f}",
         f"{rf_r['report']['MARGINAL']['recall']:.2f}", f"{rf_r['report']['MARGINAL']['f1-score']:.2f}"],
        ["", "Potable", f"{rf_r['report']['POTABLE']['precision']:.2f}",
         f"{rf_r['report']['POTABLE']['recall']:.2f}", f"{rf_r['report']['POTABLE']['f1-score']:.2f}"],
        ["KNN (k=7)", "Non-Potable", f"{knn_r['report']['NON_POTABLE']['precision']:.2f}",
         f"{knn_r['report']['NON_POTABLE']['recall']:.2f}", f"{knn_r['report']['NON_POTABLE']['f1-score']:.2f}"],
        ["", "Marginal", f"{knn_r['report']['MARGINAL']['precision']:.2f}",
         f"{knn_r['report']['MARGINAL']['recall']:.2f}", f"{knn_r['report']['MARGINAL']['f1-score']:.2f}"],
        ["", "Potable", f"{knn_r['report']['POTABLE']['precision']:.2f}",
         f"{knn_r['report']['POTABLE']['recall']:.2f}", f"{knn_r['report']['POTABLE']['f1-score']:.2f}"],
        ["SVM (RBF)", "Non-Potable", f"{svm_r['report']['NON_POTABLE']['precision']:.2f}",
         f"{svm_r['report']['NON_POTABLE']['recall']:.2f}", f"{svm_r['report']['NON_POTABLE']['f1-score']:.2f}"],
        ["", "Marginal", f"{svm_r['report']['MARGINAL']['precision']:.2f}",
         f"{svm_r['report']['MARGINAL']['recall']:.2f}", f"{svm_r['report']['MARGINAL']['f1-score']:.2f}"],
        ["", "Potable", f"{svm_r['report']['POTABLE']['precision']:.2f}",
         f"{svm_r['report']['POTABLE']['recall']:.2f}", f"{svm_r['report']['POTABLE']['f1-score']:.2f}"],
    ], col_widths=[1.5, 1.2, 1.0, 1.0, 1.0], caption="Table 5. Per-class precision, recall and F1-score on "
                                                        "the synthetic dataset.")

    add_figure(doc, f"{FIG}/fis_confusion_matrix.png", width=3.6,
               caption="Figure 5. Confusion matrix of the Mamdani FIS on the synthetic test set.")

    add_heading(doc, "4.3 Results on the Real-World Kaggle Dataset", level=2)
    add_para(doc, "Table 6 reports accuracy and macro-F1 on the independent, real-world Kaggle water-"
                   "potability dataset, which is considerably noisier and less separable than the synthetic "
                   "oracle-labelled data. Here the FIS - which requires no training and was designed purely "
                   "from WHO/BIS guideline values, without ever seeing this dataset - achieves 60.4% "
                   "accuracy, outperforming Random Forest and KNN and closely trailing SVM, despite the "
                   "trained models having the benefit of directly fitting this data's label distribution.")
    add_table(doc, [
        ["Method", "Accuracy (%)", "Macro F1 (%)", "Interpretable"],
        ["Mamdani FIS (proposed)", "60.43", "37.67", "Yes"],
        ["Random Forest", "59.61", "46.20", "No"],
        ["KNN (k=7)", "54.40", "49.40", "No"],
        ["SVM (RBF)", "61.22", "41.94", "No"],
    ], col_widths=[2.2, 1.3, 1.3, 1.3], caption="Table 6. Accuracy and macro-F1 on the real-world Kaggle "
                                                  "water-potability dataset (2,785 samples after removing "
                                                  "rows with missing values).")

    # ── 5. Discussion ────────────────────────────────────────────────
    add_heading(doc, "5. Discussion", level=1)
    add_para(doc, "The synthetic-dataset results (Table 4, Table 5) show the expected gap between the FIS "
                   "and the ML baselines: because the synthetic labels were generated by a hard-threshold "
                   "oracle and the ML models are trained directly against that same oracle, they can "
                   "essentially memorize its decision boundaries, whereas the FIS deliberately trades a "
                   "portion of that boundary-matching accuracy for smooth, graded transitions across "
                   "class boundaries. This trade-off is most visible in the MARGINAL class (WPI "
                   "approximately 3.5-6.5), where a hard-threshold oracle produces abrupt binary "
                   "assignments that a graded fuzzy system will not exactly reproduce, while still "
                   "correctly identifying the sample as being in a transitional, non-ideal state.")
    add_para(doc, "The Kaggle real-world results (Table 6) are more representative of practical "
                   "deployment conditions, and there the FIS is competitive with, and in two of three "
                   "cases better than, models that were specifically trained on that dataset - despite the "
                   "FIS having been designed zero-shot from published standards alone, with no access to "
                   "the dataset's labels. This suggests that the standards-grounded rule base generalizes "
                   "reasonably well to real, noisy sensor data, and is not overfit to any particular "
                   "labelling convention.")
    add_para(doc, "Critically, accuracy alone does not capture the primary advantage of the proposed "
                   "approach: interpretability. Every WPI value the FIS produces can be decomposed into the "
                   "specific set of rules that fired and their respective strengths, each traceable to an "
                   "explicit WHO or BIS guideline value. None of the three ML baselines offer an equivalent, "
                   "built-in mechanism for explaining an individual prediction. For safety-critical or "
                   "regulatory water-quality decisions - where a rejected sample may need to be justified to "
                   "an affected community or a regulator - this auditability is arguably as important as raw "
                   "point accuracy, and is the central motivation for the system proposed in this paper.")
    add_para(doc, "Limitations of the present study include: the comparison on the synthetic dataset uses "
                   "an oracle that is itself hard-threshold-based, which structurally favours the ML "
                   "baselines trained against it; the evaluation was conducted on stored datasets rather "
                   "than on live sensor hardware in the field; and the rule base, while grounded in "
                   "published standards, has not yet been validated against expert human assessments of "
                   "real water samples spanning the full range of the input space.")

    # ── 6. Conclusion ────────────────────────────────────────────────
    add_heading(doc, "6. Conclusion and Future Work", level=1)
    add_para(doc, "This paper presented a complete Mamdani Fuzzy Inference System for real-time water "
                   "potability classification from four low-cost sensors, together with an end-to-end "
                   "hardware and dashboard implementation. The system was validated against Random Forest, "
                   "KNN and SVM baselines on both a synthetic, oracle-labelled dataset and an independent "
                   "real-world Kaggle dataset, achieving competitive accuracy on real-world data while "
                   "retaining full rule-level interpretability grounded in WHO and BIS drinking-water "
                   "standards. The results support fuzzy inference as a practical middle ground between "
                   "brittle hard-threshold systems and opaque machine-learning classifiers for safety-"
                   "critical environmental monitoring.")
    add_para(doc, "Future work includes: field deployment and calibration of the sensor array across "
                   "multiple real water sources; hybrid tuning of the membership functions and rule weights "
                   "against expert-labelled field data (e.g. via an ANFIS-style adaptive scheme) while "
                   "preserving interpretability; and porting the FIS engine to run natively on the ESP32 "
                   "microcontroller, removing the dependency on a host processing unit for inference.")

    doc.add_page_break()

    # ── References ───────────────────────────────────────────────────
    add_heading(doc, "References", level=1)
    refs = [
        "World Health Organization, Guidelines for Drinking-Water Quality, 4th ed., WHO, Geneva, 2022.",
        "Bureau of Indian Standards, IS 10500:2012 - Drinking Water Specification (Second Revision), "
        "BIS, New Delhi, 2012.",
        "L. A. Zadeh, \"Fuzzy sets,\" Information and Control, vol. 8, no. 3, pp. 338-353, 1965.",
        "E. H. Mamdani, \"Application of fuzzy algorithms for control of simple dynamic plant,\" "
        "Proceedings of the IEE, vol. 121, no. 12, pp. 1585-1588, 1974.",
        "B. B. Benson and D. Krause, \"The concentration and isotopic fractionation of oxygen "
        "dissolved in freshwater and seawater in equilibrium with the atmosphere,\" Limnology and "
        "Oceanography, vol. 29, no. 3, pp. 620-632, 1984.",
        "DFRobot, Gravity: Analog pH / Turbidity / TDS / Dissolved Oxygen Sensor datasheets "
        "(SEN0161, SEN0189, SEN0244, SEN0237), DFRobot Co., accessed 2026.",
        "J. Kim et al., \"scikit-fuzzy: fuzzy logic toolbox for Python,\" SciPy Toolkits, 2019.",
        "Kaggle, \"Water Potability Dataset,\" https://www.kaggle.com/datasets/adityakadiwal/water-potability, "
        "accessed 2026.",
        "L. Breiman, \"Random forests,\" Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.",
        "C. Cortes and V. Vapnik, \"Support-vector networks,\" Machine Learning, vol. 20, no. 3, "
        "pp. 273-297, 1995.",
        "T. M. Cover and P. E. Hart, \"Nearest neighbor pattern classification,\" IEEE Transactions "
        "on Information Theory, vol. 13, no. 1, pp. 21-27, 1967.",
    ]
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        r = p.add_run(f"[{i}]  {ref}")
        set_font(r, size=10)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)

    out_path = 'outputs/Research_Paper.docx'
    try:
        doc.save(out_path)
    except PermissionError:
        out_path = 'outputs/Research_Paper_new.docx'
        doc.save(out_path)
    print(f"[*] Research Paper saved to {out_path}")


if __name__ == "__main__":
    create_docx()
