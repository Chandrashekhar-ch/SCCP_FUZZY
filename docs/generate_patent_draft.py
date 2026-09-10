"""
Generates a draft patent specification document for:
"A Fuzzy Logic Based System and Method for Real-Time Water Potability
 Classification Using Low-Cost Multi-Sensor Data"

This is a DRAFT prepared from the project's technical documentation to
assist a patent agent/attorney in preparing a formal application
(e.g. Indian Patents Act, 1970 provisional/complete specification format).
It is not a substitute for professional legal review before filing.

Run from project root: python docs/generate_patent_draft.py
Output: outputs/Patent_Draft.docx
"""
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FIG = "outputs/figures"


def set_font(run, size=11, bold=False, italic=False, name="Times New Roman"):
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
    default_sizes = {1: 15, 2: 13, 3: 12}
    set_font(r, size=size or default_sizes.get(level, 12), bold=True)
    if center:
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    return h


def add_para(doc, text, size=11, bold=False, italic=False, center=False, space_after=8):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_font(r, size=size, bold=bold, italic=italic)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    return p


def add_numbered(doc, items, size=11, start=1):
    for i, text in enumerate(items, start=start):
        p = doc.add_paragraph()
        r = p.add_run(f"{i}.  {text}")
        set_font(r, size=size)
        p.paragraph_format.space_after = Pt(7)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Inches(0.3)


def add_claim(doc, num, text, dependent=False):
    p = doc.add_paragraph()
    r = p.add_run(f"{num}.  {text}")
    set_font(r, size=11)
    p.paragraph_format.space_after = Pt(9)
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.left_indent = Inches(0.35 if not dependent else 0.55)


def add_figure(doc, path, width=5.6, caption=None):
    if not os.path.exists(path):
        add_para(doc, f"[Figure missing: {path}]", italic=True)
        return
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        add_para(doc, caption, size=10, italic=True, center=True, space_after=14)


def add_table(doc, rows, col_widths=None, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            set_font(run, size=10, bold=(header and r_idx == 0))
            if col_widths:
                cell.width = Inches(col_widths[c_idx])
    return t


def create_patent_draft():
    doc = Document()
    section = doc.sections[0]
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # ── Cover ────────────────────────────────────────────────────────
    add_para(doc, "DRAFT — FOR ATTORNEY / PATENT AGENT REVIEW", size=10, bold=True, center=True)
    add_para(doc, "NOT YET FILED. PREPARED FROM PROJECT TECHNICAL RECORDS.", size=9, italic=True, center=True, space_after=24)

    title = doc.add_heading(level=0)
    tr = title.add_run("COMPLETE SPECIFICATION")
    set_font(tr, size=16, bold=True)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_para(doc, "(See Section 10 and Rule 13 of the Patents Act, 1970 / Patents Rules, 2003 — India;"
                  " to be adapted to the applicable jurisdiction's format before filing)",
             size=9.5, italic=True, center=True, space_after=20)

    add_heading(doc, "TITLE OF THE INVENTION", level=1)
    add_para(doc, "“A FUZZY LOGIC BASED SYSTEM AND METHOD FOR REAL-TIME WATER "
                  "POTABILITY CLASSIFICATION USING LOW-COST MULTI-SENSOR DATA”", bold=True)

    add_heading(doc, "APPLICANT(S)", level=1)
    add_para(doc, "[Applicant name(s) / Institution to be inserted]")
    add_heading(doc, "INVENTOR(S)", level=1)
    add_para(doc, "SC_CProject Team [names to be inserted]")

    doc.add_page_break()

    # ── Field of Invention ──────────────────────────────────────────
    add_heading(doc, "FIELD OF THE INVENTION", level=1)
    add_para(doc, "The present invention relates to water quality monitoring systems, and more "
                   "particularly to an embedded, edge-deployable system and method that applies a "
                   "Mamdani-type fuzzy inference engine to real-time readings from a low-cost "
                   "multi-parameter sensor array (pH, turbidity, total dissolved solids, dissolved "
                   "oxygen and temperature) to compute a continuous, interpretable Water Potability "
                   "Index (WPI) and to display the result on a real-time visual dashboard.")

    # ── Background ────────────────────────────────────────────────────
    add_heading(doc, "BACKGROUND OF THE INVENTION", level=1)
    add_para(doc, "Access to safe drinking water is a critical public health requirement. Conventional "
                   "water-quality assessment relies on periodic laboratory analysis of collected samples. "
                   "This approach suffers from several drawbacks: (a) it requires trained personnel and "
                   "calibrated laboratory instruments; (b) results are typically available only after a "
                   "delay of hours to days, precluding real-time intervention; and (c) it is not "
                   "economically or logistically feasible to deploy at the density required for continuous "
                   "monitoring of distributed water sources, particularly in resource-constrained regions.")
    add_para(doc, "Existing low-cost electronic monitoring attempts typically apply hard, threshold-based "
                   "decision rules to individual sensor readings (for example, declaring water “unsafe” "
                   "whenever pH falls outside a fixed numeric band). Such hard-threshold classifiers suffer "
                   "from a “cliff-edge” effect: an infinitesimally small change in a measured parameter "
                   "at a threshold boundary produces a discontinuous jump in the output classification, which "
                   "does not reflect the underlying physical reality that water quality degrades gradually. "
                   "Hard-threshold systems are additionally unable to reason jointly over multiple correlated "
                   "parameters in a graded manner.")
    add_para(doc, "Separately, machine-learning classifiers (for example, random forests, support vector "
                   "machines, or neural networks) have been applied to water-quality classification and can "
                   "achieve high point accuracy on a given dataset. However, such models function largely as "
                   "“black boxes”: the basis for a specific classification decision cannot readily be "
                   "traced to an auditable, standards-grounded rule. This lack of interpretability is a "
                   "significant limitation for safety-critical, regulatory, or community-trust-sensitive "
                   "deployments, where a decision-maker must be able to explain why a given water sample was "
                   "classified as unsafe.")
    add_para(doc, "There exists, therefore, a need for a water-quality classification system that (i) operates "
                   "in real time on low-cost embedded hardware without dependence on a remote laboratory or "
                   "cloud inference service, (ii) produces a continuous, graded output rather than an abrupt "
                   "binary or hard-banded decision, and (iii) remains fully interpretable, with every "
                   "classification traceable to explicit rules grounded in recognized drinking-water standards "
                   "such as the WHO Guidelines for Drinking-Water Quality and the Bureau of Indian Standards "
                   "IS 10500 specification.")

    # ── Objects ──────────────────────────────────────────────────────
    add_heading(doc, "OBJECTS OF THE INVENTION", level=1)
    add_numbered(doc, [
        "To provide a system and method for real-time classification of water potability using "
        "readings acquired from a low-cost, multi-parameter sensor array.",
        "To provide a fuzzy-logic-based inference engine that produces a continuous, graded Water "
        "Potability Index (WPI) in place of an abrupt binary or hard-threshold classification.",
        "To provide a rule base whose individual rules are explicitly grounded in recognized "
        "drinking-water standards (WHO 2022; BIS IS 10500:2012), such that every classification "
        "decision is fully traceable and auditable.",
        "To provide a preprocessing module that compensates sensor readings for temperature-induced "
        "drift and rejects transient noise/outliers prior to fuzzy inference.",
        "To provide a system architecture that is deployable on a low-cost embedded microcontroller "
        "and associated sensor stack at a total hardware cost significantly lower than laboratory "
        "test equipment.",
        "To provide a real-time visual dashboard that displays live sensor readings, fuzzy membership "
        "degrees, activated rules and the resulting potability classification to a human operator.",
        "To provide a method that maintains classification performance in boundary/ambiguous "
        "conditions superior to a hard-threshold classifier, by virtue of graded fuzzy-set membership.",
    ])

    # ── Summary ──────────────────────────────────────────────────────
    add_heading(doc, "SUMMARY OF THE INVENTION", level=1)
    add_para(doc, "In accordance with the present invention, there is provided a system for real-time "
                   "water potability classification comprising: a sensor array including at least a pH "
                   "sensor, a turbidity sensor, a total dissolved solids (TDS) sensor, a dissolved oxygen "
                   "(DO) sensor, and a temperature sensor; a signal acquisition and microcontroller unit "
                   "configured to digitize and transmit the sensor readings; a preprocessing module "
                   "configured to apply temperature compensation, statistical outlier rejection and moving-"
                   "average noise filtering to the acquired readings; a fuzzy inference engine of the "
                   "Mamdani type configured to fuzzify the preprocessed readings into degrees of membership "
                   "in a plurality of linguistic terms, to evaluate a rule base of the order of forty-five "
                   "expert rules using a minimum (MIN) implication operator, to aggregate the resultant "
                   "fuzzy output sets using a maximum (MAX) operator, and to defuzzify the aggregated set "
                   "using the centroid-of-area method to yield a crisp Water Potability Index (WPI) on a "
                   "continuous scale; a classifier configured to map the WPI to one of a plurality of "
                   "potability classes; and a display/dashboard unit configured to render the sensor "
                   "readings, membership degrees, activated rules and resulting classification in "
                   "substantially real time.")
    add_para(doc, "In a further aspect, there is provided a corresponding computer-implemented method "
                   "comprising the steps of: acquiring raw sensor readings; applying temperature "
                   "compensation to at least the pH and dissolved-oxygen readings; rejecting statistical "
                   "outliers and smoothing the readings using a moving-average filter; fuzzifying the "
                   "filtered readings; evaluating a WHO/BIS-standards-grounded rule base using MIN "
                   "implication; aggregating the activated rule outputs using a MAX operator; defuzzifying "
                   "the aggregate via the centroid-of-area technique to compute the WPI; classifying the "
                   "WPI into a non-potable, marginal, or potable class; and displaying the result on a "
                   "real-time interface, the foregoing steps being repeated continuously to provide "
                   "real-time monitoring.")
    add_para(doc, "The invention is further described, without limitation, with reference to the "
                   "accompanying drawings and the detailed description below.")

    # ── Brief description of drawings ───────────────────────────────
    add_heading(doc, "BRIEF DESCRIPTION OF THE ACCOMPANYING DRAWINGS", level=1)
    add_para(doc, "FIG. 1 illustrates a block diagram of the overall system (100) of the present "
                   "invention, showing the sensor array (102), signal acquisition/microcontroller unit "
                   "(116), preprocessing module (114), fuzzy inference engine (118) and display/dashboard "
                   "unit (128).")
    add_para(doc, "FIG. 2 illustrates a flowchart of the computer-implemented method of the present "
                   "invention, from acquisition of raw sensor readings (202) through to output of the "
                   "classification result on the dashboard (218), repeated in a continuous real-time loop.")
    add_para(doc, "FIG. 3A illustrates representative fuzzy membership functions defined over the input "
                   "variable pH, showing the linguistic terms ACIDIC, SLIGHTLY ACIDIC, NEUTRAL, SLIGHTLY "
                   "ALKALINE and ALKALINE.")
    add_para(doc, "FIG. 3B illustrates the fuzzy membership functions defined over the output variable, "
                   "the Water Potability Index (WPI), showing the linguistic terms NON-POTABLE, MARGINAL "
                   "and POTABLE.")
    add_para(doc, "FIG. 4 illustrates a hardware/deployment diagram showing the physical arrangement of "
                   "the sensor array (102), microcontroller (116), communication link (130), host "
                   "processing unit (132) executing the preprocessing module and fuzzy inference engine, "
                   "and the dashboard/client display device (128, 134).")

    doc.add_page_break()

    # ── Detailed Description ────────────────────────────────────────
    add_heading(doc, "DETAILED DESCRIPTION OF THE INVENTION", level=1)
    add_para(doc, "The following detailed description is provided to enable a person skilled in the art "
                   "to make and use the invention, and sets forth the best mode presently contemplated. It "
                   "is to be understood that the invention is not limited to the specific embodiment "
                   "described, and that variations in the number and type of sensors, the specific "
                   "membership function shapes and parameters, the number of rules, and the specific "
                   "microcontroller or communication protocol used, remain within the scope of the "
                   "invention as claimed.")

    add_heading(doc, "1. System Architecture (FIG. 1)", level=2)
    add_para(doc, "Referring to FIG. 1, the system (100) comprises a sensor array (102) including a pH "
                   "sensor (104), a turbidity sensor (106), a total dissolved solids (TDS) sensor (108), a "
                   "dissolved-oxygen (DO) sensor (110), and a temperature sensor (112), the last of which "
                   "serves as a compensation reference rather than a potability parameter in its own right. "
                   "In one embodiment, the sensors are of the low-cost gravity/analog type (for example, "
                   "DFRobot SEN0161, SEN0189, SEN0244 and SEN0237, and a DS18B20 digital temperature probe), "
                   "selected such that the aggregate hardware cost of the sensor array is of the order of "
                   "INR 5,000–6,000, i.e. substantially below the cost of laboratory-grade instrumentation.")
    add_figure(doc, f"{FIG}/patent_fig1.png", width=5.6, caption="FIG. 1 — System block diagram (100)")
    add_para(doc, "The signal acquisition/microcontroller unit (116) — in one embodiment an ESP32 system-on-"
                   "chip having an integrated multi-channel analog-to-digital converter and wireless "
                   "communication capability — periodically samples each sensor of the array (102) and "
                   "transmits the digitized readings, for example as a structured data packet, to a "
                   "preprocessing module (114). The preprocessing module (114) is configured to: (a) apply a "
                   "temperature-compensation correction to the raw pH and dissolved-oxygen readings, "
                   "compensating for temperature-induced sensor drift; (b) reject statistical outliers, for "
                   "example using a Z-score threshold; and (c) apply a moving-average filter over a window "
                   "of N consecutive samples (in one embodiment N=10) to suppress transient measurement "
                   "noise prior to fuzzy inference.")
    add_para(doc, "The preprocessed, compensated readings are supplied to a fuzzy inference engine (118) "
                   "comprising a fuzzification unit (120), a rule evaluation unit (122) operating in "
                   "conjunction with a stored rule base (123), and an aggregation and defuzzification unit "
                   "(124), the operation of which is described in further detail below with reference to "
                   "FIG. 2. The scalar output of the fuzzy inference engine (118), the Water Potability "
                   "Index (WPI), is supplied to a classifier (126) that maps the WPI onto one of a plurality "
                   "of discrete potability classes for human-readable presentation, and the classification "
                   "result, together with the underlying sensor readings and fuzzy-inference state, is "
                   "rendered on a display/dashboard unit (128).")

    add_heading(doc, "2. Inference Method (FIG. 2)", level=2)
    add_figure(doc, f"{FIG}/patent_fig2.png", width=3.6, caption="FIG. 2 — Method flowchart (200–220)")
    add_para(doc, "As shown in FIG. 2, the method begins (200) with the acquisition of raw sensor readings "
                   "(202) from the sensor array. Temperature compensation is applied (204); in one "
                   "embodiment the pH correction follows the relation ΔpH = 0.003 × (T − 25°C), and the "
                   "dissolved-oxygen correction follows a temperature-dependent saturation relation of the "
                   "Benson-Krause type, DO_corrected = DO_raw × (DO_sat(25°C) / DO_sat(T)). Outliers are "
                   "rejected and the readings are smoothed (206) using the moving-average filter described "
                   "above.")
    add_para(doc, "The filtered, crisp input values are then fuzzified (208): for each input variable, the "
                   "degree of membership μ(x) in each of a plurality of linguistic terms (represented by "
                   "triangular and trapezoidal membership functions, as illustrated in FIG. 3A) is computed. "
                   "The rule evaluation unit then evaluates (210) a rule base (123) of IF–THEN rules of the "
                   "general form “IF (pH is T1) AND (Turbidity is T2) AND (TDS is T3) AND (DO is T4) THEN "
                   "(WPI is T5)”, where each Ti is a linguistic term, using the minimum (MIN) operator as the "
                   "fuzzy implication and to combine antecedent clauses, each rule additionally being "
                   "assigned a weighting factor. In one embodiment, the rule base comprises forty-five (45) "
                   "such rules, organized into logical groups including fully-potable rules, hard "
                   "single-parameter non-potability triggers, dual-parameter failure rules, boundary-"
                   "violation rules, and multi-parameter combination rules, each rule being derived from and "
                   "traceable to a specific provision of the WHO Guidelines for Drinking-Water Quality "
                   "(2022) and/or Bureau of Indian Standards IS 10500:2012.")
    add_para(doc, "The output fuzzy sets produced by all activated rules are aggregated (212) using the "
                   "maximum (MAX) operator, and the resulting aggregate fuzzy set — defined over the output "
                   "membership functions illustrated in FIG. 3B — is defuzzified (214) using the centroid-of-"
                   "area technique, computing WPI = ∫μ_agg(y)·y dy / ∫μ_agg(y) dy over the output universe of "
                   "discourse [0, 10], in one embodiment using a discretization of the order of 1000 points "
                   "for numerical integration. The resulting crisp WPI is classified (216) into one of a "
                   "plurality of classes, for example NON-POTABLE (WPI approximately 0–3.5), MARGINAL (WPI "
                   "approximately 3.5–6.5), and POTABLE (WPI approximately 6.5–10), and the result is output "
                   "to the dashboard (218). Steps (202) through (218) are repeated continuously (220), such "
                   "that the system provides substantially real-time, updated classification as new sensor "
                   "data becomes available.")

    add_heading(doc, "3. Membership Functions (FIG. 3A, FIG. 3B)", level=2)
    add_figure(doc, f"{FIG}/patent_fig3a.png", width=5.6, caption="FIG. 3A — Input membership functions for pH")
    add_figure(doc, f"{FIG}/patent_fig3b.png", width=5.6, caption="FIG. 3B — Output membership functions for WPI")
    add_para(doc, "In one embodiment, each input variable is defined over a respective universe of "
                   "discourse and partitioned into overlapping fuzzy sets using triangular and trapezoidal "
                   "membership functions, such that a given crisp reading may simultaneously belong, to "
                   "differing degrees, to two adjacent linguistic terms. This overlapping construction "
                   "ensures that the classification output varies smoothly and continuously as a sensor "
                   "reading moves across a nominal standards-defined boundary, in contradistinction to the "
                   "discontinuous behavior of a hard-threshold classifier. Representative parameterizations "
                   "for pH, turbidity, TDS, dissolved oxygen and the WPI output are set out in Table 1 below; "
                   "it is to be understood that these specific numeric parameters are exemplary and may be "
                   "adjusted without departing from the scope of the invention.")

    add_table(doc, [
        ["Variable", "Universe", "Representative Linguistic Terms"],
        ["pH (input)", "0–14", "Acidic, Slightly Acidic, Neutral, Slightly Alkaline, Alkaline"],
        ["Turbidity (input)", "0–100 NTU", "Clear, Slightly Turbid, Turbid, Very Turbid"],
        ["TDS (input)", "0–1500 mg/L", "Pure, Acceptable, High, Very High"],
        ["Dissolved Oxygen (input)", "0–20 mg/L", "Very Low, Low, Acceptable, High"],
        ["WPI (output)", "0–10", "Non-Potable, Marginal, Potable"],
    ], col_widths=[1.7, 1.2, 3.1])
    add_para(doc, "Table 1 — Representative input/output variables and linguistic terms.", size=9.5,
             italic=True, center=True, space_after=16)

    add_heading(doc, "4. Hardware Deployment (FIG. 4)", level=2)
    add_figure(doc, f"{FIG}/patent_fig4.png", width=6.0, caption="FIG. 4 — Hardware / deployment diagram")
    add_para(doc, "FIG. 4 illustrates one physical deployment of the system, in which the sensor array "
                   "(102) is electrically coupled to a microcontroller (116), which is in turn communicably "
                   "coupled, via a serial or wireless (Wi-Fi) communication link (130), to a host processing "
                   "unit (132) executing the preprocessing module (114) and fuzzy inference engine (118). "
                   "The host processing unit (132) is further coupled to a dashboard/client display device "
                   "(128, 134), in one embodiment implemented as a web server providing a browser-based "
                   "graphical interface over a WebSocket connection, presenting an animated potability "
                   "gauge, live sensor cards, membership-degree visualizations, and an indication of which "
                   "of the rules in the rule base (123) are currently activated and at what strength. It is "
                   "to be understood that in an alternative embodiment, the preprocessing module and fuzzy "
                   "inference engine may instead be executed directly on the microcontroller (116) itself, "
                   "such that the host processing unit (132) is not required for inference and serves only "
                   "as a display terminal.")

    add_heading(doc, "5. Validation", level=2)
    add_para(doc, "The inventors validated an embodiment of the system against a labelled dataset of 5,000 "
                   "synthetic samples generated according to a WHO/BIS hard-threshold oracle, as well as "
                   "against a real-world, publicly available water-potability dataset. In testing, the "
                   "claimed fuzzy-inference approach achieved classification performance comparable to, "
                   "though generally somewhat lower in raw accuracy than, benchmark black-box machine-"
                   "learning classifiers (random forest, k-nearest-neighbors, and support-vector machine), "
                   "while retaining the property that every classification decision remains fully traceable "
                   "to an identifiable, standards-grounded rule — a property absent in the benchmarked "
                   "machine-learning approaches. The claimed system was further observed to produce smoother "
                   "and more physically realistic classification transitions in the boundary region between "
                   "classes, as compared with a hard-threshold classifier operating on the same input data.")

    doc.add_page_break()

    # ── Claims ───────────────────────────────────────────────────────
    add_heading(doc, "CLAIMS", level=1)
    add_para(doc, "We claim:", bold=True, space_after=10)

    add_claim(doc, 1,
        "A system for real-time water potability classification, the system comprising: "
        "a sensor array comprising a pH sensor, a turbidity sensor, a total dissolved solids sensor, "
        "a dissolved oxygen sensor, and a temperature sensor; "
        "a signal acquisition unit configured to digitize readings acquired from the sensor array; "
        "a preprocessing module configured to apply temperature compensation to at least the pH sensor "
        "reading and the dissolved oxygen sensor reading, to reject statistical outliers, and to apply a "
        "moving-average filter to the digitized readings, so as to produce a set of preprocessed crisp "
        "input values; "
        "a fuzzy inference engine of the Mamdani type, configured to: "
        "(a) fuzzify each of the preprocessed crisp input values into a corresponding degree of membership "
        "in each of a plurality of predefined linguistic terms represented by overlapping membership "
        "functions; "
        "(b) evaluate a stored rule base comprising a plurality of IF–THEN rules, each rule specifying a "
        "combination of said linguistic terms as an antecedent and a linguistic term of an output variable "
        "as a consequent, using a minimum implication operator to compute a rule activation strength for "
        "each rule; "
        "(c) aggregate the output fuzzy sets of all activated rules using a maximum operator to produce an "
        "aggregated output fuzzy set; and "
        "(d) defuzzify the aggregated output fuzzy set using a centroid-of-area computation to produce a "
        "crisp Water Potability Index; "
        "a classifier configured to map the Water Potability Index onto one of a plurality of predefined "
        "potability classes; and "
        "a display unit configured to render, in substantially real time, at least the Water Potability "
        "Index and the corresponding potability class.")

    add_claim(doc, 2,
        "The system as claimed in claim 1, wherein the plurality of predefined potability classes "
        "comprises a non-potable class, a marginal class, and a potable class, defined over "
        "non-overlapping sub-ranges of the Water Potability Index.", dependent=True)

    add_claim(doc, 3,
        "The system as claimed in claim 1, wherein each rule of the stored rule base is derived from, "
        "and traceable to, a numeric limit or guideline value specified in at least one of the World "
        "Health Organization Guidelines for Drinking-Water Quality or the Bureau of Indian Standards "
        "IS 10500 specification, such that every output of the classifier is traceable to at least one "
        "identifiable rule of the rule base.", dependent=True)

    add_claim(doc, 4,
        "The system as claimed in claim 1, wherein the temperature compensation applied to the pH "
        "sensor reading comprises adjusting the pH reading by an offset proportional to the deviation of "
        "the sensed temperature from a reference temperature, and wherein the temperature compensation "
        "applied to the dissolved oxygen sensor reading comprises scaling the dissolved oxygen reading by "
        "a ratio of a saturation value at the reference temperature to a saturation value at the sensed "
        "temperature.", dependent=True)

    add_claim(doc, 5,
        "The system as claimed in claim 1, wherein the signal acquisition unit, the preprocessing module "
        "and the fuzzy inference engine are implemented, at least in part, on a microcontroller having an "
        "integrated analog-to-digital converter and a wireless communication interface, and wherein the "
        "display unit is a web-based dashboard communicably coupled to the microcontroller.", dependent=True)

    add_claim(doc, 6,
        "The system as claimed in claim 1, wherein the display unit is further configured to render, in "
        "substantially real time, the computed degrees of membership of the preprocessed crisp input "
        "values and an indication of which rules of the stored rule base are activated and their "
        "respective activation strengths.", dependent=True)

    add_claim(doc, 7,
        "The system as claimed in claim 1, wherein the stored rule base comprises at least forty rules "
        "organized into a plurality of rule groups including at least: a group of rules each having all "
        "antecedent linguistic terms indicative of safe parameter levels and a consequent indicative of "
        "the potable class; a group of rules each having a single antecedent linguistic term sufficient, "
        "independent of other input variables, to trigger a consequent indicative of the non-potable "
        "class; and a group of rules having a consequent indicative of the marginal class.", dependent=True)

    add_claim(doc, 8,
        "A computer-implemented method for real-time water potability classification, the method "
        "comprising: "
        "acquiring raw sensor readings for at least pH, turbidity, total dissolved solids, dissolved "
        "oxygen and temperature; "
        "applying temperature compensation to at least the pH reading and the dissolved oxygen reading "
        "based on the temperature reading; "
        "rejecting statistical outliers from, and applying a moving-average filter to, the readings to "
        "produce filtered crisp input values; "
        "fuzzifying the filtered crisp input values into degrees of membership in a plurality of "
        "predefined linguistic terms; "
        "evaluating a stored rule base of IF–THEN rules using a minimum implication operator to compute "
        "a rule activation strength for each rule; "
        "aggregating the output fuzzy sets of activated rules using a maximum operator; "
        "defuzzifying the aggregated fuzzy set using a centroid-of-area computation to compute a Water "
        "Potability Index; "
        "classifying the Water Potability Index into one of a plurality of predefined potability classes; "
        "and "
        "displaying the Water Potability Index and the corresponding potability class on a real-time "
        "display interface; "
        "wherein the foregoing steps are repeated continuously so as to provide continuous, real-time "
        "monitoring of water potability.")

    add_claim(doc, 9,
        "The method as claimed in claim 8, wherein the centroid-of-area computation is performed by "
        "numerical integration of the aggregated fuzzy set over a discretized output universe of "
        "discourse comprising at least 500 discrete points.", dependent=True)

    add_claim(doc, 10,
        "The method as claimed in claim 8, further comprising selecting, via a scenario selector of the "
        "display interface, one of a plurality of predefined or live sensor-data scenarios for "
        "presentation.", dependent=True)

    doc.add_page_break()

    # ── Abstract ─────────────────────────────────────────────────────
    add_heading(doc, "ABSTRACT", level=1)
    add_para(doc, "A system and method are disclosed for real-time, interpretable classification of "
                   "water potability using low-cost multi-sensor data. A sensor array (102) acquires pH, "
                   "turbidity, total dissolved solids, dissolved oxygen and temperature readings, which are "
                   "temperature-compensated, outlier-rejected and noise-filtered by a preprocessing module "
                   "(114). A Mamdani-type fuzzy inference engine (118) fuzzifies the preprocessed readings, "
                   "evaluates a rule base (123) grounded in WHO and BIS drinking-water standards using MIN "
                   "implication, aggregates the activated rule outputs using a MAX operator, and defuzzifies "
                   "the result via the centroid-of-area method to compute a continuous Water Potability "
                   "Index (WPI) on a scale of 0 to 10. The WPI is classified into non-potable, marginal or "
                   "potable categories and rendered on a real-time dashboard (128) together with live "
                   "sensor readings, membership degrees and rule-activation information. Because every "
                   "classification is traceable to an explicit, standards-grounded rule, the invention "
                   "avoids the interpretability limitations of black-box machine-learning classifiers while "
                   "avoiding the discontinuous “cliff-edge” behavior of conventional hard-threshold "
                   "systems, and is deployable on low-cost embedded hardware.")
    add_para(doc, "Reference Figure: FIG. 1", italic=True)

    doc.add_page_break()
    add_heading(doc, "NOTES FOR THE ATTORNEY / PATENT AGENT", level=1)
    add_numbered(doc, [
        "This draft was auto-generated from the project's technical documentation (README, FIS Design "
        "Report, config.yaml, benchmark results) to accelerate preparation ahead of the internal "
        "10-September readiness target. It has not been reviewed for patentability (novelty, "
        "inventive step) against the prior art landscape and must be checked before filing.",
        "Applicant name(s), inventor name(s), address(es), nationality and priority information are "
        "placeholders and must be completed.",
        "A formal prior-art / patentability search covering existing fuzzy-logic water-quality patents "
        "and publications (e.g. USPTO, WIPO, Indian Patent Office databases) is recommended before the "
        "claims are finalized, as the claim scope here has not been narrowed against specific prior art.",
        "The claims are drafted broadly around the four disclosed elements considered most likely to be "
        "novel in combination: (i) WHO/BIS-rule-traceable Mamdani inference for potability, (ii) the "
        "specific temperature-compensation formulas for pH/DO feeding the fuzzy engine, (iii) the "
        "specific rule-base structure (grouped rule categories), and (iv) the real-time membership/rule-"
        "activation dashboard. These should be reviewed and re-prioritized by counsel.",
        "Drawings (FIG. 1–FIG. 4) are engineering-style approximations suitable as a drafting aid; "
        "formal patent-office-compliant drawings (correct margins, numbering conventions, sheet format) "
        "should be prepared by a professional draftsperson prior to filing.",
        "Consider whether a provisional specification should be filed first (to lock in a priority date "
        "ahead of any public disclosure, e.g. publication of the associated research paper) followed by "
        "a complete specification within 12 months.",
    ])

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/Patent_Draft.docx"
    doc.save(out_path)
    print(f"[*] Patent draft saved to {out_path}")


if __name__ == "__main__":
    create_patent_draft()
