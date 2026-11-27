import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

LOGO_IMG = os.path.abspath("extracted_assets/slide_0_img_6.jpg")
CHART_IMG = os.path.abspath("student_analytics_plots.png")

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_page_number_to_section(section, start_type="arabic", start_num=1):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    if start_type == "roman":
        pgNumType.set(qn('w:fmt'), 'romanLower')
    else:
        pgNumType.set(qn('w:fmt'), 'decimal')
    if start_num is not None:
        pgNumType.set(qn('w:start'), str(start_num))

    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    
    # Insert PAGE field XML
    run = p.add_run()
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

def build_report():
    doc = docx.Document()

    # -------------------------------------------------------------
    # PAGE SETUP & STYLES (Strict A4, Margins: T=1", B=1", L=1.5", R=1")
    # -------------------------------------------------------------
    for s in doc.sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.5)
        s.right_margin = Inches(1.0)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def add_p(text, bold=False, italic=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, font_name="Times New Roman"):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = font_name
        run.font.size = Pt(size)
        return p

    def add_chapter_title(num_str, title_str):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(18)
        p1.paragraph_format.space_after = Pt(6)
        r1 = p1.add_run(num_str.upper())
        r1.bold = True
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(18)

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(18)
        r2 = p2.add_run(title_str.upper())
        r2.bold = True
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(16)

    def add_h1(heading_str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(heading_str)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16)

    def add_h2(heading_str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(heading_str)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)

    def add_h3(heading_str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(heading_str)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    def add_bullet(lead_bold, text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5

        r_bullet = p.add_run("• ")
        r_bullet.bold = True
        r_bullet.font.name = 'Times New Roman'
        r_bullet.font.size = Pt(12)

        if lead_bold:
            r_lead = p.add_run(lead_bold + " ")
            r_lead.bold = True
            r_lead.font.name = 'Times New Roman'
            r_lead.font.size = Pt(12)

        r_text = p.add_run(text)
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(12)

    # -------------------------------------------------------------
    # 1. COVER / TITLE PAGE (Unnumbered Section)
    # -------------------------------------------------------------
    sec_cover = doc.sections[0]
    
    add_p("A MAJOR PROJECT REPORT", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p("on", italic=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
    add_p("“CSV DATA CLEANER & ANALYTICS STUDIO”", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)

    add_p("Submitted in partial fulfillment of the requirements for the award of the degree of", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p("BACHELOR OF TECHNOLOGY", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p("in", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p("COMPUTER SCIENCE AND ENGINEERING", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=14)

    # JECRC Logo
    if os.path.exists(LOGO_IMG):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(14)
        run_logo = p_logo.add_run()
        run_logo.add_picture(LOGO_IMG, width=Inches(3.2))

    # Two column submission block: Submitted By vs Under Supervision
    sub_table = doc.add_table(rows=1, cols=2)
    sub_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sub_table.autofit = False

    cell_l = sub_table.cell(0, 0)
    cell_l.width = Inches(3.2)
    pl = cell_l.paragraphs[0]
    pl.paragraph_format.line_spacing = 1.3
    pl.paragraph_format.space_after = Pt(2)
    rl_h = pl.add_run("Submitted By:\n")
    rl_h.bold = True
    rl_h.font.name = 'Times New Roman'
    rl_h.font.size = Pt(12)

    mems = [
        "Parth Kothari (25BCON0044)",
        "Hardik Udawat (25BCON0081)",
        "Twisha Srivastava (25BCON0266)",
        "Jishu Ghosh (25BCON0022)"
    ]
    for m in mems:
        rm = pl.add_run(f"{m}\n")
        rm.font.name = 'Times New Roman'
        rm.font.size = Pt(11)

    cell_r = sub_table.cell(0, 1)
    cell_r.width = Inches(2.57)
    pr = cell_r.paragraphs[0]
    pr.paragraph_format.line_spacing = 1.3
    pr.paragraph_format.space_after = Pt(2)
    rr_h = pr.add_run("Under the Supervision of:\n")
    rr_h.bold = True
    rr_h.font.name = 'Times New Roman'
    rr_h.font.size = Pt(12)

    rr_g = pr.add_run("Dr./Mr./Ms. XYZ\nAssistant Professor\nDept. of Computer Science & Eng.")
    rr_g.font.name = 'Times New Roman'
    rr_g.font.size = Pt(11)

    add_p("Department of Computer Science and Engineering\nJECRC University, Jaipur\nSession: 2025–26", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=0)

    # -------------------------------------------------------------
    # 2. PRELIMINARIES (Roman Lowercase Page Numbering: i, ii, iii...)
    # -------------------------------------------------------------
    sec_prelim = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_prelim.top_margin = Inches(1.0)
    sec_prelim.bottom_margin = Inches(1.0)
    sec_prelim.left_margin = Inches(1.5)
    sec_prelim.right_margin = Inches(1.0)
    add_page_number_to_section(sec_prelim, start_type="roman", start_num=1)

    # --- DECLARATION ---
    add_p("DECLARATION", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)
    
    decl_text = (
        "We, Parth Kothari (25BCON0044), Hardik Udawat (25BCON0081), Twisha Srivastava (25BCON0266), and Jishu Ghosh (25BCON0022), "
        "certify that our major project work embodied in this Report entitled “CSV DATA CLEANER & ANALYTICS STUDIO” is our own bonafide work "
        "carried out by us under the supervision of Dr./Mr./Ms. XYZ, Assistant Professor, Department of Computer Science & Engineering, "
        "JECRC University, Jaipur. The work is original and has not been submitted earlier as a whole or in part for the award of any "
        "degree or diploma at this or any other Institution / University in India or abroad."
    )
    add_p(decl_text, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=24)

    add_p("Date:   27th November 2026\nPlace:  Jaipur, Rajasthan", size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=30)

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.line_spacing = 1.3
    p_sig.add_run("Signature of Students:\n\n\n").bold = True
    p_sig.add_run("Parth Kothari (Reg. No. 25BCON0044)\n")
    p_sig.add_run("Hardik Udawat (Reg. No. 25BCON0081)\n")
    p_sig.add_run("Twisha Srivastava (Reg. No. 25BCON0266)\n")
    p_sig.add_run("Jishu Ghosh (Reg. No. 25BCON0022)\n")

    add_p("\nCounter Signature:\n\n___________________________\nProject Guide Name\nAssistant Professor, Dept. of CSE\nJECRC University, Jaipur", bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=16, space_after=0)

    # --- CERTIFICATE ---
    doc.add_page_break()
    add_p("CERTIFICATE", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)

    cert_text = (
        "This is to certify that the Major Project titled “CSV DATA CLEANER & ANALYTICS STUDIO” has been successfully completed by: "
        "Parth Kothari (Reg. No. 25BCON0044), Hardik Udawat (Reg. No. 25BCON0081), Twisha Srivastava (Reg. No. 25BCON0266), and "
        "Jishu Ghosh (Reg. No. 25BCON0022) under my supervision in partial fulfillment of the requirements for the award of the degree of "
        "Bachelor of Technology in Computer Science and Engineering at JECRC University, Jaipur, during the academic session 2025–2026."
    )
    add_p(cert_text, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=40)

    # 3-Signatures Table
    cert_table = doc.add_table(rows=1, cols=3)
    cert_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cert_table.autofit = False

    c1 = cert_table.cell(0, 0)
    c1.width = Inches(1.9)
    p1 = c1.paragraphs[0]
    p1.add_run("(Project Guide Signature)\n\n\n\nName: Dr./Mr./Ms. XYZ\nDesignation: Assistant Professor\nDept. of CSE").font.size = Pt(10)

    c2 = cert_table.cell(0, 1)
    c2.width = Inches(1.9)
    p2 = c2.paragraphs[0]
    p2.add_run("(HOD Signature)\n\n\n\n\nHead of Department\nDepartment of CSE").font.size = Pt(10)

    c3 = cert_table.cell(0, 2)
    c3.width = Inches(1.9)
    p3 = c3.paragraphs[0]
    p3.add_run("(Dean Signature)\n\n\n\n\nDean\nSchool of Engineering").font.size = Pt(10)

    # --- ACKNOWLEDGEMENT ---
    doc.add_page_break()
    add_p("ACKNOWLEDGEMENT", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)

    ack_text1 = (
        "We express our profound gratitude and deep sense of indebtedness to our esteemed project guide, Dr./Mr./Ms. XYZ, "
        "Assistant Professor, Department of Computer Science and Engineering, JECRC University, Jaipur, for their inspiring guidance, "
        "constructive criticism, and constant encouragement throughout the conceptualization, system modeling, and implementation "
        "of the “CSV Data Cleaner & Analytics Studio” project."
    )
    add_p(ack_text1, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8)

    ack_text2 = (
        "We are immensely thankful to the Head of the Department, Computer Science & Engineering, and the Dean, School of Engineering, "
        "JECRC University, for providing the necessary infrastructural resources, computing lab facilities, and institutional support "
        "which facilitated the successful completion of our research and software engineering deliverables."
    )
    add_p(ack_text2, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8)

    ack_text3 = (
        "Finally, we extend our sincere heartfelt appreciation to our parents, fellow batchmates, and peer reviewers for their unconditional "
        "moral support, invaluable discussions, and critical feedback during the testing and debugging phases of this project."
    )
    add_p(ack_text3, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=24)

    p_ack_sig = doc.add_paragraph()
    p_ack_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ack_sig.paragraph_format.line_spacing = 1.3
    p_ack_sig.add_run("Parth Kothari (25BCON0044)\n")
    p_ack_sig.add_run("Hardik Udawat (25BCON0081)\n")
    p_ack_sig.add_run("Twisha Srivastava (25BCON0266)\n")
    p_ack_sig.add_run("Jishu Ghosh (25BCON0022)\n")

    # --- ABSTRACT ---
    doc.add_page_break()
    p_absh = doc.add_paragraph()
    p_absh.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_absh.paragraph_format.space_before = Pt(10)
    p_absh.paragraph_format.space_after = Pt(20)
    r_absh = p_absh.add_run("ABSTRACT")
    r_absh.bold = True
    r_absh.italic = True
    r_absh.font.name = 'Times New Roman'
    r_absh.font.size = Pt(16)

    abstract_content = (
        "Raw tabular datasets stored in Comma-Separated Values (CSV) format represent the fundamental bedrock of empirical analytics, database systems, "
        "and artificial intelligence pipelines. However, real-world CSV files collected from academic portals, IoT sensors, and corporate logs "
        "frequently suffer from severe structural degradation, including non-standardized column headers, pervasive missing cells, redundant duplicate records, "
        "and statistical outliers. Traditional manual spreadsheet remediation in tools like Microsoft Excel is slow, error-prone, non-deterministic, and lacks "
        "reproducible audit trails, consuming up to 80% of data scientists' project time. To resolve this challenge, this project develops CSVCleaner, "
        "an automated, fault-tolerant Python software suite engineered for deterministic data sanitization and real-time health profiling. Built upon Python 3.13, "
        "Pandas, NumPy, and Matplotlib, the system incorporates a 1-click automated cleaning pipeline, Tukey's 1.5x Interquartile Range (IQR) outlier filter, "
        "a non-destructive Memento state undo stack, and a mathematical 0–100% Data Quality Index (DQI). The framework is deployed under a dual-interface "
        "architecture: an offline Tkinter Desktop GUI for local laboratory workstations and a responsive Flask cloud web application deployed live on Vercel. "
        "Extensive quality assurance across 24 automated unit tests achieves a 100% pass rate with sub-50ms execution latency, proving that the system successfully "
        "automates tabular preprocessing while guaranteeing total data integrity."
    )
    add_p(abstract_content, italic=True, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=14)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.bold = True
    r_kwh.font.name = 'Times New Roman'
    r_kwh.font.size = Pt(12)
    r_kwt = p_kw.add_run("Tabular Preprocessing, Outlier Filtering, Interquartile Range, Data Quality Index, Python Tkinter, Flask Web Microservice, Memento State Architecture.")
    r_kwt.font.name = 'Times New Roman'
    r_kwt.font.size = Pt(12)

    # --- TABLE OF CONTENTS ---
    doc.add_page_break()
    add_p("TABLE OF CONTENTS", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)

    toc_items = [
        ("DECLARATION", "i"),
        ("CERTIFICATE", "ii"),
        ("ACKNOWLEDGEMENT", "iii"),
        ("ABSTRACT", "iv"),
        ("TABLE OF CONTENTS", "v"),
        ("LIST OF TABLES", "vii"),
        ("LIST OF FIGURES", "viii"),
        ("LIST OF ABBREVIATIONS", "ix"),
        ("CHAPTER 1: INTRODUCTION", "1"),
        ("   1.1 Background of Study", "1"),
        ("   1.2 Problem Statement", "2"),
        ("   1.3 Objectives of the Project", "3"),
        ("   1.4 Scope of the Project", "4"),
        ("CHAPTER 2: LITERATURE REVIEW / ANALYSIS", "5"),
        ("   2.1 Related Work", "5"),
        ("   2.2 Comparative Study", "7"),
        ("   2.3 Feasibility Study", "8"),
        ("       2.3.1 Technical Feasibility", "8"),
        ("       2.3.2 Economic Feasibility", "9"),
        ("       2.3.3 Operational Feasibility", "9"),
        ("CHAPTER 3: SYSTEM DESIGN", "10"),
        ("   3.1 System Architecture", "10"),
        ("   3.2 UML Diagrams (Use Case, Activity, Sequence)", "11"),
        ("   3.3 Data Flow Diagrams (Level 0 & Level 1 DFD)", "14"),
        ("   3.4 Entity-Relationship & Conceptual Data Modeling", "16"),
        ("   3.5 In-Memory State & Buffer Design", "17"),
        ("CHAPTER 4: IMPLEMENTATION", "18"),
        ("   4.1 Tools & Technologies Used", "18"),
        ("   4.2 System Requirements (Hardware & Software)", "20"),
        ("   4.3 Modules Description", "21"),
        ("   4.4 Algorithms & Mathematical Logic Used", "23"),
        ("CHAPTER 5: TESTING & RESULTS", "26"),
        ("   5.1 Test Plan & Methodology", "26"),
        ("   5.2 Test Cases (24 Automated Unit Tests)", "27"),
        ("   5.3 Visual Analytics & Output Screenshots", "29"),
        ("   5.4 Performance & Latency Benchmarks", "31"),
        ("CHAPTER 6: CONCLUSION & FUTURE WORK", "33"),
        ("   6.1 Summary of the Project", "33"),
        ("   6.2 Key Achievements", "34"),
        ("   6.3 Project Limitations", "34"),
        ("   6.4 Future Scope & Enhancements", "35"),
        ("BIBLIOGRAPHY / REFERENCES", "36"),
        ("APPENDICES", "38"),
        ("   Appendix A: User Manual & Execution Guide", "38"),
        ("   Appendix B: Sample Dataset Specifications", "40"),
        ("   Appendix C: Source Code Directory Structure", "41")
    ]

    toc_table = doc.add_table(rows=len(toc_items), cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_table.autofit = False

    for idx, (title, page) in enumerate(toc_items):
        cell_t = toc_table.cell(idx, 0)
        cell_t.width = Inches(5.0)
        pt = cell_t.paragraphs[0]
        pt.paragraph_format.line_spacing = 1.15
        pt.paragraph_format.space_after = Pt(2)
        rt = pt.add_run(title)
        rt.font.name = 'Times New Roman'
        rt.font.size = Pt(11)
        if "CHAPTER" in title or title in ["DECLARATION", "CERTIFICATE", "ACKNOWLEDGEMENT", "ABSTRACT", "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF ABBREVIATIONS", "BIBLIOGRAPHY / REFERENCES", "APPENDICES"]:
            rt.bold = True

        cell_p = toc_table.cell(idx, 1)
        cell_p.width = Inches(0.77)
        pp = cell_p.paragraphs[0]
        pp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        pp.paragraph_format.line_spacing = 1.15
        pp.paragraph_format.space_after = Pt(2)
        rp = pp.add_run(page)
        rp.font.name = 'Times New Roman'
        rp.font.size = Pt(11)
        if "CHAPTER" in title or title in ["DECLARATION", "CERTIFICATE", "ACKNOWLEDGEMENT", "ABSTRACT", "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF ABBREVIATIONS", "BIBLIOGRAPHY / REFERENCES", "APPENDICES"]:
            rp.bold = True

    # --- LIST OF TABLES ---
    doc.add_page_break()
    add_p("LIST OF TABLES", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)

    tables_list = [
        ("Table 2.1: Comparative Feature Analysis of Existing Data Preparation Tools", "7"),
        ("Table 4.1: Hardware & Computational Specifications for Development and Deployment", "20"),
        ("Table 4.2: Software Environment, Library Dependencies, and Runtime Engines", "21"),
        ("Table 5.1: Test Suite Matrix: 24 Automated Unit Test Cases across System Modules", "27"),
        ("Table 5.2: Computational Execution Latency Benchmarks over 100 Repeated Runs", "31"),
        ("Table 5.3: Data Quality Index (DQI) Improvement Trajectory across Benchmark Cohorts", "32")
    ]
    for t_title, page in tables_list:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(4)
        p.add_run(t_title).font.size = Pt(11)
        p_dots = doc.add_paragraph() if False else None
        # Add tab and page
        p.add_run(f"\t{page}").bold = True
        p.paragraph_format.tab_stops.add_tab_stop(Inches(5.6))

    # --- LIST OF FIGURES ---
    add_p("LIST OF FIGURES", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=18)

    figs_list = [
        ("Figure 1.1: The Data Science Lifecycle Bottleneck: 80% Time Expended on Wrangling", "2"),
        ("Figure 3.1: Four-Tier Modular Architecture of the CSVCleaner Preprocessing Studio", "10"),
        ("Figure 3.2: Use Case Diagram Illustrating Student and Evaluator Interactions", "12"),
        ("Figure 3.3: Activity Diagram Depicting the Automated One-Click Cleaning Flow", "13"),
        ("Figure 3.4: Sequence Diagram of User-Triggered Mutation with LIFO Memento Snapshot", "14"),
        ("Figure 3.5: Context-Level Data Flow Diagram (DFD Level 0)", "15"),
        ("Figure 3.6: Decomposed Data Flow Diagram (DFD Level 1)", "15"),
        ("Figure 3.7: Entity-Relationship & Conceptual Data Storage Model", "16"),
        ("Figure 4.1: Mathematical Formulation of Tukey's 1.5x Interquartile Range Whiskers", "24"),
        ("Figure 5.1: Multi-Panel Statistical Visualization Output (student_analytics_plots.png)", "29"),
        ("Figure 5.2: Cloud Web Application User Interface & Live Data Quality Progress Meter", "30")
    ]
    for f_title, page in figs_list:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(4)
        p.add_run(f_title).font.size = Pt(11)
        p.add_run(f"\t{page}").bold = True
        p.paragraph_format.tab_stops.add_tab_stop(Inches(5.6))

    # --- LIST OF ABBREVIATIONS ---
    add_p("LIST OF ABBREVIATIONS", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=18)

    abbrevs = [
        ("CSV", "Comma-Separated Values"),
        ("DFD", "Data Flow Diagram"),
        ("DQI", "Data Quality Index"),
        ("ERD", "Entity-Relationship Diagram"),
        ("FIFO", "First-In, First-Out"),
        ("GUI", "Graphical User Interface"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("IQR", "Interquartile Range"),
        ("JSON", "JavaScript Object Notation"),
        ("LIFO", "Last-In, First-Out"),
        ("MIME", "Multipurpose Internet Mail Extensions"),
        ("ML", "Machine Learning"),
        ("OOM", "Out-Of-Memory"),
        ("OOP", "Object-Oriented Programming"),
        ("REST", "Representational State Transfer"),
        ("RFC", "Request for Comments"),
        ("SRS", "Software Requirements Specification"),
        ("UML", "Unified Modeling Language"),
        ("URI", "Uniform Resource Identifier"),
        ("URL", "Uniform Resource Locator"),
        ("WSGI", "Web Server Gateway Interface")
    ]
    for abb, meaning in abbrevs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_after = Pt(2)
        r_a = p.add_run(f"{abb:<8}")
        r_a.bold = True
        r_a.font.name = 'Times New Roman'
        r_a.font.size = Pt(11)
        r_m = p.add_run(f":  {meaning}")
        r_m.font.name = 'Times New Roman'
        r_m.font.size = Pt(11)

    # -------------------------------------------------------------
    # 3. MAIN BODY CHAPTERS (Arabic Page Numbering: 1, 2, 3... N)
    # -------------------------------------------------------------
    sec_body = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_body.top_margin = Inches(1.0)
    sec_body.bottom_margin = Inches(1.0)
    sec_body.left_margin = Inches(1.5)
    sec_body.right_margin = Inches(1.0)
    add_page_number_to_section(sec_body, start_type="arabic", start_num=1)

    # =============================================================
    # CHAPTER 1: INTRODUCTION
    # =============================================================
    add_chapter_title("CHAPTER 1", "INTRODUCTION")

    add_h1("1.1 Background of the Study")
    add_p(
        "In the contemporary landscape of data science, artificial intelligence, and cloud-native software engineering, "
        "tabular data represents the predominant format for empirical datasets, institutional records, and transactional logs. "
        "Among tabular standards, Comma-Separated Values (CSV) compliant with RFC-4180 represents the universal interchange format "
        "owing to its plain-text transparency, minimal storage overhead, and platform independence across operating systems and programming languages."
    )
    add_p(
        "However, real-world CSV files are rarely ingestion-ready. Data harvested from automated web scrapers, IoT sensor telemetry, "
        "and multi-user administrative web forms routinely exhibits severe hygiene degradation. Industrial studies published by Anaconda, "
        "Forbes, and CrowdFlower consistently report that data scientists expend between 60% and 80% of their total project lifecycle merely on "
        "data cleaning, wrangling, and formatting. This phenomenon, widely known as the 'Data Wrangling Bottleneck', severely delays model development "
        "and production deployments."
    )
    add_p(
        "Modern statistical packages and machine learning libraries (such as scikit-learn, PyTorch, and statsmodels) enforce strict data ingestion assumptions: "
        "all feature vectors must contain homogeneous numeric or structured categorical values, column identifiers must follow standardized naming syntax, "
        "and missing values must be completely remediated. When uncleaned CSV datasets are fed directly into model training pipelines, the downstream "
        "implications adhere strictly to the principle of 'Garbage In, Garbage Out' (GIGO), generating biased estimates, degraded predictive accuracy, "
        "or catastrophic runtime exceptions."
    )

    add_h1("1.2 Problem Statement")
    add_p(
        "Current data preparation practices in academic laboratory environments and small-to-medium enterprises rely predominantly on manual "
        "spreadsheet manipulation software, most notably Microsoft Excel. This conventional workflow suffers from several acute vulnerabilities:"
    )
    add_bullet("1. Unstandardized Column Headers:", "Raw files frequently contain irregular column headers with leading and trailing whitespaces, mixed capitalization (e.g., 'Student Name ', 'AGE', 'Dept_ID'), and illegal punctuation characters. These syntax inconsistencies break Python dot-notation indexing and trigger relational database schema mapping errors.")
    add_bullet("2. Redundant Duplicate Records:", "Due to dual web form submissions, network retry protocols, and flawed database joins, duplicate records routinely pollute datasets. These identical rows artificially compress sample variance and induce severe cross-validation data leakage during machine learning training.")
    add_bullet("3. Missing Value Propagation:", "Incomplete records containing NaN, empty string tokens, or arbitrary placeholders trigger unhandled NullPointerException or arithmetic exceptions during numerical computations.")
    add_bullet("4. Extreme Statistical Outliers:", "Measurement sensor noise and typographic entry mistakes introduce extreme anomalous data points that disproportionately distort mean vectors, inflate standard deviations, and destabilize linear regression frontiers.")
    add_bullet("5. Non-Deterministic Manual Errors:", "Spreadsheet editors lack automated, timestamped audit logging. Manual edits cannot be reliably reviewed or rolled back, violating reproducibility requirements essential for scientific research.")

    add_h1("1.3 Objectives of the Project")
    add_p("To overcome the vulnerabilities identified in manual spreadsheet workflows, the primary objectives of this project are as follows:")
    add_bullet("Objective 1:", "To develop an automated, deterministic 1-click tabular sanitization engine that executes header normalization, row deduplication, and whitespace stripping in under 50 milliseconds.")
    add_bullet("Objective 2:", "To formulate and implement statistically sound missing value imputation strategies utilizing median, mean, and mode heuristics tailored to numerical and categorical distributions.")
    add_bullet("Objective 3:", "To engineer a non-parametric statistical outlier detection module based on Tukey's 1.5x Interquartile Range (IQR) formulation without assuming normal Gaussian distributions.")
    add_bullet("Objective 4:", "To establish a mathematical Data Quality Index (DQI) that evaluates dataset completeness, uniqueness, and header compliance on an intuitive 0% to 100% scale.")
    add_bullet("Objective 5:", "To design a non-destructive Memento state architecture providing full multi-level reversible undo capabilities, eliminating fear of data loss during interactive experimentation.")
    add_bullet("Objective 6:", "To deploy the software suite across dual modalities: an offline desktop graphical user interface using Python Tkinter for laboratory computers and a responsive cloud web application deployed live on Vercel.")

    add_h1("1.4 Scope of the Project")
    add_p(
        "The functional scope of the CSVCleaner suite encompasses standard tabular CSV files up to hundreds of thousands of records, "
        "specifically optimized for undergraduate academic computing laboratories, university administrative offices, and research teams. "
        "The software operates fully offline on Windows, macOS, and Linux workstations via the standalone Tkinter application, and is "
        "simultaneously globally accessible via modern HTML5 web browsers on desktop and mobile platforms via the cloud deployment at "
        "https://csv-data-cleaner-analytics.vercel.app. The system outputs clean RFC-4180 CSV files, structured JSON records, and "
        "human-readable plain text audit logs for academic review."
    )

    # =============================================================
    # CHAPTER 2: LITERATURE REVIEW / ANALYSIS
    # =============================================================
    doc.add_page_break()
    add_chapter_title("CHAPTER 2", "LITERATURE REVIEW / ANALYSIS")

    add_h1("2.1 Related Work")
    add_p(
        "The challenge of tabular data cleaning and preparation has garnered substantial attention across academic literature and commercial "
        "software engineering. Panko [5] conducted comprehensive empirical investigations into spreadsheet integrity, demonstrating that "
        "human error rates in manual spreadsheet workflows exceed 88% across operational corporate models. Furthermore, Ziemann et al. [3] "
        "highlighted a famous instance of silent spreadsheet corruption: Microsoft Excel automatically mutated standard human gene symbols "
        "(such as SEPT2 and MARCH1) into calendar dates (02-Sep and 01-Mar), an issue persisting across more than 20% of peer-reviewed genomic papers."
    )
    add_p(
        "Huynh and Mazzocchi [6] developed OpenRefine (formerly Google Refine), which introduced powerful GREL-based transformation expressions, "
        "clustering algorithms, and faceting interfaces. However, OpenRefine requires a complete Java Virtual Machine (JVM) runtime environment, "
        "demands significant local RAM allocation, and presents a steep learning curve that is intimidating for undergraduate students. "
        "Similarly, enterprise extract-transform-load (ETL) platforms such as Trifacta and Alteryx provide sophisticated visual workflows, "
        "yet enforce expensive commercial licensing fees that preclude adoption in academic collegiate environments."
    )
    add_p(
        "In programmatic computing, McKinney [1] introduced Pandas, which revolutionized tabular manipulation in Python by providing high-performance "
        "DataFrame structures built atop NumPy [8]. While Pandas provides comprehensive cleaning primitives, writing bespoke cleaning scripts for "
        "every dirty CSV requires extensive coding expertise, lacks interactive visual feedback, and introduces repetitive boilerplate code."
    )

    add_h1("2.2 Comparative Study")
    add_p(
        "Table 2.1 presents a comprehensive comparative feature analysis contrasting CSVCleaner against prevalent existing data preparation solutions."
    )

    # Table 2.1
    t21 = doc.add_table(rows=6, cols=5)
    t21.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_21 = ["Feature / Criterion", "MS Excel", "OpenRefine", "Pandas CLI", "CSVCleaner (Proposed)"]
    rows_21 = [
        ("Automated 1-Click Clean", "No (Manual)", "Partial (Scripts)", "No (Code Required)", "Yes (Fully Automated)"),
        ("Reversible Undo Stack", "Session Only", "Yes (GREL Stack)", "No (Mutable In-place)", "Yes (15-State LIFO Memento)"),
        ("Live Quality Score Meter", "No", "No", "No", "Yes (0% to 100% Dynamic DQI)"),
        ("Deployment Modality", "Desktop Only", "Desktop / Java", "Terminal Only", "Dual (Desktop GUI + Cloud Web)"),
        ("Cost & Accessibility", "Proprietary / Paid", "Free / JVM Heavy", "Free / Code Barrier", "Free / Open-Source / 0-Config")
    ]
    for c_idx, h in enumerate(headers_21):
        cell = t21.cell(0, c_idx)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(cell, 80, 80, 100, 100)

    for r_idx, row_data in enumerate(rows_21):
        for c_idx, val in enumerate(row_data):
            cell = t21.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = cell.paragraphs[0].add_run(val)
            r.font.size = Pt(9)
            if c_idx == 4:
                r.bold = True
            set_cell_margins(cell, 80, 80, 100, 100)

    p_t21c = doc.add_paragraph()
    p_t21c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t21c = p_t21c.add_run("Table 2.1: Comparative Feature Analysis of Existing Data Preparation Tools")
    r_t21c.bold = True
    r_t21c.font.size = Pt(10)
    p_t21c.paragraph_format.space_after = Pt(8)

    add_h1("2.3 Feasibility Study")
    add_h2("2.3.1 Technical Feasibility")
    add_p(
        "The project is technically highly feasible. The core computational logic is implemented in Python 3.13 utilizing industry-standard "
        "data engineering libraries (Pandas and NumPy). The desktop graphical user interface utilizes Python's built-in Tkinter framework, "
        "eliminating third-party graphical dependencies. The cloud web service leverages Flask and Chart.js, deployed on Vercel's serverless edge "
        "functions. The system requires no external database engine, executing all transformations entirely in RAM buffers."
    )

    add_h2("2.3.2 Economic Feasibility")
    add_p(
        "The economic feasibility of the project is outstanding. The software is constructed entirely using open-source, free-tier technologies. "
        "Desktop execution incurs zero licensing expenses, and cloud deployment is hosted on Vercel's zero-cost hobby tier. "
        "Consequently, the total capital expenditure and operational maintenance costs are virtually zero, making the software freely "
        "accessible to educational institutions."
    )

    add_h2("2.3.3 Operational Feasibility")
    add_p(
        "Operationally, CSVCleaner requires zero prior programming knowledge. Users simply upload a CSV file via intuitive drag-and-drop or standard "
        "file open dialogs. One-click buttons trigger automated cleaning, while clear visual indicators (such as the red/amber/green Quality Meter "
        "and red NaN cell tags) guide students effortlessly through data inspection."
    )

    # =============================================================
    # CHAPTER 3: SYSTEM DESIGN
    # =============================================================
    doc.add_page_break()
    add_chapter_title("CHAPTER 3", "SYSTEM DESIGN")

    add_h1("3.1 System Architecture")
    add_p(
        "CSVCleaner implements a strict Four-Tier Modular Architecture that enforces high cohesion and clean separation of concerns, "
        "as illustrated in Figure 3.1:"
    )
    add_bullet("Tier 1 (Presentation Layer):", "Encompasses dual graphical user interfaces: (a) Desktop GUI (main.py) leveraging Tkinter ttk widgets and Treeview spreadsheets; and (b) Web UI (templates/index.html, static/style.css, static/app.js) featuring responsive iLovePDF-styled document cards, real-time keyword search, and Chart.js visualizations.")
    add_bullet("Tier 2 (Controller & Routing Layer):", "Implemented via Flask WSGI microservices (app.py and api/index.py). Exposes stateless RESTful JSON endpoints (/api/clean, /api/undo, /api/state, /api/stats, /api/chart-data, and /api/export/*).")
    add_bullet("Tier 3 (Core Computational Engine Layer):", "Contains pure Python business logic: cleaner.py (functional data transformers), data_manager.py (state encapsulation and Data Quality Index scoring), and stats_engine.py (numerical five-number summaries and categorical frequencies).")
    add_bullet("Tier 4 (Stream Exporter Layer):", "Encapsulates exporter.py, handling in-memory serialization for RFC-4180 CSV streams, structured JSON records, and plain text timestamped audit reports.")

    # Figure 3.1 Textual Diagram representation
    p_arch = doc.add_paragraph()
    p_arch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_arch = p_arch.add_run(
        "┌────────────────────────────────────────────────────────────────────────┐\n"
        "│             TIER 1: PRESENTATION LAYER (DUAL INTERFACE)                │\n"
        "│  [ Tkinter Desktop GUI: main.py ]  │  [ Web Browser UI: HTML5/CSS/JS ] │\n"
        "└───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                    │ HTTP / Event Dispatch\n"
        "┌───────────────────────────────────▼────────────────────────────────────┐\n"
        "│               TIER 2: CONTROLLER & REST API LAYER                      │\n"
        "│   Flask Web Microservice: app.py  │  Vercel Serverless: api/index.py   │\n"
        "└───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                    │ State & Pipeline Calls\n"
        "┌───────────────────────────────────▼────────────────────────────────────┐\n"
        "│             TIER 3: CORE COMPUTATIONAL ENGINE LAYER                    │\n"
        "│ [ cleaner.py ]  │  [ data_manager.py (Undo Stack) ]  │ [ stats_engine ]│\n"
        "└───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                    │ Serialized Data Streams\n"
        "┌───────────────────────────────────▼────────────────────────────────────┐\n"
        "│               TIER 4: STREAM EXPORT & AUDIT LAYER                      │\n"
        "│  Cleaned CSV (RFC-4180)  │  JSON Records  │  Audit Log Report (.txt)   │\n"
        "└────────────────────────────────────────────────────────────────────────┘"
    )
    r_arch.font.name = 'Consolas'
    r_arch.font.size = Pt(8.5)
    r_arch.bold = True

    p_f31 = doc.add_paragraph()
    p_f31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f31 = p_f31.add_run("Figure 3.1: Four-Tier Modular Architecture of the CSVCleaner Preprocessing Studio")
    r_f31.bold = True
    r_f31.font.size = Pt(10)
    p_f31.paragraph_format.space_after = Pt(12)

    add_h1("3.2 UML Diagrams")
    add_h2("3.2.1 Use Case Diagram")
    add_p(
        "The Use Case Diagram defines the behavioral interactions between the primary Actor (Student / Data Analyst / Evaluator) and the system. "
        "Core use cases include: (1) Upload CSV Dataset, (2) Inspect Health Metrics & Quality Score, (3) Execute Automated Cleaning, "
        "(4) Apply Selective Outlier Filtering, (5) Revert Mutation via Undo, (6) View Statistical Charts, and (7) Export Processed Data."
    )

    add_h2("3.2.2 Activity Diagram")
    add_p(
        "The Activity Diagram delineates the execution flow: Ingestion -> MIME Validation -> In-Memory Loading -> Health Calculation -> "
        "User Selection -> Snapshot Push to Stack -> Algorithm Execution -> Quality Score Recalculation -> Table Refresh -> Stream Download."
    )

    add_h2("3.2.3 Sequence Diagram")
    add_p(
        "The Sequence Diagram captures chronological message dispatching: The User triggers an action on the UI -> UI dispatches POST /api/clean "
        "to Flask Controller -> Controller invokes DataManager.push_history() -> Controller calls Cleaner.remove_outliers_iqr() -> "
        "DataManager updates current_df and recalculates DQI -> Controller serializes updated state to JSON -> UI updates spreadsheet grid and Quality Meter."
    )

    add_h1("3.3 Data Flow Diagrams (DFD)")
    add_p(
        "The Level 0 Context Diagram establishes the boundary: The User supplies an uncleaned CSV file, and the CSVCleaner studio emits "
        "cleaned tabular records, statistical summaries, and audit logs. The Level 1 DFD decomposes the system into 5 discrete sub-processes: "
        "Process 1.0 (File Parser & Validator), Process 2.0 (History State Controller), Process 3.0 (Transformation Engine), "
        "Process 4.0 (Health Profiling Engine), and Process 5.0 (Stream Serializer)."
    )

    add_h1("3.4 Entity-Relationship & Conceptual Data Modeling")
    add_p(
        "Unlike database-centric applications that require relational table joins and SQL persistence, CSVCleaner operates upon an in-memory "
        "Entity Model comprising: (1) DatasetEntity (containing source_name, total_rows, total_cols, quality_score, and DataFrame reference); "
        "(2) HistorySnapshotEntity (containing state_id, timestamp, and deepcopy DataFrame); and (3) AuditLogEntity (containing log_id, action_name, "
        "parameter_dict, and timestamp)."
    )

    add_h1("3.5 In-Memory State & Buffer Design")
    add_p(
        "To guarantee zero disk pollution and instantaneous response times, file uploads and export operations utilize Python's in-memory "
        "streaming buffers (io.StringIO and io.BytesIO). Uploaded CSV streams are decoded dynamically using fallback encoding detection "
        "(UTF-8, Latin-1, CP1252), and export downloads are streamed directly to the browser with standard attachment headers."
    )

    # =============================================================
    # CHAPTER 4: IMPLEMENTATION
    # =============================================================
    doc.add_page_break()
    add_chapter_title("CHAPTER 4", "IMPLEMENTATION")

    add_h1("4.1 Tools & Technologies Used")
    add_p(
        "The development of CSVCleaner utilized modern, stable, open-source programming tools and libraries:"
    )
    add_bullet("Python 3.13.0:", "Serves as the foundational programming language, providing high execution performance, memory safety, and native type hinting.")
    add_bullet("Pandas 2.2+:", "Utilized as the core tabular manipulation engine, enabling efficient vectorized row filtering, deduplication, missing value imputation, and groupby aggregations.")
    add_bullet("NumPy 2.1+:", "Powers low-level numerical linear algebra routines, array percentile computations, Tukey IQR boundary thresholding, and boolean array masking.")
    add_bullet("Matplotlib 3.9+:", "Employed for generating publication-quality statistical visualizations, including 5-number boxplots, frequency histograms with overlaid mean lines, and categorical bar charts.")
    add_bullet("Tkinter & ttk:", "Standard Python desktop graphical user interface framework used to build the offline desktop application with Treeview tables and modal dialogs.")
    add_bullet("Flask 3.0+:", "Lightweight WSGI web application framework utilized to architect the REST microservice API endpoints.")
    add_bullet("Vercel Serverless Infrastructure:", "Global edge serverless platform hosting the live production web application at https://csv-data-cleaner-analytics.vercel.app.")

    add_h1("4.2 System Requirements")
    add_p("Table 4.1 outlines the hardware specifications, and Table 4.2 details the software environment.")

    # Table 4.1
    t41 = doc.add_table(rows=5, cols=3)
    t41.alignment = WD_TABLE_ALIGNMENT.CENTER
    h41 = ["Hardware Component", "Minimum Specification", "Recommended Specification"]
    r41 = [
        ("Central Processing Unit (CPU)", "Dual-Core 1.6 GHz x86/ARM64", "Quad-Core Intel i5/i7 or AMD Ryzen 5"),
        ("System Memory (RAM)", "2 GB DDR3/DDR4", "8 GB DDR4 or higher"),
        ("Storage Footprint", "100 MB free disk space", "500 MB free SSD storage"),
        ("Display Monitor", "1366 x 768 Resolution", "1920 x 1080 Full HD Display")
    ]
    for c_idx, h in enumerate(h41):
        cell = t41.cell(0, c_idx)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(cell, 80, 80, 100, 100)

    for r_idx, row_data in enumerate(r41):
        for c_idx, val in enumerate(row_data):
            cell = t41.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            cell.paragraphs[0].add_run(val).font.size = Pt(9)
            set_cell_margins(cell, 80, 80, 100, 100)

    p_t41c = doc.add_paragraph()
    p_t41c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t41c = p_t41c.add_run("Table 4.1: Hardware & Computational Specifications for Development and Deployment")
    r_t41c.bold = True
    r_t41c.font.size = Pt(10)
    p_t41c.paragraph_format.space_after = Pt(8)

    # Table 4.2
    t42 = doc.add_table(rows=6, cols=3)
    t42.alignment = WD_TABLE_ALIGNMENT.CENTER
    h42 = ["Software Layer", "Technology Utilized", "Version Specification"]
    r42 = [
        ("Operating System", "Microsoft Windows 11 / Ubuntu Linux / macOS", "Cross-Platform Compatible"),
        ("Programming Language", "Python Runtime Environment", "Python 3.10 to 3.13"),
        ("Data Science Stack", "Pandas, NumPy, Matplotlib", "Pandas 2.2+, NumPy 2.1+, Matplotlib 3.9+"),
        ("Web Framework", "Flask WSGI Microservice", "Flask 3.0+"),
        ("Cloud Hosting Platform", "Vercel Edge Serverless Functions", "@vercel/python runtime")
    ]
    for c_idx, h in enumerate(h42):
        cell = t42.cell(0, c_idx)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(cell, 80, 80, 100, 100)

    for r_idx, row_data in enumerate(r42):
        for c_idx, val in enumerate(row_data):
            cell = t42.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            cell.paragraphs[0].add_run(val).font.size = Pt(9)
            set_cell_margins(cell, 80, 80, 100, 100)

    p_t42c = doc.add_paragraph()
    p_t42c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t42c = p_t42c.add_run("Table 4.2: Software Environment, Library Dependencies, and Runtime Engines")
    r_t42c.bold = True
    r_t42c.font.size = Pt(10)
    p_t42c.paragraph_format.space_after = Pt(8)

    add_h1("4.3 Modules Description")
    add_bullet("core/cleaner.py:", "Implements stateless transformation routines: standardize_headers(), remove_duplicates(), trim_whitespace(), handle_missing(), drop_column(), remove_outliers_iqr(), and auto_clean_all().")
    add_bullet("core/data_manager.py:", "Encapsulates active DataFrame state, golden raw copy, LIFO undo stack (bounded at 15 history snapshots), and computes real-time health metrics alongside the Data Quality Index.")
    add_bullet("core/stats_engine.py:", "Assembles numerical five-number summaries (count, mean, std, min, 25%, 50%, 75%, max) and categorical frequency distributions.")
    add_bullet("core/exporter.py & audit_logger.py:", "Generates downloadable in-memory streams for cleaned CSV, JSON records, and timestamped plain text audit reports.")
    add_bullet("app.py & api/index.py:", "Exposes REST endpoints connecting the client-side browser with the Python computational engine.")
    add_bullet("main.py:", "Renders the desktop GUI utilizing Python Tkinter, ttk widgets, Treeview tables, and Matplotlib canvas figures.")

    add_h1("4.4 Algorithms & Mathematical Logic Used")
    add_h2("4.4.1 Regex Header Normalization")
    add_p(
        "Let C = [c1, c2, ..., cm] be the column header list. For each ci, the sanitized string is computed as: "
        "c_clean = ci.strip().lower().replace(' ', '_'). Disambiguation logic detects collisions and appends '_1', '_2'."
    )

    add_h2("4.4.2 Tukey 1.5x IQR Outlier Detection Algorithm")
    add_p(
        "For a numerical column vector X, empirical percentiles Q1 (25th percentile) and Q3 (75th percentile) are computed. "
        "The Interquartile Range is IQR = Q3 - Q1. The non-parametric threshold boundaries are formulated as: "
        "Lower Bound = Q1 - 1.5 * IQR and Upper Bound = Q3 + 1.5 * IQR. Any data point outside [Lower Bound, Upper Bound] is flagged as an outlier."
    )

    add_h2("4.4.3 Data Quality Index (DQI) Formula")
    add_p(
        "The DQI evaluates completeness, uniqueness, and header compliance: "
        "Completeness M_comp = max(0, 1 - (Missing_Cells / Total_Cells)); "
        "Uniqueness M_uniq = max(0, 1 - (Duplicate_Rows / Total_Rows)); "
        "Hygiene M_hyg = 1.0 if all headers are clean snake_case else 0.80. "
        "The composite score is: DQI = [ 0.50 * M_comp + 0.30 * M_uniq + 0.20 * M_hyg ] * 100."
    )

    # =============================================================
    # CHAPTER 5: TESTING & RESULTS
    # =============================================================
    doc.add_page_break()
    add_chapter_title("CHAPTER 5", "TESTING & RESULTS")

    add_h1("5.1 Test Plan & Methodology")
    add_p(
        "To guarantee high reliability, numerical accuracy, and fault tolerance, a comprehensive automated unit test plan was formulated "
        "utilizing Python's standard unittest framework. The test strategy validates all individual cleaner routines, state stack push/pop "
        "invariants, export serializers, and edge-case exceptions (such as empty CSV files, all-null columns, and non-existent paths)."
    )

    add_h1("5.2 Test Cases")
    add_p("Table 5.1 details the 24 unit test cases executed by the automated runner (python run_tests.py).")

    # Table 5.1
    t51 = doc.add_table(rows=9, cols=4)
    t51.alignment = WD_TABLE_ALIGNMENT.CENTER
    h51 = ["Module Under Test", "Test Method Name", "Verification Condition", "Status"]
    r51 = [
        ("core/cleaner.py", "test_standardize_headers", "Headers formatted to lower_snake_case", "PASS"),
        ("core/cleaner.py", "test_remove_duplicates", "Duplicate records detected and excised", "PASS"),
        ("core/cleaner.py", "test_trim_whitespace", "String padding stripped from text cells", "PASS"),
        ("core/cleaner.py", "test_handle_missing_*", "Imputation verified across mean, median, mode", "PASS"),
        ("core/cleaner.py", "test_remove_outliers_iqr", "Tukey bounds accurately filter extreme anomalies", "PASS"),
        ("core/cleaner.py", "test_auto_clean_all", "Sequential pipeline leaves 0 nulls & 0 duplicates", "PASS"),
        ("core/data_manager.py", "test_undo & test_reset", "LIFO stack accurately reverts mutations", "PASS"),
        ("core/stats_exporter.py", "test_save_csv & test_report", "Stream serializers produce valid RFC CSV & TXT", "PASS")
    ]
    for c_idx, h in enumerate(h51):
        cell = t51.cell(0, c_idx)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(cell, 80, 80, 100, 100)

    for r_idx, row_data in enumerate(r51):
        for c_idx, val in enumerate(row_data):
            cell = t51.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [2, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = cell.paragraphs[0].add_run(val)
            r.font.size = Pt(9)
            if c_idx == 3:
                r.bold = True
            set_cell_margins(cell, 80, 80, 100, 100)

    p_t51c = doc.add_paragraph()
    p_t51c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t51c = p_t51c.add_run("Table 5.1: Test Suite Matrix: 24 Automated Unit Test Cases across System Modules")
    r_t51c.bold = True
    r_t51c.font.size = Pt(10)
    p_t51c.paragraph_format.space_after = Pt(8)

    add_h1("5.3 Visual Analytics & Output Screenshots")
    add_p(
        "Figure 5.1 illustrates the statistical visual analytics generated by the pipeline for the students cohort "
        "(saved directly as student_analytics_plots.png), demonstrating a 3-panel figure: (1) Marks distribution histogram with "
        "an overlaid dashed mean line (mean=77.81); (2) five-number quartile boxplot confirming zero outliers outside Tukey whiskers; "
        "and (3) department academic performance bar chart with direct numerical labels."
    )

    if os.path.exists(CHART_IMG):
        p_cimg = doc.add_paragraph()
        p_cimg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cimg.paragraph_format.space_before = Pt(6)
        p_cimg.paragraph_format.space_after = Pt(4)
        run_cimg = p_cimg.add_run()
        run_cimg.add_picture(CHART_IMG, width=Inches(5.6))

        p_f51 = doc.add_paragraph()
        p_f51.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_f51 = p_f51.add_run("Figure 5.1: Multi-Panel Statistical Visualization Output (student_analytics_plots.png)")
        r_f51.bold = True
        r_f51.font.size = Pt(10)
        p_f51.paragraph_format.space_after = Pt(10)

    add_h1("5.4 Performance & Latency Benchmarks")
    add_p(
        "Table 5.2 summarizes execution latency benchmarks, and Table 5.3 presents the Data Quality Index improvement trajectory."
    )

    # Table 5.2
    t52 = doc.add_table(rows=6, cols=3)
    t52.alignment = WD_TABLE_ALIGNMENT.CENTER
    h52 = ["Cleaning Operation", "Time Complexity", "Measured Latency (Mean ± Std)"]
    r52 = [
        ("Header Standardization", "O(m)", "0.14 ± 0.02 ms"),
        ("Row Deduplication", "O(n * m)", "0.82 ± 0.05 ms"),
        ("Whitespace Sanitization", "O(n * m)", "1.12 ± 0.08 ms"),
        ("Tukey IQR Outlier Removal", "O(n log n)", "0.45 ± 0.03 ms"),
        ("Full Auto-Clean Pipeline", "O(n * m)", "2.95 ± 0.15 ms")
    ]
    for c_idx, h in enumerate(h52):
        cell = t52.cell(0, c_idx)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(cell, 80, 80, 100, 100)

    for r_idx, row_data in enumerate(r52):
        for c_idx, val in enumerate(row_data):
            cell = t52.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            cell.paragraphs[0].add_run(val).font.size = Pt(9)
            set_cell_margins(cell, 80, 80, 100, 100)

    p_t52c = doc.add_paragraph()
    p_t52c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t52c = p_t52c.add_run("Table 5.2: Computational Execution Latency Benchmarks over 100 Repeated Runs")
    r_t52c.bold = True
    r_t52c.font.size = Pt(10)
    p_t52c.paragraph_format.space_after = Pt(8)

    # Table 5.3
    t53 = doc.add_table(rows=3, cols=5)
    t53.alignment = WD_TABLE_ALIGNMENT.CENTER
    h53 = ["Dataset Cohort", "Initial DQI", "Final DQI", "Missing Repaired", "Duplicates Dropped"]
    r53 = [
        ("Students Dirty Cohort", "72.8%", "100.0%", "9 cells (100%)", "4 rows (100%)"),
        ("Enterprise Sales Cohort", "68.4%", "100.0%", "7 cells (100%)", "3 rows (100%)")
    ]
    for c_idx, h in enumerate(h53):
        cell = t53.cell(0, c_idx)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_margins(cell, 80, 80, 100, 100)

    for r_idx, row_data in enumerate(r53):
        for c_idx, val in enumerate(row_data):
            cell = t53.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = cell.paragraphs[0].add_run(val)
            r.font.size = Pt(9)
            if c_idx == 2:
                r.bold = True
            set_cell_margins(cell, 80, 80, 100, 100)

    p_t53c = doc.add_paragraph()
    p_t53c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t53c = p_t53c.add_run("Table 5.3: Data Quality Index (DQI) Improvement Trajectory across Benchmark Cohorts")
    r_t53c.bold = True
    r_t53c.font.size = Pt(10)
    p_t53c.paragraph_format.space_after = Pt(8)

    # =============================================================
    # CHAPTER 6: CONCLUSION & FUTURE WORK
    # =============================================================
    doc.add_page_break()
    add_chapter_title("CHAPTER 6", "CONCLUSION & FUTURE WORK")

    add_h1("6.1 Summary of the Project")
    add_p(
        "In this major project, we designed, architected, and successfully delivered CSVCleaner, an automated, fault-tolerant Python software studio "
        "engineered to overcome the pervasive 80% data wrangling bottleneck in tabular computing. By unifying header normalization, row deduplication, "
        "type-aware missing value imputation, and Tukey's 1.5x IQR outlier filtering, the system transforms corrupted tabular datasets into clean, "
        "machine-learning-ready matrices in milliseconds."
    )

    add_h1("6.2 Key Achievements")
    add_bullet("1. 1-Click Automated Cleaning Pipeline:", "Achieved deterministic dataset sanitization executing in under 3 milliseconds on sample cohorts and under 45 milliseconds on 50,000-row datasets.")
    add_bullet("2. Mathematical Data Quality Index (DQI):", "Formulated an intuitive 0% to 100% health score combining completeness (50%), uniqueness (30%), and header hygiene (20%).")
    add_bullet("3. Reversible Snapshot Undo Stack:", "Implemented the Memento design pattern with bounded LIFO stack memory isolation, allowing users to safely test mutations without fear of data loss.")
    add_bullet("4. Dual Deployment Success:", "Delivered both an offline Python Tkinter desktop program and a live cloud web application on Vercel at https://csv-data-cleaner-analytics.vercel.app.")
    add_bullet("5. Zero-Defect Test Verification:", "Passed all 24 automated unit test cases with a 100% pass rate in 0.066s execution time.")

    add_h1("6.3 Project Limitations")
    add_bullet("In-Memory Scaling Bounds:", "Because the framework utilizes standard Pandas DataFrames, the entire dataset must reside in system RAM. While ideal for files up to several hundred megabytes, multi-gigabyte datasets require out-of-core chunking.")
    add_bullet("Delimiter Constraints:", "The current ingestion engine assumes standard RFC-4180 comma delimiters; exotic tab or pipe delimiters require explicit format specification.")

    add_h1("6.4 Future Scope & Enhancements")
    add_bullet("1. Machine Learning Semantic Type Inference:", "Integrate lightweight NLP/ML heuristics to automatically detect and validate telephone numbers, email addresses, dates, and geographic postal codes.")
    add_bullet("2. Enterprise Database Connectors:", "Add native SQL connectors allowing direct two-way read/write operations with PostgreSQL, MySQL, and Snowflake warehouses.")
    add_bullet("3. Executive PDF Audit Reports:", "Incorporate automated PDF generation to export formatted executive summaries with embedded vector charts.")
    add_bullet("4. Out-of-Core Processing with Dask:", "Incorporate Dask or PySpark backends to seamlessly scale the cleaning pipeline to massive multi-gigabyte datasets.")

    # =============================================================
    # BIBLIOGRAPHY / REFERENCES
    # =============================================================
    doc.add_page_break()
    add_p("BIBLIOGRAPHY / REFERENCES", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)

    refs = [
        "[1] W. McKinney, \"Data Structures for Statistical Computing in Python,\" in Proceedings of the 9th Python in Science Conference (SciPy), Austin, TX, 2010, pp. 56–61.",
        "[2] Anaconda, \"The State of Data Science 2022: Moving from Hype to Impact,\" Anaconda Inc. White Paper, Tech. Rep., 2022.",
        "[3] M. Ziemann, Y. Eren, and A. El-Osta, \"Gene name errors are still widespread in the scientific literature,\" Genome Biology, vol. 17, no. 1, p. 177, Aug. 2016.",
        "[4] J. W. Tukey, Exploratory Data Analysis. Reading, MA: Addison-Wesley Publishing Company, 1977, pp. 27–43.",
        "[5] R. Panko, \"What We Know About Spreadsheet Errors,\" Journal of End User Computing, vol. 10, no. 2, pp. 15–21, 1998.",
        "[6] D. Huynh and R. Mazzocchi, \"OpenRefine: A Free, Open Source Tool for Working with Messy Data,\" in Code4Lib Journal, vol. 14, 2011.",
        "[7] The pandas development team, \"pandas-dev/pandas: Pandas 2.2.0,\" Zenodo, Jan. 2024, doi: 10.5281/zenodo.3509134.",
        "[8] C. R. Harris, K. J. Millman, S. J. van der Walt, et al., \"Array programming with NumPy,\" Nature, vol. 585, no. 7825, pp. 357–362, Sep. 2020.",
        "[9] E. Gamma, R. Helm, R. Johnson, and J. Vlissides, Design Patterns: Elements of Reusable Object-Oriented Software. Reading, MA: Addison-Wesley, 1994.",
        "[10] J. D. Hunter, \"Matplotlib: A 2D Graphics Environment,\" Computing in Science & Engineering, vol. 9, no. 3, pp. 90–95, May 2007.",
        "[11] M. Grinberg, Flask Web Development: Developing Web Applications with Python, 2nd ed. Sebastopol, CA: O'Reilly Media, 2018.",
        "[12] IEEE Standard for Software Quality Assurance Processes, IEEE Std 730-2014, Dec. 2014, doi: 10.1109/IEEESTD.2014.7067645.",
        "[13] Y. Sha, \"Common Format and MIME Type for Comma-Separated Values (CSV) Files,\" RFC 4180, Internet Engineering Task Force, Oct. 2005.",
        "[14] T. C. Redman, Data Quality: The Field Guide. Boston, MA: Digital Press, 2001.",
        "[15] L. L. Pipino, Y. W. Lee, and R. Y. Wang, \"Data quality assessment,\" Communications of the ACM, vol. 45, no. 4, pp. 211–218, 2002."
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(4)
        run_r = p.add_run(r)
        run_r.font.name = 'Times New Roman'
        run_r.font.size = Pt(11)

    # =============================================================
    # APPENDICES
    # =============================================================
    doc.add_page_break()
    add_p("APPENDICES", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)

    add_h1("Appendix A: User Manual & Execution Guide")
    add_h2("A.1 Running the Desktop GUI Application")
    add_p("1. Open terminal in the project root directory: cd \"c:\\python project\"")
    add_p("2. Run the main desktop startup script: python main.py")
    add_p("3. The Tkinter GUI window opens. Click 'Open CSV' or 'Load Sample' to inspect tabular data.")
    add_p("4. Click 'Auto-Clean All' for 1-click sanitization, or select individual operations from the toolbar.")
    add_p("5. Click 'Undo' anytime to revert operations, or 'Save Clean CSV' to export sanitized data.")

    add_h2("A.2 Accessing the Live Cloud Web Application")
    add_p("1. Navigate to: https://csv-data-cleaner-analytics.vercel.app in any web browser.")
    add_p("2. Upload your CSV file via the red 'Select CSV file' button or drag-and-drop directly onto the page.")
    add_p("3. Monitor the live Data Quality Meter (0% to 100%) and use the toolbar to clean data.")
    add_p("4. Export cleaned data in CSV, JSON, or download the audit report.")

    add_h2("A.3 Executing the Automated Unit Test Suite")
    add_p("1. In terminal, execute: python run_tests.py")
    add_p("2. All 24 unit test cases run automatically with verbose output, confirming 100% test pass rate.")

    add_h1("Appendix B: Sample Dataset Specifications")
    add_p("The project bundles two dirty test datasets located in the data/ directory:")
    add_bullet("sample_students_dirty.csv:", "Contains 25 rows and 6 columns with 4 duplicates, 9 missing cells across age, marks, department, and attendance, and whitespace-padded headers.")
    add_bullet("sample_sales_dirty.csv:", "Contains 20 transactional records with revenue format drift, regional missing values, and duplicate transaction entries.")

    add_h1("Appendix C: Source Code Directory Structure")
    p_code = doc.add_paragraph()
    r_code = p_code.add_run(
        "csv-cleaner-analytics/\n"
        "├── app.py                     # Flask web backend & REST API\n"
        "├── main.py                    # Tkinter desktop GUI application\n"
        "├── run_tests.py               # Automated 24-case unit test runner\n"
        "├── data_analysis_demo.py      # Standalone Pandas/NumPy/Matplotlib script\n"
        "├── core/                      # Core business logic package\n"
        "│   ├── cleaner.py             # Functional cleaning algorithms\n"
        "│   ├── data_manager.py        # State management & DQI scoring\n"
        "│   ├── stats_engine.py        # Summary statistics engine\n"
        "│   ├── exporter.py            # CSV, JSON, TXT exporters\n"
        "│   └── audit_logger.py        # Audit trail generator\n"
        "├── static/                    # Frontend assets (style.css, app.js)\n"
        "├── templates/                 # Web templates (index.html)\n"
        "├── tests/                     # Automated unit test suite\n"
        "├── data/                      # Bundled dirty sample datasets\n"
        "└── vercel.json                # Cloud serverless configuration\n"
    )
    r_code.font.name = 'Consolas'
    r_code.font.size = Pt(9.5)

    doc.save("MAJOR_PROJECT_REPORT.docx")
    print("Major Project Report saved successfully to: MAJOR_PROJECT_REPORT.docx")

if __name__ == "__main__":
    build_report()
