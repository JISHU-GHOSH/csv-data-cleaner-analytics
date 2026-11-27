import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# CONSTANTS & THEME (Matching FixMyCampus PDF Exactly)
# -------------------------------------------------------------
COLOR_DARK_GREEN = RGBColor(19, 71, 49)      # #134731 Deep Forest Green
COLOR_CREAM_BG = RGBColor(245, 235, 225)     # #F5EBE1 Warm Sand / Cream
COLOR_CREAM_CARD = RGBColor(240, 228, 215)   # #F0E4D7 Cream Fill for cards
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_CHEVRON_RED = RGBColor(176, 38, 71)    # #B02647 Crimson / Magenta accent
COLOR_MUTED_TEXT = RGBColor(100, 110, 105)

FONT_TITLE = "Trebuchet MS"                  # Bold, condensed headline font
FONT_BODY = "Arial"                          # Clean modern sans-serif

CAMPUS_IMG_PATH = os.path.abspath("extracted_assets/slide_0_img_0.png")
CHART_IMG_PATH = os.path.abspath("student_analytics_plots.png")

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Helper: Set slide background
    def set_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    # Helper: Add chevrons >>> or <<<
    def add_chevrons(slide, text=">>>", left=11.5, top=1.0, font_size=32, color=COLOR_CHEVRON_RED):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(1.5), Inches(0.8))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT_TITLE
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = color

    # Helper: Add rounded card
    def add_card(slide, left, top, width, height, bg_color=COLOR_CREAM_CARD, border_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # =========================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, COLOR_CREAM_BG)

    # Campus banner at the bottom half
    if os.path.exists(CAMPUS_IMG_PATH):
        s1.shapes.add_picture(CAMPUS_IMG_PATH, Inches(0.0), Inches(4.3), width=Inches(13.333), height=Inches(3.2))

    # Top Subtitle: P Y T H O N   P R O J E C T
    tb_top = s1.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.333), Inches(0.5))
    tf_top = tb_top.text_frame
    p_top = tf_top.paragraphs[0]
    p_top.text = "P  Y  T  H  O  N     P  R  O  J  E  C  T"
    p_top.font.name = FONT_TITLE
    p_top.font.size = Pt(18)
    p_top.font.bold = True
    p_top.font.color.rgb = COLOR_DARK_GREEN
    p_top.alignment = PP_ALIGN.CENTER

    # Main Huge Title: CSVCleaner
    tb_title = s1.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(12.333), Inches(1.8))
    tf_title = tb_title.text_frame
    p_title = tf_title.paragraphs[0]
    p_title.text = "CSVCleaner"
    p_title.font.name = FONT_TITLE
    p_title.font.size = Pt(82)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_DARK_GREEN
    p_title.alignment = PP_ALIGN.CENTER

    # Subtitle: SMART CSV DATA CLEANING & ANALYTICS STUDIO
    tb_sub = s1.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(11.333), Inches(0.6))
    tf_sub = tb_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "SMART CSV DATA CLEANING & ANALYTICS STUDIO"
    p_sub.font.name = FONT_TITLE
    p_sub.font.size = Pt(17)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_DARK_GREEN
    p_sub.alignment = PP_ALIGN.CENTER

    # Middle Presented By Card (Forest Green background with white text)
    add_card(s1, 3.5, 4.2, 6.333, 2.5, COLOR_DARK_GREEN, None)
    tb_pres = s1.shapes.add_textbox(Inches(3.7), Inches(4.35), Inches(5.933), Inches(2.2))
    tf_pres = tb_pres.text_frame
    tf_pres.word_wrap = True

    p_pby = tf_pres.paragraphs[0]
    p_pby.text = "Presented by: TEAM ROCKET"
    p_pby.font.name = FONT_TITLE
    p_pby.font.size = Pt(17)
    p_pby.font.bold = True
    p_pby.font.color.rgb = COLOR_WHITE
    p_pby.alignment = PP_ALIGN.CENTER

    members = [
        "PARTH KOTHARI - 25BCON0044",
        "HARDIK UDAWAT - 25BCON0081",
        "TWISHA SRIVASTAVA - 25BCON0266",
        "JISHU GHOSH - 25BCON0022"
    ]
    for m in members:
        pm = tf_pres.add_paragraph()
        pm.text = m
        pm.font.name = FONT_TITLE
        pm.font.size = Pt(13)
        pm.font.bold = True
        pm.font.color.rgb = COLOR_CREAM_BG
        pm.alignment = PP_ALIGN.CENTER
        pm.space_before = Pt(3)

    # Chevrons
    add_chevrons(s1, ">>>", 0.6, 6.6, 32, COLOR_CHEVRON_RED)
    add_chevrons(s1, "<<<", 12.0, 5.0, 32, COLOR_CHEVRON_RED)

    # =========================================================
    # SLIDE 2: WHAT IS CSV CLEANER?
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2, COLOR_DARK_GREEN)
    add_chevrons(s2, ">>>", 9.2, 0.9, 36, COLOR_CHEVRON_RED)
    add_chevrons(s2, "<<<", 11.2, 4.8, 36, COLOR_CHEVRON_RED)

    # Title: What is \n CSV Cleaner?
    tb_w = s2.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.0), Inches(1.8))
    tf_w = tb_w.text_frame
    p_w1 = tf_w.paragraphs[0]
    p_w1.text = "What is"
    p_w1.font.name = FONT_TITLE
    p_w1.font.size = Pt(40)
    p_w1.font.bold = True
    p_w1.font.color.rgb = COLOR_WHITE

    p_w2 = tf_w.add_paragraph()
    p_w2.text = "CSV Cleaner?"
    p_w2.font.name = FONT_TITLE
    p_w2.font.size = Pt(64)
    p_w2.font.bold = True
    p_w2.font.color.rgb = COLOR_CREAM_BG
    p_w2.space_before = Pt(0)

    # Card 1: Main features (Dark green with cream border)
    add_card(s2, 0.8, 2.5, 10.2, 3.2, COLOR_DARK_GREEN, COLOR_CREAM_CARD)
    tb_c1 = s2.shapes.add_textbox(Inches(1.1), Inches(2.7), Inches(9.6), Inches(2.8))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True

    c1_bullets = [
        "CSV Cleaner is an automated data sanitization & analytics system.",
        "It allows users to upload dirty CSV datasets and fix them in 1-click.",
        "Deduplicates rows, trims spaces, and standardizes column headers.",
        "Imputes missing values with statistical median, mean, or mode.",
        "Filters numerical outliers using Tukey's 1.5x IQR formula.",
        "Features a dual interface: Tkinter Desktop GUI + Flask Cloud Web App."
    ]
    for idx, b in enumerate(c1_bullets):
        pb = tf_c1.paragraphs[0] if idx == 0 else tf_c1.add_paragraph()
        pb.text = f"• {b}"
        pb.font.name = FONT_BODY
        pb.font.size = Pt(14)
        pb.font.color.rgb = COLOR_WHITE
        pb.space_before = Pt(4)

    # Card 2: Main Goal pill
    add_card(s2, 0.8, 6.0, 11.733, 1.0, COLOR_CREAM_BG, None)
    tb_goal = s2.shapes.add_textbox(Inches(1.1), Inches(6.15), Inches(11.1), Inches(0.7))
    tf_goal = tb_goal.text_frame
    p_goal = tf_goal.paragraphs[0]
    p_goal.text = "Main Goal: To eliminate the 80% manual data wrangling bottleneck through an automated, reproducible Python platform."
    p_goal.font.name = FONT_TITLE
    p_goal.font.size = Pt(15)
    p_goal.font.bold = True
    p_goal.font.color.rgb = COLOR_DARK_GREEN

    # =========================================================
    # SLIDE 3: PROBLEM >>> OBJECTIVES (Split Screen)
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3, COLOR_CREAM_BG)

    # Right half dark green background
    right_bg = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.666), 0, Inches(6.667), Inches(7.5))
    right_bg.fill.solid()
    right_bg.fill.fore_color.rgb = COLOR_DARK_GREEN
    right_bg.line.fill.background()

    # Left: PROBLEM
    tb_pl = s3.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(5.4), Inches(1.1))
    tf_pl = tb_pl.text_frame
    p_pl = tf_pl.paragraphs[0]
    p_pl.text = "PROBLEM"
    p_pl.font.name = FONT_TITLE
    p_pl.font.size = Pt(54)
    p_pl.font.bold = True
    p_pl.font.color.rgb = COLOR_DARK_GREEN

    add_chevrons(s3, ">>>", 5.4, 0.7, 36, COLOR_CHEVRON_RED)

    tb_pbody = s3.shapes.add_textbox(Inches(0.6), Inches(1.6), Inches(5.6), Inches(5.4))
    tf_pb = tb_pbody.text_frame
    tf_pb.word_wrap = True

    p_phead = tf_pb.paragraphs[0]
    p_phead.text = "Problems in Traditional Data Preparation"
    p_phead.font.name = FONT_TITLE
    p_phead.font.size = Pt(14)
    p_phead.font.bold = True
    p_phead.font.color.rgb = COLOR_DARK_GREEN

    prob_bullets = [
        "No standardized column headers; leading spaces break code.",
        "Redundant duplicate records distort statistics and models.",
        "Missing values (NaN, empty cells) trigger runtime errors.",
        "Extreme statistical outliers heavily bias analytical results.",
        "Spreadsheet editors lack automated, timestamped audit logs.",
        "Manual cleaning in Excel is tedious, slow, and error-prone."
    ]
    for b in prob_bullets:
        pb = tf_pb.add_paragraph()
        pb.text = f"• {b}"
        pb.font.name = FONT_BODY
        pb.font.size = Pt(11.5)
        pb.font.color.rgb = COLOR_DARK_GREEN
        pb.space_before = Pt(4)

    p_sol = tf_pb.add_paragraph()
    p_sol.text = "Our Solution: A modular Python application that automates data sanitization, health scoring, and statistical visualization."
    p_sol.font.name = FONT_TITLE
    p_sol.font.size = Pt(12)
    p_sol.font.bold = True
    p_sol.font.color.rgb = COLOR_DARK_GREEN
    p_sol.space_before = Pt(10)

    # Right: OBJECTIVES
    tb_pr = s3.shapes.add_textbox(Inches(7.2), Inches(0.4), Inches(5.6), Inches(1.1))
    tf_pr = tb_pr.text_frame
    p_pr = tf_pr.paragraphs[0]
    p_pr.text = "OBJECTIVES"
    p_pr.font.name = FONT_TITLE
    p_pr.font.size = Pt(54)
    p_pr.font.bold = True
    p_pr.font.color.rgb = COLOR_CREAM_BG

    tb_obody = s3.shapes.add_textbox(Inches(7.2), Inches(1.6), Inches(5.6), Inches(5.4))
    tf_ob = tb_obody.text_frame
    tf_ob.word_wrap = True

    obj_bullets = [
        "1. Develop a 1-click automated dataset sanitization pipeline.",
        "2. Standardize column headers to lowercase snake_case.",
        "3. Detect and drop duplicate rows with zero data corruption.",
        "4. Provide statistically sound median, mean, and mode imputation.",
        "5. Filter statistical anomalies using Tukey's 1.5x IQR method.",
        "6. Compute a real-time composite 0–100% Data Quality Health Score.",
        "7. Provide dual access: Offline Desktop GUI & Cloud Web App."
    ]
    for idx, b in enumerate(obj_bullets):
        pb = tf_ob.paragraphs[0] if idx == 0 else tf_ob.add_paragraph()
        pb.text = b
        pb.font.name = FONT_BODY
        pb.font.size = Pt(12)
        pb.font.color.rgb = COLOR_WHITE
        pb.space_before = Pt(6)

    # =========================================================
    # SLIDE 4: SYSTEM DESIGN
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4, COLOR_DARK_GREEN)
    add_chevrons(s4, ">>>", 0.6, 6.6, 32, COLOR_CHEVRON_RED)

    tb_s4 = s4.shapes.add_textbox(Inches(0.6), Inches(0.5), Inches(8.0), Inches(1.2))
    tf_s4 = tb_s4.text_frame
    p_s4 = tf_s4.paragraphs[0]
    p_s4.text = "System design"
    p_s4.font.name = FONT_TITLE
    p_s4.font.size = Pt(54)
    p_s4.font.bold = True
    p_s4.font.color.rgb = COLOR_CREAM_BG

    layers_s4 = [
        ("Presentation\nlayer:", [
            "Tkinter Desktop GUI",
            "HTML5 & CSS3 Web UI",
            "Responsive iLovePDF Theme",
            "Interactive Chart.js Canvas",
            "Interactive Treeview Spreadsheet"
        ]),
        ("Application\nlayer", [
            "Python 3.13 Core",
            "Flask REST API Services",
            "Cleaner Transformation Engine",
            "State Manager (LIFO Undo Stack)",
            "Tukey 1.5x IQR Outlier Logic"
        ]),
        ("Data / Analytics\nlayer", [
            "Pandas Tabular DataFrames",
            "NumPy Vectorized Arrays",
            "Matplotlib Statistical Figures",
            "In-memory BytesIO Streaming",
            "CSV, JSON & Text Exporters"
        ])
    ]

    card_w4 = 3.65
    for idx, (title, items) in enumerate(layers_s4):
        left = 0.8 + idx * (card_w4 + 0.39)
        add_card(s4, left, 1.8, card_w4, 4.6, COLOR_CREAM_BG, None)
        tb = s4.shapes.add_textbox(Inches(left + 0.2), Inches(2.0), Inches(card_w4 - 0.4), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK_GREEN

        for it in items:
            pit = tf.add_paragraph()
            pit.text = f"• {it}"
            pit.font.name = FONT_BODY
            pit.font.size = Pt(13)
            pit.font.color.rgb = COLOR_DARK_GREEN
            pit.space_before = Pt(8)

    # =========================================================
    # SLIDE 5: METHODOLOGY
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5, COLOR_CREAM_BG)
    add_chevrons(s5, ">>>", 11.5, 0.7, 36, COLOR_CHEVRON_RED)

    tb_s5 = s5.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.0), Inches(1.2))
    tf_s5 = tb_s5.text_frame
    p_s5 = tf_s5.paragraphs[0]
    p_s5.text = "METHODOLOGY"
    p_s5.font.name = FONT_TITLE
    p_s5.font.size = Pt(56)
    p_s5.font.bold = True
    p_s5.font.color.rgb = COLOR_DARK_GREEN

    meth_steps = [
        ("Requirement analysis", [
            "Identify common spreadsheet flaws.",
            "Understand student and ML researcher needs.",
            "Finalize the core cleaning features."
        ]),
        ("System & state design", [
            "Design modular 4-tier application architecture.",
            "Formulate LIFO undo snapshot stack.",
            "Prepare user workflows and REST endpoints."
        ]),
        ("Core algorithm development", [
            "Implement regex header normalization.",
            "Build median, mean, and mode imputation.",
            "Formulate Tukey 1.5x IQR outlier bounds."
        ]),
        ("Health & metrics engine", [
            "Formulate composite 0–100% Quality Score.",
            "Assemble 5-number statistical summaries.",
            "Build timestamped audit logging system."
        ]),
        ("Dual frontend development", [
            "Build offline desktop GUI using Tkinter.",
            "Design responsive web layouts using CSS3.",
            "Implement client-side sorting & pagination."
        ]),
        ("Integration & testing", [
            "Connect web frontend with Flask backend.",
            "Execute 24-case automated unit test suite.",
            "Deploy live to Vercel serverless cloud."
        ])
    ]

    col_w5 = 5.7
    for idx, (title, points) in enumerate(meth_steps):
        col = idx // 3
        row = idx % 3
        left = 0.8 + col * (col_w5 + 0.333)
        top = 1.7 + row * 1.8

        tb = s5.shapes.add_textbox(Inches(left), Inches(top), Inches(col_w5), Inches(1.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f"●  {title}"
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK_GREEN

        for pt in points:
            ppt = tf.add_paragraph()
            ppt.text = f"    • {pt}"
            ppt.font.name = FONT_BODY
            ppt.font.size = Pt(11)
            ppt.font.color.rgb = COLOR_DARK_GREEN
            ppt.space_before = Pt(2)

    # =========================================================
    # SLIDE 6: TOOLS & TECHNOLOGIES
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6, COLOR_DARK_GREEN)

    tb_s6 = s6.shapes.add_textbox(Inches(0.6), Inches(0.5), Inches(10.0), Inches(1.2))
    tf_s6 = tb_s6.text_frame
    p_s6 = tf_s6.paragraphs[0]
    p_s6.text = "TOOLS & TECHNOLOGIES"
    p_s6.font.name = FONT_TITLE
    p_s6.font.size = Pt(54)
    p_s6.font.bold = True
    p_s6.font.color.rgb = COLOR_CREAM_BG

    card_tools = [
        ("Core Stack", [
            ("Python 3.13", "Main programming language and runtime environment."),
            ("Pandas", "Tabular DataFrame manipulation, deduplication, and grouping."),
            ("NumPy", "Vectorized array calculations and IQR percentile thresholding."),
            ("Matplotlib", "Statistical figures: histograms, boxplots, and bar charts."),
            ("Tkinter", "Standard desktop graphical user interface with Treeview."),
            ("Flask", "Lightweight WSGI microservice framework for REST APIs.")
        ]),
        ("Ecosystem & Libraries", [
            ("Chart.js", "Client-side interactive canvas charting in the browser."),
            ("unittest", "Automated test suite covering 24 comprehensive test cases."),
            ("io & os", "In-memory file stream management (BytesIO, StringIO)."),
            ("json", "Structured JSON serialization for records export."),
            ("Vercel", "Serverless cloud infrastructure and global edge deployment."),
            ("Git & GitHub", "Source version control and automated deployment pipeline.")
        ])
    ]

    card_w6 = 5.7
    for idx, (title, items) in enumerate(card_tools):
        left = 0.8 + idx * (card_w6 + 0.333)
        add_card(s6, left, 1.8, card_w6, 5.0, COLOR_CREAM_BG, None)
        tb = s6.shapes.add_textbox(Inches(left + 0.2), Inches(2.0), Inches(card_w6 - 0.4), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True

        for i, (tool, desc) in enumerate(items):
            pt = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            pt.text = f"• {tool} – {desc}"
            pt.font.name = FONT_BODY
            pt.font.size = Pt(12)
            pt.font.color.rgb = COLOR_DARK_GREEN
            pt.space_before = Pt(6)

    # =========================================================
    # SLIDE 7: ROLES & RESPONSIBILITIES
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7, COLOR_CREAM_BG)
    add_chevrons(s7, "<<<", 11.5, 0.7, 36, COLOR_CHEVRON_RED)

    tb_s7 = s7.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(10.0), Inches(1.2))
    tf_s7 = tb_s7.text_frame
    p_s7 = tf_s7.paragraphs[0]
    p_s7.text = "ROLES & RESPONSIBILITIES"
    p_s7.font.name = FONT_TITLE
    p_s7.font.size = Pt(54)
    p_s7.font.bold = True
    p_s7.font.color.rgb = COLOR_DARK_GREEN

    members_data = [
        ("Parth Kothari", "25BCON0044", [
            "Responsible for core data cleaning pipelines in cleaner.py.",
            "Engineered regex header standardization and whitespace stripping.",
            "Formulated rule-based missing value imputation (median/mean/mode)."
        ]),
        ("Hardik Udawat", "25BCON0081", [
            "Built native desktop graphical interface in main.py using Tkinter.",
            "Engineered interactive Treeview data spreadsheet with row indexing.",
            "Integrated Matplotlib statistical charts into GUI and demo pipelines."
        ]),
        ("Twisha Srivastava", "25BCON0266", [
            "Architected and implemented 24-case automated test suite in tests/.",
            "Developed descriptive statistical summary engine in stats_engine.py.",
            "Authored project technical documentation and SRS requirements."
        ]),
        ("Jishu Ghosh", "25BCON0022", [
            "Designed full-stack web architecture and Flask REST API endpoints.",
            "Developed responsive web application UI with client-side sorting & search.",
            "Configured Vercel serverless cloud deployment and production hosting."
        ])
    ]

    card_w7 = 5.7
    for idx, (name, reg, tasks) in enumerate(members_data):
        col = idx % 2
        row = idx // 2
        left = 0.8 + col * (card_w7 + 0.333)
        top = 1.8 + row * 2.6

        # Circular Badge on Left of card
        badge = s7.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top + 0.2), Inches(1.4), Inches(1.4))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_DARK_GREEN
        badge.line.fill.background()

        # Initials inside badge
        tb_ini = s7.shapes.add_textbox(Inches(left), Inches(top + 0.5), Inches(1.4), Inches(0.8))
        tf_ini = tb_ini.text_frame
        p_ini = tf_ini.paragraphs[0]
        initials = "".join([part[0] for part in name.split()])
        p_ini.text = initials
        p_ini.font.name = FONT_TITLE
        p_ini.font.size = Pt(20)
        p_ini.font.bold = True
        p_ini.font.color.rgb = COLOR_WHITE
        p_ini.alignment = PP_ALIGN.CENTER

        # Text Details on Right
        tb = s7.shapes.add_textbox(Inches(left + 1.6), Inches(top), Inches(card_w7 - 1.6), Inches(2.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f"{name} ({reg})"
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK_GREEN

        for t in tasks:
            pt = tf.add_paragraph()
            pt.text = f"• {t}"
            pt.font.name = FONT_BODY
            pt.font.size = Pt(10.5)
            pt.font.color.rgb = COLOR_DARK_GREEN
            pt.space_before = Pt(2)

    # =========================================================
    # SLIDE 8: PROJECT STRUCTURE & PYTHON BACKEND
    # =========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8, COLOR_DARK_GREEN)
    add_chevrons(s8, ">>>", 11.5, 6.2, 32, COLOR_CHEVRON_RED)

    tb_s8 = s8.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.0), Inches(1.2))
    tf_s8 = tb_s8.text_frame
    p_s8 = tf_s8.paragraphs[0]
    p_s8.text = "PROJECT STRUCTURE & PYTHON BACKEND"
    p_s8.font.name = FONT_TITLE
    p_s8.font.size = Pt(46)
    p_s8.font.bold = True
    p_s8.font.color.rgb = COLOR_CREAM_BG

    # Left card: Directory Tree
    add_card(s8, 0.8, 1.8, 5.2, 5.0, COLOR_DARK_GREEN, COLOR_CREAM_CARD)
    tb_tree = s8.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(4.8), Inches(4.7))
    tf_tree = tb_tree.text_frame
    tf_tree.word_wrap = True

    p_th = tf_tree.paragraphs[0]
    p_th.text = "Project Architecture Tree"
    p_th.font.name = FONT_TITLE
    p_th.font.size = Pt(14)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_CREAM_BG

    tree_lines = [
        "csv-cleaner-analytics/",
        "├── app.py                (Flask backend & API)",
        "├── main.py               (Tkinter desktop GUI)",
        "├── run_tests.py          (Automated test runner)",
        "├── core/",
        "│   ├── cleaner.py        (Cleaning algorithms)",
        "│   ├── data_manager.py   (State & undo stack)",
        "│   ├── stats_engine.py   (Summary statistics)",
        "│   ├── exporter.py       (CSV, JSON, TXT)",
        "│   └── audit_logger.py   (Action logging)",
        "├── static/               (style.css, app.js)",
        "├── templates/            (index.html)",
        "├── tests/                (24 unit test cases)",
        "└── vercel.json           (Cloud configuration)"
    ]
    for tl in tree_lines:
        ptl = tf_tree.add_paragraph()
        ptl.text = tl
        ptl.font.name = "Consolas"
        ptl.font.size = Pt(10)
        ptl.font.color.rgb = COLOR_WHITE
        ptl.space_before = Pt(1)

    # Right column: Concepts
    tb_c = s8.shapes.add_textbox(Inches(6.4), Inches(1.8), Inches(6.0), Inches(5.0))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p_ch = tf_c.paragraphs[0]
    p_ch.text = "IMPORTANT PYTHON CONCEPTS USED"
    p_ch.font.name = FONT_TITLE
    p_ch.font.size = Pt(20)
    p_ch.font.bold = True
    p_ch.font.color.rgb = COLOR_CREAM_BG

    concepts = [
        "Object-Oriented Programming (Classes & DataManager encapsulation).",
        "Vectorized array processing with NumPy (zero loop overhead).",
        "Tabular indexing, filtering & grouping with Pandas.",
        "LIFO Stack data structures for Multi-Level Undo operations.",
        "In-memory stream buffers (io.StringIO, io.BytesIO).",
        "Decorators and REST routing in Flask (@app.route).",
        "Automated unit testing with Python unittest.TestCase.",
        "Defensive exception handling (try / except) across all file I/O."
    ]
    for c in concepts:
        pc = tf_c.add_paragraph()
        pc.text = f"• {c}"
        pc.font.name = FONT_BODY
        pc.font.size = Pt(12)
        pc.font.color.rgb = COLOR_WHITE
        pc.space_before = Pt(5)

    # =========================================================
    # SLIDE 9: DATA CLEANING, STATE & QUALITY SCORING
    # =========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9, COLOR_CREAM_BG)
    add_chevrons(s9, "<<<", 11.5, 0.7, 36, COLOR_CHEVRON_RED)

    tb_s9 = s9.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(11.0), Inches(1.2))
    tf_s9 = tb_s9.text_frame
    p_s9 = tf_s9.paragraphs[0]
    p_s9.text = "DATA CLEANING, STATE & QUALITY SCORING"
    p_s9.font.name = FONT_TITLE
    p_s9.font.size = Pt(44)
    p_s9.font.bold = True
    p_s9.font.color.rgb = COLOR_DARK_GREEN

    sec_s9 = [
        ("Data Cleaning Pipeline", [
            "Converts all headers to standardized lowercase snake_case.",
            "Strips extraneous spaces across all text/object columns.",
            "Detects duplicate rows and drops them while logging exact counts.",
            "Imputes missing numerical values with Median (skewed) or Mean (symmetric).",
            "Imputes categorical text columns with Mode (most frequent category).",
            "Filters statistical outliers using Tukey's 1.5x IQR boundaries."
        ]),
        ("State Management & Undo Stack", [
            "Implements snapshot Memento design pattern with in-memory LIFO stack.",
            "Uses deepcopy isolation so prior states remain completely untampered.",
            "Maintains a bounded stack of 15 states to protect RAM from exhaustion.",
            "Allows users to hit 'Undo' to revert operations instantly.",
            "Provides 'Reset' to restore pristine raw dataset from disk anytime."
        ]),
        ("0–100% Quality Scoring Engine", [
            "Completeness (50% weight): 1.0 - (Missing Cells / Total Grid Cells).",
            "Uniqueness (30% weight): 1.0 - (Duplicate Rows / Total Rows).",
            "Header Hygiene (20% weight): 1.0 if clean snake_case, else 0.80.",
            "Dynamic color progress bar: Red (<60%), Amber (60–84%), Green (≥85%).",
            "Gives users instant quantitative feedback before exporting data."
        ])
    ]

    card_w9 = 3.65
    for idx, (title, points) in enumerate(sec_s9):
        left = 0.8 + idx * (card_w9 + 0.39)
        add_card(s9, left, 1.8, card_w9, 5.0, COLOR_CREAM_BG, COLOR_DARK_GREEN)
        tb = s9.shapes.add_textbox(Inches(left + 0.15), Inches(1.95), Inches(card_w9 - 0.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK_GREEN

        for pt in points:
            ppt = tf.add_paragraph()
            ppt.text = f"• {pt}"
            ppt.font.name = FONT_BODY
            ppt.font.size = Pt(10.5)
            ppt.font.color.rgb = COLOR_DARK_GREEN
            ppt.space_before = Pt(4)

    # =========================================================
    # SLIDE 10: RESULTS (Visual Showcase)
    # =========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10, COLOR_DARK_GREEN)

    tb_s10 = s10.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.0), Inches(1.2))
    tf_s10 = tb_s10.text_frame
    p_s10 = tf_s10.paragraphs[0]
    p_s10.text = "RESULTS"
    p_s10.font.name = FONT_TITLE
    p_s10.font.size = Pt(56)
    p_s10.font.bold = True
    p_s10.font.color.rgb = COLOR_CREAM_BG

    # Embed Chart Image in Top Center
    if os.path.exists(CHART_IMG_PATH):
        s10.shapes.add_picture(CHART_IMG_PATH, Inches(0.8), Inches(1.7), width=Inches(11.733), height=Inches(3.3))

    # Three summary result cards underneath
    res_cards = [
        ("Cloud Web Application", "Deployed live on Vercel at csv-data-cleaner-analytics.vercel.app with iLovePDF-inspired theme, real-time search, sorting, and pagination."),
        ("Desktop GUI Application", "Fully functional native Tkinter desktop interface with Treeview spreadsheet view, file dialogs, and embedded Matplotlib visualizer."),
        ("Automated Quality Audit", "Generates downloadable cleaning_audit_report.txt documenting every applied transformation, dropped rows, and imputed values.")
    ]
    card_w10 = 3.65
    for idx, (title, desc) in enumerate(res_cards):
        left = 0.8 + idx * (card_w10 + 0.39)
        add_card(s10, left, 5.2, card_w10, 1.6, COLOR_CREAM_BG, None)
        tb = s10.shapes.add_textbox(Inches(left + 0.15), Inches(5.3), Inches(card_w10 - 0.3), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_DARK_GREEN
        p2.space_before = Pt(3)

    # =========================================================
    # SLIDE 11: TESTING (Table & Verification)
    # =========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11, COLOR_DARK_GREEN)
    add_chevrons(s11, ">>>", 0.6, 6.4, 32, COLOR_CHEVRON_RED)

    tb_s11 = s11.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.0), Inches(1.2))
    tf_s11 = tb_s11.text_frame
    p_s11 = tf_s11.paragraphs[0]
    p_s11.text = "TESTING"
    p_s11.font.name = FONT_TITLE
    p_s11.font.size = Pt(56)
    p_s11.font.bold = True
    p_s11.font.color.rgb = COLOR_CREAM_BG

    # Testing Table Card (Left & Right Cards)
    test_cases_left = [
        ("Standardize headers", "Standardized lowercase snake_case headers"),
        ("Duplicate row detection", "Redundant rows identified & removed"),
        ("Median numeric imputation", "Missing age/marks filled with median"),
        ("Mode categorical imputation", "Missing department filled with mode"),
        ("IQR outlier removal", "Extreme anomalies outside whiskers removed")
    ]
    test_cases_right = [
        ("Multi-level undo operation", "Prior DataFrame state safely restored"),
        ("Data Quality Score formula", "0–100% composite index accurately computed"),
        ("Invalid file upload", "Graceful error message returned (zero crash)"),
        ("Export to JSON records", "Valid JSON stream generated and downloaded"),
        ("Export to CSV format", "Standard RFC-4180 CSV generated and downloaded")
    ]

    add_card(s11, 1.0, 1.8, 5.4, 4.3, COLOR_CREAM_BG, None)
    tb_tl = s11.shapes.add_textbox(Inches(1.2), Inches(1.95), Inches(5.0), Inches(4.0))
    tf_tl = tb_tl.text_frame
    tf_tl.word_wrap = True

    p_thl = tf_tl.paragraphs[0]
    p_thl.text = "Test Case                        Expected Result"
    p_thl.font.name = FONT_TITLE
    p_thl.font.size = Pt(13)
    p_thl.font.bold = True
    p_thl.font.color.rgb = COLOR_DARK_GREEN

    for tc, er in test_cases_left:
        p = tf_tl.add_paragraph()
        p.text = f"✔ {tc}\n   ➔ {er}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_DARK_GREEN
        p.space_before = Pt(4)

    add_card(s11, 6.9, 1.8, 5.4, 4.3, COLOR_CREAM_BG, None)
    tb_tr = s11.shapes.add_textbox(Inches(7.1), Inches(1.95), Inches(5.0), Inches(4.0))
    tf_tr = tb_tr.text_frame
    tf_tr.word_wrap = True

    p_thr = tf_tr.paragraphs[0]
    p_thr.text = "Test Case                        Expected Result"
    p_thr.font.name = FONT_TITLE
    p_thr.font.size = Pt(13)
    p_thr.font.bold = True
    p_thr.font.color.rgb = COLOR_DARK_GREEN

    for tc, er in test_cases_right:
        p = tf_tr.add_paragraph()
        p.text = f"✔ {tc}\n   ➔ {er}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_DARK_GREEN
        p.space_before = Pt(4)

    # Bottom summary pill
    add_card(s11, 1.0, 6.3, 11.3, 0.7, COLOR_CREAM_CARD, None)
    tb_ts = s11.shapes.add_textbox(Inches(1.2), Inches(6.38), Inches(10.9), Inches(0.5))
    tf_ts = tb_ts.text_frame
    p_ts = tf_ts.paragraphs[0]
    p_ts.text = "All 24 automated unit tests passed with 0 errors in 0.066s execution time via 'python run_tests.py'."
    p_ts.font.name = FONT_TITLE
    p_ts.font.size = Pt(12)
    p_ts.font.bold = True
    p_ts.font.color.rgb = COLOR_DARK_GREEN
    p_ts.alignment = PP_ALIGN.CENTER

    # =========================================================
    # SLIDE 12: CONCLUSION
    # =========================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12, COLOR_DARK_GREEN)
    add_chevrons(s12, ">>>", 0.6, 0.4, 32, COLOR_CHEVRON_RED)
    add_chevrons(s12, "<<<", 11.8, 3.6, 32, COLOR_CHEVRON_RED)

    tb_s12 = s12.shapes.add_textbox(Inches(1.5), Inches(0.8), Inches(10.333), Inches(1.2))
    tf_s12 = tb_s12.text_frame
    p_s12 = tf_s12.paragraphs[0]
    p_s12.text = "CONCLUSION"
    p_s12.font.name = FONT_TITLE
    p_s12.font.size = Pt(64)
    p_s12.font.bold = True
    p_s12.font.color.rgb = COLOR_CREAM_BG
    p_s12.alignment = PP_ALIGN.CENTER

    tb_cbody = s12.shapes.add_textbox(Inches(1.8), Inches(2.2), Inches(9.733), Inches(4.5))
    tf_cb = tb_cbody.text_frame
    tf_cb.word_wrap = True

    concl_points = [
        "CSVCleaner provides a centralized, automated digital platform for dataset sanitization and statistical analytics.",
        "The project demonstrates the practical application of Python programming, Pandas data wrangling, NumPy vectorized math, and Matplotlib figure plotting.",
        "It successfully eliminates the 80% data wrangling bottleneck by transforming messy raw files into clean, analysis-ready datasets in milliseconds.",
        "Introduced an innovative 0–100% Data Quality Metric that delivers instant quantitative visibility into dataset hygiene.",
        "Verified with 24 automated unit tests and deployed live to Vercel cloud infrastructure for public academic evaluation."
    ]
    for idx, cp in enumerate(concl_points):
        p = tf_cb.paragraphs[0] if idx == 0 else tf_cb.add_paragraph()
        p.text = f"• {cp}"
        p.font.name = FONT_BODY
        p.font.size = Pt(16)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(14)

    # =========================================================
    # SLIDE 13: REFERENCES
    # =========================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13, COLOR_CREAM_BG)
    add_chevrons(s13, ">>>", 0.6, 0.4, 32, COLOR_CHEVRON_RED)

    tb_s13 = s13.shapes.add_textbox(Inches(1.5), Inches(0.8), Inches(10.333), Inches(1.2))
    tf_s13 = tb_s13.text_frame
    p_s13 = tf_s13.paragraphs[0]
    p_s13.text = "REFERENCES"
    p_s13.font.name = FONT_TITLE
    p_s13.font.size = Pt(64)
    p_s13.font.bold = True
    p_s13.font.color.rgb = COLOR_DARK_GREEN
    p_s13.alignment = PP_ALIGN.CENTER

    tb_rbody = s13.shapes.add_textbox(Inches(1.5), Inches(2.3), Inches(10.333), Inches(4.5))
    tf_rb = tb_rbody.text_frame
    tf_rb.word_wrap = True

    ref_items = [
        ("Python Software Foundation", "Python 3.13 Documentation.", "https://docs.python.org/3/"),
        ("Pandas Development Team", "pandas: Powerful Python Data Analysis Toolkit.", "https://pandas.pydata.org/"),
        ("NumPy Developers", "NumPy: Fundamental Package for Scientific Computing with Python.", "https://numpy.org/"),
        ("Matplotlib Development Team", "Matplotlib: Visualization with Python.", "https://matplotlib.org/"),
        ("Pallets Projects", "Flask Documentation (Web Development with Python).", "https://flask.palletsprojects.com/"),
        ("John W. Tukey", "Exploratory Data Analysis (Tukey IQR Outlier Standard).", "Addison-Wesley, 1977.")
    ]
    for idx, (org, title, url) in enumerate(ref_items):
        p = tf_rb.paragraphs[0] if idx == 0 else tf_rb.add_paragraph()
        p.text = f"• {org}, {title} {url}"
        p.font.name = FONT_BODY
        p.font.size = Pt(14.5)
        p.font.color.rgb = COLOR_DARK_GREEN
        p.space_before = Pt(12)

    # =========================================================
    # SLIDE 14: THANK YOU
    # =========================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_bg(s14, COLOR_CREAM_BG)
    add_chevrons(s14, ">>>", 0.6, 0.6, 40, COLOR_CHEVRON_RED)
    add_chevrons(s14, "<<<", 12.0, 5.6, 40, COLOR_CHEVRON_RED)

    # Huge THANK YOU
    tb_ty = s14.shapes.add_textbox(Inches(0.6), Inches(2.2), Inches(6.5), Inches(3.2))
    tf_ty = tb_ty.text_frame
    p_t1 = tf_ty.paragraphs[0]
    p_t1.text = "THANK"
    p_t1.font.name = FONT_TITLE
    p_t1.font.size = Pt(92)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_DARK_GREEN

    p_t2 = tf_ty.add_paragraph()
    p_t2.text = "YOU"
    p_t2.font.name = FONT_TITLE
    p_t2.font.size = Pt(92)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_DARK_GREEN
    p_t2.space_before = Pt(0)

    # Right side: Team Rocket Info
    tb_rinfo = s14.shapes.add_textbox(Inches(6.6), Inches(2.0), Inches(6.0), Inches(4.5))
    tf_ri = tb_rinfo.text_frame
    tf_ri.word_wrap = True

    p_rt = tf_ri.paragraphs[0]
    p_rt.text = "TEAM ROCKET"
    p_rt.font.name = FONT_TITLE
    p_rt.font.size = Pt(28)
    p_rt.font.bold = True
    p_rt.font.color.rgb = COLOR_CHEVRON_RED

    p_rp = tf_ri.add_paragraph()
    p_rp.text = "CSV Data Cleaner & Analytics Studio"
    p_rp.font.name = FONT_TITLE
    p_rp.font.size = Pt(16)
    p_rp.font.bold = True
    p_rp.font.color.rgb = COLOR_DARK_GREEN
    p_rp.space_before = Pt(4)

    mems_14 = [
        "Parth Kothari (25BCON0044)",
        "Hardik Udawat (25BCON0081)",
        "Twisha Srivastava (25BCON0266)",
        "Jishu Ghosh (25BCON0022)"
    ]
    for m in mems_14:
        pm = tf_ri.add_paragraph()
        pm.text = f"• {m}"
        pm.font.name = FONT_BODY
        pm.font.size = Pt(13)
        pm.font.color.rgb = COLOR_DARK_GREEN
        pm.space_before = Pt(4)

    p_rlive = tf_ri.add_paragraph()
    p_rlive.text = "Live Deployment: https://csv-data-cleaner-analytics.vercel.app\nGitHub: https://github.com/JISHU-GHOSH/csv-data-cleaner-analytics"
    p_rlive.font.name = FONT_TITLE
    p_rlive.font.size = Pt(11.5)
    p_rlive.font.bold = True
    p_rlive.font.color.rgb = COLOR_DARK_GREEN
    p_rlive.space_before = Pt(12)

    # Save presentation
    output_filename = "CSV_Cleaner_14_Pages_Presentation.pptx"
    prs.save(output_filename)
    print(f"14-page presentation saved successfully to: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    create_deck()
