import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_ppt():
    prs = Presentation()
    
    # Title Slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Fuzzy Inference System for Real-Time Water Potability"
    subtitle.text = "A Multi-Sensor Edge AI Approach\nAuthor: SC_CProject"
    
    # Slide 1: Introduction
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Introduction & Motivation"
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Problem Statement"
    p = tf.add_paragraph()
    p.text = "Traditional water quality monitoring relies on slow, expensive lab tests."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Hard threshold models create 'cliff-edge' decisions."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Proposed Solution"
    p = tf.add_paragraph()
    p.text = "A Mamdani Fuzzy Inference System (FIS) using 4 low-cost sensors."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Provides continuous, graded potability scores (WPI 0-10)."
    p.level = 1

    # Slide 2: Methodology
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = "System Architecture"
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "4-Stage Pipeline:"
    p = tf.add_paragraph()
    p.text = "1. Fuzzification (pH, Turbidity, TDS, DO)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "2. Rule Evaluation (45 WHO/BIS Rules)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "3. Aggregation (MAX operator)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "4. Defuzzification (Centroid of Area)"
    p.level = 1

    # Slide 3: Membership Functions Plot
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Fuzzy Sets: pH Example"
    img_path = "outputs/figures/mf_ph.png"
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1), Inches(1.5), width=Inches(8))

    # Slide 4: Results Plot
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Benchmark Results"
    img_path = "outputs/figures/benchmark_comparison.png"
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1), Inches(1.5), width=Inches(8))

    # Slide 5: Conclusion
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Conclusion"
    tf = slide.shapes.placeholders[1].text_frame
    tf.text = "Key Takeaways:"
    p = tf.add_paragraph()
    p.text = "FIS achieves ~60% accuracy on real-world Kaggle data (matching SVM/RF)."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Maintains 100% interpretability, essential for safety-critical systems."
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Can be deployed on low-cost edge hardware (ESP32)."
    p.level = 1

    out_path = "outputs/Water_Potability_FIS_Presentation.ppt"
    prs.save(out_path)
    print(f"[*] Presentation saved to {out_path}")

if __name__ == "__main__":
    create_ppt()
