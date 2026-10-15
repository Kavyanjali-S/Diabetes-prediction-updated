"""
PDF Report Generator for AI Diabetes Risk Prediction System
Generates a beginner-friendly, comprehensive project documentation PDF.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import (
    HexColor, white, black
)
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image, KeepTogether
)
from reportlab.platypus import ListFlowable, ListItem
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────
C_NAVY       = HexColor("#0f172a")
C_BLUE       = HexColor("#2563eb")
C_BLUE_LIGHT = HexColor("#3b82f6")
C_INDIGO     = HexColor("#6366f1")
C_TEAL       = HexColor("#0ea5e9")
C_EMERALD    = HexColor("#10b981")
C_AMBER      = HexColor("#f59e0b")
C_RED        = HexColor("#ef4444")
C_GRAY_50    = HexColor("#f8fafc")
C_GRAY_100   = HexColor("#f1f5f9")
C_GRAY_200   = HexColor("#e2e8f0")
C_GRAY_400   = HexColor("#94a3b8")
C_GRAY_600   = HexColor("#475569")
C_GRAY_700   = HexColor("#334155")
C_GRAY_800   = HexColor("#1e293b")
C_CODE_BG    = HexColor("#1e1e2e")
C_CODE_TXT   = HexColor("#cdd6f4")
C_CODE_GREEN = HexColor("#a6e3a1")
C_CODE_PINK  = HexColor("#f38ba8")
C_CODE_BLUE  = HexColor("#89b4fa")
C_CODE_YEL   = HexColor("#f9e2af")

PAGE_W, PAGE_H = A4
LEFT_M  = 2.0 * cm
RIGHT_M = 2.0 * cm
TOP_M   = 2.5 * cm
BOT_M   = 2.5 * cm

# ─────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────
base = getSampleStyleSheet()

def _style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=base[parent])
    for k, v in kw.items():
        setattr(s, k, v)
    return s

sTitle      = _style("sTitle",      "Title",  fontSize=32, textColor=white,     alignment=TA_CENTER, spaceAfter=6,  fontName="Helvetica-Bold")
sSubtitle   = _style("sSubtitle",   "Normal", fontSize=14, textColor=HexColor("#93c5fd"), alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica")
sAuthor     = _style("sAuthor",     "Normal", fontSize=10, textColor=HexColor("#94a3b8"), alignment=TA_CENTER, spaceAfter=2, fontName="Helvetica")

sCh         = _style("sCh",         "Heading1", fontSize=18, textColor=C_BLUE,    spaceBefore=18, spaceAfter=6,  fontName="Helvetica-Bold",  borderPad=4)
sSec        = _style("sSec",        "Heading2", fontSize=13, textColor=C_INDIGO,  spaceBefore=12, spaceAfter=4,  fontName="Helvetica-Bold")
sSubSec     = _style("sSubSec",     "Heading3", fontSize=11, textColor=C_GRAY_700,spaceBefore=8,  spaceAfter=3,  fontName="Helvetica-Bold")

sBody       = _style("sBody",       "Normal", fontSize=10, textColor=C_GRAY_800, leading=16, spaceAfter=6,  fontName="Helvetica", alignment=TA_JUSTIFY)
sBullet     = _style("sBullet",     "Normal", fontSize=10, textColor=C_GRAY_700, leading=15, spaceAfter=3,  fontName="Helvetica", leftIndent=14, firstLineIndent=-14)
sCode       = _style("sCode",       "Normal", fontSize=8.5,textColor=C_CODE_TXT, leading=13, spaceAfter=0,  fontName="Courier",   backColor=C_CODE_BG, leftIndent=8, rightIndent=8)
sCodeLabel  = _style("sCodeLabel",  "Normal", fontSize=8,  textColor=white,      leading=11, spaceAfter=0,  fontName="Courier-Bold", backColor=C_GRAY_800, leftIndent=8)
sNote       = _style("sNote",       "Normal", fontSize=9,  textColor=C_GRAY_600, leading=14, spaceAfter=4,  fontName="Helvetica-Oblique", leftIndent=10, borderPad=4)
sCaption    = _style("sCaption",    "Normal", fontSize=8.5,textColor=C_GRAY_400, leading=12, spaceAfter=6,  fontName="Helvetica-Oblique", alignment=TA_CENTER)
sMetric     = _style("sMetric",     "Normal", fontSize=9,  textColor=C_GRAY_700, leading=14, spaceAfter=2,  fontName="Helvetica")
sStep       = _style("sStep",       "Normal", fontSize=10, textColor=C_GRAY_800, leading=15, spaceAfter=3,  fontName="Helvetica-Bold", leftIndent=30)
sStepBody   = _style("sStepBody",   "Normal", fontSize=10, textColor=C_GRAY_700, leading=15, spaceAfter=5,  fontName="Helvetica", leftIndent=30)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def hline(color=C_GRAY_200, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=6)

def space(h=8):
    return Spacer(1, h)

def bullet(txt):
    return Paragraph(f"• &nbsp; {txt}", sBullet)

def code_block(label, lines):
    """Returns a styled code block with a label bar."""
    elems = []
    # label bar
    elems.append(Paragraph(f"  📄  {label}", sCodeLabel))
    # code lines
    for ln in lines:
        # escape XML
        safe = ln.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        elems.append(Paragraph(safe, sCode))
    elems.append(space(6))
    return KeepTogether(elems)

def chapter_header(num, title, subtitle=""):
    elems = []
    elems.append(space(4))
    # coloured side-bar via a thin table
    bar_data = [[
        Paragraph(f"<font color='#{C_BLUE.hexval()[2:]}'>■</font>  {num}.&nbsp; {title}", sCh)
    ]]
    bar_tbl = Table(bar_data, colWidths=[PAGE_W - LEFT_M - RIGHT_M])
    bar_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), C_GRAY_50),
        ("LINEAFTER",    (0,0),(0,0), 3, C_BLUE),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
    ]))
    elems.append(bar_tbl)
    if subtitle:
        elems.append(Paragraph(subtitle, sNote))
    elems.append(space(4))
    return elems

def info_box(title, body_lines, color=C_TEAL):
    rows = [[Paragraph(f"<b><font color='#{color.hexval()[2:]}'>{title}</font></b>", sSec)]]
    for ln in body_lines:
        rows.append([Paragraph(ln, sBody)])
    tbl = Table(rows, colWidths=[PAGE_W - LEFT_M - RIGHT_M - 30])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), C_GRAY_50),
        ("LEFTPADDING",  (0,0),(-1,-1), 12),
        ("RIGHTPADDING", (0,0),(-1,-1), 12),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LINEAFTER",    (0,0),(-1,-1), 3, color),
        ("BOX",          (0,0),(-1,-1), 0.5, C_GRAY_200),
    ]))
    return [tbl, space(8)]

def step_card(num, title, desc, file_ref=""):
    color = [C_BLUE, C_INDIGO, C_EMERALD, C_AMBER, C_RED, C_TEAL, C_BLUE_LIGHT][num % 7]
    num_cell  = Paragraph(f"<font color='#ffffff'><b>{num}</b></font>", 
                          ParagraphStyle("n", parent=sBody, alignment=TA_CENTER, fontSize=12, fontName="Helvetica-Bold", textColor=white))
    title_p   = Paragraph(f"<b>{title}</b>", 
                          ParagraphStyle("t", parent=sBody, fontSize=10.5, fontName="Helvetica-Bold", textColor=C_GRAY_800, spaceAfter=2))
    desc_p    = Paragraph(desc, 
                          ParagraphStyle("d", parent=sBody, fontSize=9.5, textColor=C_GRAY_600, spaceAfter=0))
    ref_p     = Paragraph(f"<i>File: {file_ref}</i>", 
                          ParagraphStyle("r", parent=sBody, fontSize=8.5, textColor=C_GRAY_400)) if file_ref else Spacer(1,0)
    
    data = [[num_cell, [title_p, desc_p, ref_p]]]
    tbl = Table(data, colWidths=[28, PAGE_W - LEFT_M - RIGHT_M - 40])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), color),
        ("BACKGROUND",    (1,0),(1,0), white),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(0,0), 4),
        ("RIGHTPADDING",  (0,0),(0,0), 4),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (1,0),(1,0), 12),
        ("BOX",           (0,0),(-1,-1), 0.5, C_GRAY_200),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_GRAY_50]),
    ]))
    return [tbl, space(5)]

# ─────────────────────────────────────────────
#  COVER PAGE
# ─────────────────────────────────────────────
def cover_page():
    elems = []
    # full-width navy background simulation via large table
    cover_data = [[Paragraph(
        "<br/><br/><br/>AI-Based Diabetes<br/>Risk Prediction System",
        _style("cTitle","Normal", fontSize=28, textColor=white, fontName="Helvetica-Bold",
               alignment=TA_CENTER, leading=38))],
    [Paragraph("Machine Learning · FastAPI · SQLite · Python", 
               _style("cSub","Normal",fontSize=13,textColor=HexColor("#93c5fd"),
                      fontName="Helvetica",alignment=TA_CENTER,spaceAfter=6))],
    [Paragraph("A Complete Beginner-Friendly Project Documentation", 
               _style("cBy","Normal",fontSize=11,textColor=HexColor("#94a3b8"),
                      fontName="Helvetica-Oblique",alignment=TA_CENTER))],
    [space(20)],
    [Paragraph("Kavya — Project Report  ·  2024",
               _style("cDate","Normal",fontSize=9,textColor=HexColor("#64748b"),
                      fontName="Helvetica",alignment=TA_CENTER))],
    ]
    cover_tbl = Table(cover_data, colWidths=[PAGE_W - LEFT_M - RIGHT_M])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), C_NAVY),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",  (0,0),(-1,-1), 20),
        ("RIGHTPADDING", (0,0),(-1,-1), 20),
    ]))
    elems.append(cover_tbl)
    elems.append(space(20))

    # Quick stats strip
    stats = [
        ("5", "ML Models\nTrained"),
        ("768+", "Patient\nRecords"),
        ("8", "Medical\nFeatures"),
        ("~92%", "Model\nAccuracy"),
    ]
    stat_cells = []
    for val, lbl in stats:
        cell = [
            Paragraph(f"<b><font color='#{C_BLUE.hexval()[2:]}'>{val}</font></b>",
                      _style("sv","Normal",fontSize=20,fontName="Helvetica-Bold",
                             textColor=C_BLUE,alignment=TA_CENTER)),
            Paragraph(lbl.replace("\n","<br/>"),
                      _style("sl","Normal",fontSize=8,fontName="Helvetica",
                             textColor=C_GRAY_600,alignment=TA_CENTER)),
        ]
        stat_cells.append(cell)

    stat_row = [[sc[0] for sc in stat_cells],
                [sc[1] for sc in stat_cells]]
    stat_tbl = Table(stat_row, colWidths=[(PAGE_W-LEFT_M-RIGHT_M)/4]*4)
    stat_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), C_GRAY_50),
        ("BOX",          (0,0),(-1,-1), 0.5, C_GRAY_200),
        ("INNERGRID",    (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ]))
    elems.append(stat_tbl)
    elems.append(PageBreak())
    return elems

# ─────────────────────────────────────────────
#  SECTION 1 – INTRODUCTION
# ─────────────────────────────────────────────
def section_intro():
    e = []
    e += chapter_header("1", "Introduction", "What is this project and why does it matter?")
    e.append(Paragraph(
        "This project is an <b>Artificial Intelligence-powered Diabetes Risk Prediction System</b>. "
        "It uses real medical data about patients — like their blood sugar level, BMI, age, and family "
        "history of diabetes — and runs those numbers through a <b>machine learning (ML) model</b> that "
        "has already learned patterns from hundreds of patients. The model then tells you whether a "
        "new patient is at <b>Low Risk</b>, <b>Moderate Risk</b>, or <b>High Risk</b> of having diabetes.",
        sBody))
    e.append(Paragraph(
        "The system is built as a full web application that anyone can open in their browser. A doctor "
        "or health worker can type in a patient's details, click a button, and instantly get a risk "
        "score along with personalised health recommendations.",
        sBody))
    e.append(space(6))

    e += info_box("🔑 Key Idea (Beginner-Friendly)", [
        "Think of Machine Learning like teaching a computer by example. You show it thousands of "
        "patient records, each labelled 'has diabetes' or 'does not have diabetes'. The computer finds "
        "hidden patterns. Later, when you give it a new, unlabelled patient record, it uses those "
        "patterns to make a prediction — just like a doctor uses experience from past patients."
    ], C_TEAL)

    e.append(Paragraph("What Makes This Project Special?", sSec))
    items = [
        "Trains and compares <b>5 different ML algorithms</b> and automatically picks the best one.",
        "Provides a <b>modern, interactive web dashboard</b> built with FastAPI.",
        "Stores every prediction in a <b>database</b> so doctors can review past results.",
        "Supports <b>batch predictions</b> — upload a CSV file and analyse hundreds of patients at once.",
        "Generates <b>visual charts</b> (correlation heatmaps, model comparison bar charts, etc.).",
        "Gives <b>personalised health recommendations</b> based on the patient's specific risk factors.",
    ]
    for it in items:
        e.append(bullet(it))
    e.append(space(8))
    return e

# ─────────────────────────────────────────────
#  SECTION 2 – PROBLEM STATEMENT
# ─────────────────────────────────────────────
def section_problem():
    e = []
    e += chapter_header("2", "Problem Statement", "What problem does this project solve?")
    e.append(Paragraph(
        "Diabetes is one of the fastest-growing chronic diseases worldwide. According to the World Health "
        "Organization (WHO), over <b>422 million people</b> live with diabetes globally, and millions more "
        "are undiagnosed. Early detection is critical — catching diabetes early can prevent life-threatening "
        "complications like heart disease, kidney failure, and blindness.",
        sBody))
    e.append(Paragraph(
        "Traditional medical screening is time-consuming, expensive, and often requires specialist "
        "consultations. This project addresses three core problems:",
        sBody))
    e.append(space(4))

    prob_data = [
        ["#", "Problem", "How This Project Solves It"],
        ["1", "Manual risk assessment is slow and error-prone",
         "AI model processes 8 medical metrics in milliseconds"],
        ["2", "No data-driven baseline for risk stratification",
         "Trained on the PIMA benchmark diabetes dataset (proven dataset)"],
        ["3", "Results not stored or trackable",
         "SQLite database records every prediction with timestamps"],
        ["4", "Cannot handle large numbers of patients",
         "Batch CSV upload endpoint processes hundreds at once"],
        ["5", "Doctors cannot compare different AI models",
         "Model comparison dashboard with Accuracy, F1, ROC-AUC scores"],
    ]
    prob_tbl = Table(prob_data, colWidths=[18, 160, 195])
    prob_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_NAVY),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ALIGN",         (0,0),(-1,0), "CENTER"),
        ("BACKGROUND",    (0,1),(-1,-1), C_GRAY_50),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTSIZE",      (0,1),(-1,-1), 8.5),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.4, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
    ]))
    e.append(prob_tbl)
    e.append(space(8))
    return e

# ─────────────────────────────────────────────
#  SECTION 3 – DATASET
# ─────────────────────────────────────────────
def section_dataset():
    e = []
    e += chapter_header("3", "Dataset", "What data is used to teach the AI?")
    e.append(Paragraph(
        "The project uses the <b>PIMA Indians Diabetes Dataset</b>, one of the most well-known and "
        "widely studied datasets in medical machine learning. Originally collected by the National "
        "Institute of Diabetes and Digestive and Kidney Diseases (NIDDK) in the USA, it contains "
        "medical records from <b>Pima Indian women</b> aged 21 and above.",
        sBody))
    e.append(space(4))

    e.append(Paragraph("Dataset Features (Columns)", sSec))
    e.append(Paragraph(
        "Each row in the dataset represents <b>one patient</b>. The following 8 features "
        "are used as inputs to the model, plus one output (Outcome):",
        sBody))
    e.append(space(4))

    feat_data = [
        ["Column Name", "Plain English Description", "Unit / Range", "Why It Matters"],
        ["Pregnancies", "Number of times patient was pregnant", "0 – 17", "More pregnancies → higher risk"],
        ["Glucose", "Blood sugar level (2-hr glucose test)", "0 – 200 mg/dL", "Primary diabetes indicator"],
        ["BloodPressure", "Diastolic blood pressure", "0 – 122 mm Hg", "High BP linked to insulin resistance"],
        ["SkinThickness", "Triceps skin fold thickness", "0 – 60 mm", "Proxy for body fat percentage"],
        ["Insulin", "2-hour serum insulin level", "0 – 450 μU/mL", "Measures insulin response"],
        ["BMI", "Body Mass Index", "0 – 70 kg/m²", "Obesity is a major risk factor"],
        ["DiabetesPedigreeFunction", "Genetic/family history score", "0.08 – 2.42", "Family history increases risk"],
        ["Age", "Patient age in years", "21 – 81", "Risk rises with age"],
        ["Outcome", "1 = Diabetic, 0 = Not Diabetic", "Binary", "Target label (what we predict)"],
    ]
    feat_tbl = Table(feat_data, colWidths=[100, 155, 80, 130])
    feat_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_INDIGO),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 8.5),
        ("ALIGN",         (0,0),(-1,0), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("TEXTCOLOR",     (0,1),(-1,-1), C_GRAY_800),
    ]))
    e.append(feat_tbl)
    e.append(space(8))

    e += info_box("📊 Data Preprocessing — Fixing Zeroes", [
        "Some columns like Glucose and BMI had values of zero, which is biologically impossible "
        "(you cannot have 0 blood sugar and be alive!). These zeroes are actually missing data "
        "recorded as zero. The code detects them and replaces each zero with the <b>median value</b> "
        "of that column — a simple but effective fix.",
        "The dataset is stored in: <b>data/diabetes.csv</b> (800 patient records)."
    ], C_EMERALD)
    return e

# ─────────────────────────────────────────────
#  SECTION 4 – LIBRARIES & TECH STACK
# ─────────────────────────────────────────────
def section_libraries():
    e = []
    e += chapter_header("4", "Libraries, AI Tools & External Sources",
                        "Every tool and library used — explained simply.")

    e.append(Paragraph("Python Libraries", sSec))

    libs = [
        ("FastAPI", "The web framework that creates all the API endpoints (the URLs your browser calls). "
         "It's modern, fast, and automatically generates interactive API documentation."),
        ("Uvicorn", "The web server that actually runs the FastAPI application. Think of it as the "
         "engine that keeps the app running on your computer at http://127.0.0.1:8000."),
        ("Scikit-learn", "The core machine learning library. Provides Logistic Regression, Random Forest, "
         "Gradient Boosting, SVM, StandardScaler, train_test_split, and all evaluation metrics."),
        ("XGBoost", "A highly optimised gradient boosting library. Famous for winning many data science "
         "competitions. It builds trees sequentially, each correcting the previous one's mistakes."),
        ("Pandas", "Used to load, clean, and manipulate the CSV dataset as a 'DataFrame' — a table-like "
         "structure similar to Excel but much more powerful for programmatic use."),
        ("NumPy", "Provides fast numerical array operations. Used for mathematical computations like "
         "logistic functions, array clipping, and statistical calculations."),
        ("Matplotlib", "The base library for creating plots and charts (saved as PNG files for display "
         "in the web dashboard)."),
        ("Seaborn", "Built on top of Matplotlib, Seaborn creates beautiful statistical charts with "
         "less code — used for heatmaps, histograms, and box plots."),
        ("Joblib", "Saves the trained ML model and scaler to disk as .joblib files so you don't need "
         "to retrain every time the server starts."),
        ("Pydantic", "Validates the data sent to the API. If someone sends a negative glucose value, "
         "Pydantic automatically rejects it with a helpful error message."),
        ("SQLite3", "A lightweight file-based database (built into Python). Stores every prediction "
         "record including patient name, input values, and predicted risk."),
        ("Jinja2", "A templating engine that lets FastAPI serve HTML pages with dynamic data embedded."),
        ("python-multipart", "Enables file upload support in FastAPI — required for the batch CSV upload feature."),
    ]

    lib_data = [["Library", "Version", "Purpose"]]
    version_map = {
        "FastAPI": "≥ 0.115", "Uvicorn": "≥ 0.34", "Scikit-learn": "≥ 1.6",
        "XGBoost": "≥ 2.0", "Pandas": "≥ 2.0", "NumPy": "≥ 1.24",
        "Matplotlib": "≥ 3.8", "Seaborn": "≥ 0.13", "Joblib": "≥ 1.3",
        "Pydantic": "≥ 2.0", "SQLite3": "Built-in", "Jinja2": "≥ 3.1",
        "python-multipart": "≥ 0.0.20",
    }
    for name, desc in libs:
        lib_data.append([name, version_map.get(name, "—"), desc])

    lib_tbl = Table(lib_data, colWidths=[90, 65, 308])
    lib_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("FONTNAME",      (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("TEXTCOLOR",     (1,1),(1,-1), C_INDIGO),
    ]))
    e.append(lib_tbl)
    e.append(space(10))

    e.append(Paragraph("Frontend Technologies (Browser Side)", sSec))
    front = [
        ("Chart.js (CDN)", "Interactive doughnut and bar charts shown in the web dashboard. "
         "Loaded from a CDN (Content Delivery Network) — no local install needed."),
        ("Bootstrap 5 (CDN)", "A popular CSS framework that makes the website look polished and "
         "responsive on any screen size."),
        ("Vanilla JavaScript", "Custom JS in static/js/ handles form submission, API calls (fetch), "
         "chart updates, and dynamic table rendering — no React or Vue needed."),
        ("HTML5 + Jinja2", "The templates/index.html file is an HTML page with Jinja2 placeholders "
         "filled by FastAPI before sending to the browser."),
    ]
    for name, desc in front:
        e.append(bullet(f"<b>{name}</b> — {desc}"))
    e.append(space(8))

    e += info_box("🤖 AI / ML Algorithms Used", [
        "<b>Logistic Regression</b> — Classic algorithm that models the probability of a binary outcome using a sigmoid curve. Best ROC-AUC: 0.866.",
        "<b>Random Forest</b> — Ensemble of many decision trees that vote on the result. Robust and interpretable via feature importance.",
        "<b>Gradient Boosting</b> — Builds trees one-by-one, each tree fixing the errors of the last. Very accurate on tabular data.",
        "<b>XGBoost</b> — Extreme Gradient Boosting. Optimised version of Gradient Boosting with regularisation, extremely popular in competitions.",
        "<b>Support Vector Machine (SVM)</b> — Finds the best hyperplane that separates diabetic from non-diabetic patients in feature space.",
    ], C_INDIGO)
    return e

# ─────────────────────────────────────────────
#  SECTION 5 – PROJECT STRUCTURE
# ─────────────────────────────────────────────
def section_structure():
    e = []
    e += chapter_header("5", "Project File Structure", "A map of every file and what it does.")

    struct_data = [
        ["File / Folder", "Role"],
        ["app.py", "FastAPI backend server. Defines all API routes and loads the ML model."],
        ["train_model.py", "ML training pipeline: loads data, does EDA, trains 5 models, saves the best."],
        ["database.py", "SQLite database manager: creates tables, saves & retrieves predictions."],
        ["test_app.py", "Automated test suite using Python's unittest and FastAPI TestClient."],
        ["requirements.txt", "Lists all Python packages needed to run the project."],
        ["data/diabetes.csv", "The PIMA diabetes dataset (800 patient records, 9 columns)."],
        ["data/predictions.db", "SQLite database file storing all prediction records."],
        ["models/diabetes_model.joblib", "The best trained ML model saved to disk."],
        ["models/scaler.joblib", "The StandardScaler used to normalise patient inputs."],
        ["models/model_comparison.json", "JSON file with accuracy, F1, ROC-AUC scores for all 5 models."],
        ["static/css/", "CSS stylesheets for the web dashboard (glassmorphism styling)."],
        ["static/js/", "JavaScript for charts, form handling, and API calls."],
        ["static/eda_plots/", "Generated PNG charts: heatmap, distributions, feature importance."],
        ["templates/index.html", "Single-page HTML app served by FastAPI."],
    ]
    s_tbl = Table(struct_data, colWidths=[165, 298])
    s_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_GRAY_800),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTSIZE",      (0,1),(-1,-1), 8.5),
        ("FONTNAME",      (0,1),(0,-1), "Courier"),
        ("FONTNAME",      (1,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("TEXTCOLOR",     (0,1),(0,-1), C_BLUE),
    ]))
    e.append(s_tbl)
    e.append(space(8))
    return e

# ─────────────────────────────────────────────
#  SECTION 6 – STEP-BY-STEP FLOW
# ─────────────────────────────────────────────
def section_flow():
    e = []
    e += chapter_header("6", "Step-by-Step Application Flow",
                        "How everything works from start to finish.")

    e.append(Paragraph(
        "Here is the complete journey of the system, explained step-by-step as if you are a "
        "doctor entering a patient's data for the first time.",
        sBody))
    e.append(space(6))

    steps = [
        ("PHASE A — TRAINING (done once, before the server starts)",),
        (1, "Load or Generate Dataset",
         "train_model.py reads data/diabetes.csv. If the file doesn't exist, it synthetically generates "
         "800 patient records using statistical distributions that mirror the real PIMA dataset.",
         "train_model.py → generate_or_load_dataset()"),
        (2, "Clean & Preprocess Data",
         "Any column values of 0 that are biologically impossible (e.g., zero BMI, zero glucose) are "
         "detected and replaced with the column's median value. This prevents the model from learning "
         "false patterns.",
         "train_model.py → preprocess_and_eda()"),
        (3, "Exploratory Data Analysis (EDA)",
         "4 charts are automatically generated and saved as PNG files: (a) Correlation Heatmap showing "
         "how features relate to each other; (b) Distribution plots by diabetes outcome; "
         "(c) Feature Importance ranking; (d) Model comparison bar chart.",
         "train_model.py → preprocess_and_eda()"),
        (4, "Split Data into Training & Testing Sets",
         "80% of data is used to teach the model (training set). 20% is held back to test how well "
         "the model performs on patients it has never seen (test set). Stratified split ensures "
         "both sets have the same proportion of diabetic/non-diabetic patients.",
         "train_model.py → train_and_evaluate_models()"),
        (5, "Scale the Features (Normalisation)",
         "All 8 input features are scaled to have mean=0 and std=1 using StandardScaler. This is "
         "important because features like Insulin (0-450) and Age (21-81) have very different ranges. "
         "Without scaling, larger-range features would unfairly dominate the model.",
         "train_model.py → StandardScaler"),
        (6, "Train 5 ML Models & Compare",
         "Five classifiers are trained: Logistic Regression, Random Forest, Gradient Boosting, "
         "XGBoost, and SVM. Each is evaluated using Accuracy, Precision, Recall, F1-Score, ROC-AUC, "
         "and 5-fold Cross-Validation. The model with the highest ROC-AUC score wins.",
         "train_model.py → models dict"),
        (7, "Save the Best Model",
         "The winning model is serialised with joblib.dump() to models/diabetes_model.joblib. "
         "The scaler is saved to models/scaler.joblib. Results are saved to model_comparison.json.",
         "train_model.py → joblib.dump()"),

        ("PHASE B — RUNTIME (every time a user visits the app)",),
        (8, "Server Starts",
         "Running python app.py starts the FastAPI server. It immediately loads the trained model "
         "and scaler from disk, and initialises the SQLite database (creating tables if they don't exist). "
         "Sample patient records are pre-loaded for an immediate demo.",
         "app.py → main block, database.init_db()"),
        (9, "User Opens the Dashboard",
         "The browser sends a GET request to http://127.0.0.1:8000/. FastAPI returns the index.html "
         "template. JavaScript immediately calls /api/dashboard to populate the stat cards "
         "(total predictions, high-risk %, avg glucose, avg BMI).",
         "app.py → serve_dashboard(), templates/index.html"),
        (10, "Doctor Enters Patient Data",
         "The interactive form has sliders and text fields for all 8 medical features. As the doctor "
         "adjusts each slider, the number input stays synchronised in real time. The form validates "
         "inputs on the client side before submitting.",
         "static/js/ → form event listeners"),
        (11, "Prediction API Called",
         "On form submit, JavaScript sends a POST request to /api/predict with the patient data as JSON. "
         "FastAPI's Pydantic model validates all fields (e.g., glucose must be 0–300). "
         "The 8 feature values are assembled into a DataFrame.",
         "app.py → predict_diabetes_risk()"),
        (12, "Model Makes a Prediction",
         "The input DataFrame is scaled using the saved StandardScaler. The scaled data is passed to "
         "model.predict() (binary: 0 or 1) and model.predict_proba() (probability between 0 and 1). "
         "A probability < 35% → Low Risk, 35–65% → Moderate Risk, > 65% → High Risk.",
         "app.py → predict_diabetes_risk()"),
        (13, "Health Recommendations Generated",
         "Based on the specific values entered (e.g., glucose > 140 triggers a blood test recommendation, "
         "BMI > 30 triggers an exercise recommendation), personalised advice is generated without "
         "using any AI — pure if/else logic for transparency and medical safety.",
         "app.py → generate_health_recommendations()"),
        (14, "Result Saved to Database",
         "The prediction (including patient name, all 8 inputs, probability, risk level, and model "
         "used) is saved to the SQLite database via database.save_prediction(). Every prediction is "
         "timestamped and given a unique ID.",
         "database.py → save_prediction()"),
        (15, "Result Displayed in Browser",
         "The JSON response is received by JavaScript. The circular SVG risk gauge animates to the "
         "predicted probability. The risk badge changes colour (green/orange/red). "
         "Risk factors and recommendations are rendered in styled cards below.",
         "templates/index.html + static/js/"),
        (16, "History & Analytics Updated",
         "The prediction history table is refreshed to show all past records. The doctor can export "
         "records to CSV or delete individual entries. Model comparison charts and EDA plots "
         "are viewable in separate dashboard tabs.",
         "app.py → /api/history, /api/model-comparison"),
    ]

    for item in steps:
        if len(item) == 1:
            # Phase header
            e.append(space(8))
            phase_data = [[Paragraph(item[0], _style("ph","Normal",fontSize=10,fontName="Helvetica-Bold",
                                                      textColor=white,alignment=TA_CENTER))]]
            phase_tbl = Table(phase_data, colWidths=[PAGE_W-LEFT_M-RIGHT_M])
            phase_tbl.setStyle(TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), C_NAVY),
                ("TOPPADDING",   (0,0),(-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ]))
            e.append(phase_tbl)
            e.append(space(5))
        else:
            num, title, desc, fref = item
            e += step_card(num, title, desc, fref)

    e.append(space(10))
    return e

# ─────────────────────────────────────────────
#  SECTION 7 – CODE SNIPPETS
# ─────────────────────────────────────────────
def section_code():
    e = []
    e += chapter_header("7", "Key Code Snippets with Explanations",
                        "Important parts of the code, explained line by line.")

    snippets = [
        {
            "title": "1. PatientMetrics – Data Validation Model",
            "file": "app.py  (Lines 45–55)",
            "desc": (
                "This Pydantic class defines what patient data looks like. Pydantic automatically "
                "validates every field — if someone sends glucose=500 (above the max of 300), "
                "FastAPI will immediately return an error without even reaching the prediction code. "
                "This is a safety net for the entire API."
            ),
            "lines": [
                "class PatientMetrics(BaseModel):",
                "    patient_name: str = Field(default='Anonymous Patient')",
                "    pregnancies: int = Field(ge=0, le=20, default=1)",
                "    glucose: float = Field(ge=0.0, le=300.0, default=120.0)",
                "    blood_pressure: float = Field(ge=0.0, le=200.0, default=70.0)",
                "    skin_thickness: float = Field(ge=0.0, le=100.0, default=20.0)",
                "    insulin: float = Field(ge=0.0, le=900.0, default=79.0)",
                "    bmi: float = Field(ge=0.0, le=70.0, default=28.5)",
                "    dpf: float = Field(ge=0.0, le=3.0, default=0.47)",
                "    age: int = Field(ge=1, le=120, default=33)",
                "# ge = greater than or equal to (minimum value)",
                "# le = less than or equal to (maximum value)",
            ],
        },
        {
            "title": "2. The Prediction API Endpoint",
            "file": "app.py  (Lines 98–151)",
            "desc": (
                "This is the heart of the application. When a doctor submits patient data, this "
                "function runs. It: (1) converts data to a DataFrame, (2) scales the values, "
                "(3) gets prediction + probability, (4) assigns risk level, (5) saves to DB, "
                "and (6) returns a rich JSON response."
            ),
            "lines": [
                "@app.post('/api/predict')",
                "async def predict_diabetes_risk(metrics: PatientMetrics):",
                "    # Step 1: Build a DataFrame from the patient's input",
                "    feature_names = ['Pregnancies','Glucose','BloodPressure',",
                "                     'SkinThickness','Insulin','BMI',",
                "                     'DiabetesPedigreeFunction','Age']",
                "    input_df = pd.DataFrame([[",
                "        metrics.pregnancies, metrics.glucose, ...",
                "    ]], columns=feature_names)",
                "",
                "    # Step 2: Scale the input using the saved StandardScaler",
                "    input_scaled = scaler.transform(input_df)",
                "",
                "    # Step 3: Get binary prediction (0 or 1) and probability",
                "    prediction_class = int(model.predict(input_scaled)[0])",
                "    prob_positive = float(model.predict_proba(input_scaled)[0][1])",
                "",
                "    # Step 4: Assign Risk Level",
                "    if prob_positive < 0.35:  risk_level = 'Low Risk'",
                "    elif prob_positive < 0.65: risk_level = 'Moderate Risk'",
                "    else:                      risk_level = 'High Risk'",
                "",
                "    # Step 5: Save to database",
                "    database.save_prediction(record_data)",
            ],
        },
        {
            "title": "3. Health Recommendations Logic",
            "file": "app.py  (Lines 57–92)",
            "desc": (
                "Instead of a 'black box' AI for recommendations, the system uses clear, "
                "transparent rule-based logic. This is intentional — in medical applications, "
                "doctors need to understand exactly why a recommendation was made. "
                "Each if-condition maps to a known clinical threshold."
            ),
            "lines": [
                "def generate_health_recommendations(data, prob, risk_level):",
                "    recommendations = []",
                "    risk_factors = []",
                "",
                "    # Glucose check — Clinical threshold: pre-diabetes starts at 100 mg/dL",
                "    if data['glucose'] >= 140:",
                "        risk_factors.append('High Plasma Glucose (> 140 mg/dL)')",
                "        recommendations.append('Schedule a Fasting Blood Sugar test.')",
                "    elif data['glucose'] >= 100:",
                "        recommendations.append('Reduce refined sugars in daily diet.')",
                "",
                "    # BMI check — WHO defines obesity as BMI >= 30",
                "    if data['bmi'] >= 30:",
                "        risk_factors.append('Obesity (BMI >= 30)')",
                "        recommendations.append('Aim for 150 min of exercise per week.')",
                "",
                "    # Genetic predisposition check",
                "    if data['dpf'] > 0.5:",
                "        recommendations.append('Perform annual diabetes screening.')",
            ],
        },
        {
            "title": "4. Training 5 ML Models",
            "file": "train_model.py  (Lines 156–211)",
            "desc": (
                "This section trains all 5 models in a loop, evaluates each one, and automatically "
                "picks the best. 'Best' is defined as highest ROC-AUC score — a metric that measures "
                "how well the model distinguishes diabetic from non-diabetic patients across all "
                "decision thresholds, not just one fixed threshold."
            ),
            "lines": [
                "models = {",
                "    'Logistic Regression': LogisticRegression(max_iter=1000),",
                "    'Random Forest':       RandomForestClassifier(n_estimators=100),",
                "    'Gradient Boosting':   GradientBoostingClassifier(n_estimators=100),",
                "    'XGBoost':             xgb.XGBClassifier(n_estimators=100),",
                "    'Support Vector Machine': SVC(probability=True),",
                "}",
                "",
                "best_score = 0",
                "for name, model in models.items():",
                "    model.fit(X_train_scaled, y_train)",
                "    y_proba = model.predict_proba(X_test_scaled)[:, 1]",
                "    auc = roc_auc_score(y_test, y_proba)",
                "    if auc > best_score:",
                "        best_score = auc",
                "        best_model_obj = model   # Track the champion",
                "",
                "# Save the champion model to disk",
                "joblib.dump(best_model_obj, 'models/diabetes_model.joblib')",
            ],
        },
        {
            "title": "5. Zero-Value Imputation in Preprocessing",
            "file": "train_model.py  (Lines 95–118)",
            "desc": (
                "This preprocessing step is critical for model quality. It detects biologically "
                "impossible zero values (no one has a BMI of 0!) and replaces them with the median "
                "of valid (non-zero) values in that column. Using median instead of mean makes this "
                "robust to outliers."
            ),
            "lines": [
                "zero_cols = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']",
                "",
                "for col in zero_cols:",
                "    zero_count = (df_clean[col] == 0).sum()",
                "    if zero_count > 0:",
                "        print(f'Imputing {zero_count} zeros in \"{col}\" ...')",
                "        # Calculate median using ONLY non-zero rows (valid data)",
                "        median_val = df_clean[df_clean[col] != 0][col].median()",
                "        # Replace all 0s in this column with the median",
                "        df_clean[col] = df_clean[col].replace(0, median_val)",
            ],
        },
        {
            "title": "6. SQLite Database — Save Prediction",
            "file": "database.py  (Lines 57–89)",
            "desc": (
                "Every time the AI makes a prediction, this function stores the full record in a "
                "SQLite database. SQLite is a file-based database — no server setup needed. "
                "The conn.row_factory = sqlite3.Row setting makes query results behave like "
                "Python dictionaries, making JSON conversion easy."
            ),
            "lines": [
                "def save_prediction(data):",
                "    conn = sqlite3.connect('data/predictions.db')",
                "    conn.row_factory = sqlite3.Row  # Rows act like dicts",
                "    cursor = conn.cursor()",
                "",
                "    cursor.execute('''",
                "        INSERT INTO predictions (",
                "            timestamp, patient_name, pregnancies, glucose,",
                "            blood_pressure, bmi, prediction, probability, risk_level",
                "        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                "    ''', (timestamp, name, pregnancies, glucose, bp, bmi,",
                "          prediction, probability, risk_level))",
                "",
                "    inserted_id = cursor.lastrowid  # Get auto-generated ID",
                "    conn.commit()  # Save changes to disk",
                "    conn.close()",
                "    return inserted_id",
            ],
        },
        {
            "title": "7. Batch CSV Prediction Endpoint",
            "file": "app.py  (Lines 178–231)",
            "desc": (
                "This endpoint allows uploading a CSV file with many patients and getting predictions "
                "for all of them in one request. The CSV is read into a Pandas DataFrame, scaled, "
                "and run through model.predict() on all rows simultaneously — much faster than "
                "calling the single-patient API for each one."
            ),
            "lines": [
                "@app.post('/api/batch-predict')",
                "async def batch_predict(file: UploadFile = File(...)):",
                "    # Read the uploaded CSV bytes",
                "    contents = await file.read()",
                "    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))",
                "",
                "    # Validate required columns exist",
                "    required_cols = ['Pregnancies','Glucose','BloodPressure',...]",
                "    missing = [c for c in required_cols if c not in df.columns]",
                "    if missing: raise HTTPException(400, f'Missing: {missing}')",
                "",
                "    # Scale and predict ALL rows at once (vectorised = very fast)",
                "    X_batch_scaled = scaler.transform(df[required_cols])",
                "    preds  = model.predict(X_batch_scaled)",
                "    probas = model.predict_proba(X_batch_scaled)[:, 1]",
                "    # Save each result to the database",
                "    for idx, row in df.iterrows():",
                "        database.save_prediction(record)",
            ],
        },
    ]

    for snip in snippets:
        e.append(Paragraph(snip["title"], sSec))
        e.append(Paragraph(snip["desc"], sBody))
        e += [code_block(snip["file"], snip["lines"])]
        e.append(space(6))

    return e

# ─────────────────────────────────────────────
#  SECTION 8 – MODEL PERFORMANCE
# ─────────────────────────────────────────────
def section_performance():
    e = []
    e += chapter_header("8", "Model Performance Results",
                        "How well do each of the 5 models perform?")

    e.append(Paragraph(
        "After training all 5 models on the diabetes dataset, the following scores were recorded "
        "on the held-out 20% test set (160 patients the model has never seen during training).",
        sBody))
    e.append(space(6))

    # Header row
    data = [["Model", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "CV Mean"]]
    rows = [
        ("Logistic Regression", 0.925, 0.9295, 0.9932, 0.9603, 0.8664, 0.9203),
        ("Random Forest",       0.9187, 0.9236, 0.9932, 0.9571, 0.7975, 0.9219),
        ("Gradient Boosting",   0.9125, 0.9286, 0.9795, 0.9533, 0.8322, 0.9062),
        ("XGBoost",             0.925,  0.9351, 0.9863, 0.9600, 0.8249, 0.9156),
        ("Support Vector Machine", 0.9125, 0.9125, 1.0000, 0.9542, 0.6874, 0.9141),
    ]
    best_auc = max(r[5] for r in rows)
    for row in rows:
        is_best = row[5] == best_auc
        data.append([
            f"★ {row[0]}" if is_best else row[0],
            f"{row[1]:.1%}", f"{row[2]:.1%}", f"{row[3]:.1%}",
            f"{row[4]:.1%}", f"{row[5]:.4f}", f"{row[6]:.1%}"
        ])

    perf_tbl = Table(data, colWidths=[115, 58, 58, 50, 55, 58, 55])
    perf_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_NAVY),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 8),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("BACKGROUND",    (0,1),(0,1), HexColor("#fef3c7")),  # highlight best row
        ("FONTNAME",      (0,1),(0,1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ]))
    e.append(perf_tbl)
    e.append(space(4))
    e.append(Paragraph(
        "★ Logistic Regression was selected as the best model with the highest ROC-AUC of 0.8664. "
        "ROC-AUC measures the model's ability to rank diabetic patients higher than non-diabetic ones "
        "across all decision thresholds — a more reliable metric than simple accuracy.",
        sNote))
    e.append(space(6))

    e.append(Paragraph("Understanding the Metrics (Beginner Glossary)", sSec))
    metrics_def = [
        ("Accuracy", "% of all patients correctly classified (diabetic + non-diabetic combined)."),
        ("Precision", "Of all patients predicted diabetic, how many actually are diabetic? "
         "High precision = few false alarms."),
        ("Recall", "Of all actually diabetic patients, how many did we correctly catch? "
         "High recall = fewer missed diagnoses (crucial in medicine)."),
        ("F1-Score", "Harmonic mean of Precision and Recall. Balances both — a single summary score."),
        ("ROC-AUC", "Area Under the ROC Curve. 1.0 = perfect, 0.5 = random guessing. "
         "Best single metric for imbalanced medical datasets."),
        ("CV Mean", "5-fold Cross-Validation accuracy. Tests the model on 5 different splits — "
         "shows if the model is consistent, not just lucky on one split."),
    ]
    m_data = [["Metric", "Plain English Meaning"]]
    for name, desc in metrics_def:
        m_data.append([name, desc])
    m_tbl = Table(m_data, colWidths=[95, 368])
    m_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_GRAY_800),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTSIZE",      (0,1),(-1,-1), 8.5),
        ("FONTNAME",      (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("TEXTCOLOR",     (1,1),(1,-1), C_GRAY_700),
    ]))
    e.append(m_tbl)
    e.append(space(8))
    return e

# ─────────────────────────────────────────────
#  SECTION 9 – API REFERENCE
# ─────────────────────────────────────────────
def section_api():
    e = []
    e += chapter_header("9", "API Endpoints Reference",
                        "All web API URLs the application exposes.")

    e.append(Paragraph(
        "An API (Application Programming Interface) is how the browser (frontend) talks to the "
        "Python server (backend). FastAPI automatically generates interactive documentation at "
        "<b>http://127.0.0.1:8000/docs</b> where you can test all endpoints.",
        sBody))
    e.append(space(6))

    endpoints = [
        ["Method", "URL", "Description"],
        ["GET",    "/",                      "Serves the main web dashboard (index.html)"],
        ["POST",   "/api/predict",           "Single patient prediction (JSON body → risk score + recommendations)"],
        ["POST",   "/api/batch-predict",     "Multi-patient CSV file upload → bulk predictions"],
        ["GET",    "/api/history",           "Returns all saved prediction records from SQLite"],
        ["DELETE", "/api/history/{id}",      "Deletes a specific prediction record by its ID"],
        ["GET",    "/api/dashboard",         "Returns aggregated stats: total, high-risk %, averages"],
        ["GET",    "/api/model-comparison",  "Returns JSON with all 5 model accuracy/F1/AUC scores"],
        ["GET",    "/docs",                  "Auto-generated interactive API documentation (Swagger UI)"],
    ]
    api_tbl = Table(endpoints, colWidths=[42, 130, 291])
    method_colors = {"GET": C_EMERALD, "POST": C_BLUE, "DELETE": C_RED}
    api_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_NAVY),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTNAME",      (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,1),(1,-1), "Courier"),
        ("FONTNAME",      (2,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1), 8.5),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (0,0),(0,-1), "CENTER"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
    ]))
    e.append(api_tbl)
    e.append(space(8))
    return e

# ─────────────────────────────────────────────
#  SECTION 10 – HOW TO RUN
# ─────────────────────────────────────────────
def section_howto():
    e = []
    e += chapter_header("10", "How to Run the Project",
                        "Step-by-step setup guide for a complete beginner.")

    steps_run = [
        ("Install Python 3.10+",
         "Download Python from python.org/downloads. During installation, check "
         "'Add Python to PATH'. Verify in terminal: python --version"),
        ("Download / Clone the Project",
         "Place all project files in a folder. Open a terminal and navigate to "
         "that folder: cd path/to/project"),
        ("Install Dependencies",
         "Run: pip install -r requirements.txt  — This installs all 12 libraries "
         "listed in requirements.txt. Takes 2–5 minutes."),
        ("Train the Model (Optional — model already exists)",
         "Run: python train_model.py  — This generates EDA charts and trains all 5 "
         "models. The best model is automatically saved. Skip if model files already exist."),
        ("Start the Web Server",
         "Run: python app.py  — You will see: 'Uvicorn running on http://127.0.0.1:8000'"),
        ("Open the Dashboard",
         "Open your browser and go to: http://127.0.0.1:8000  — The full dashboard "
         "will load with the prediction form and analytics."),
        ("Run Automated Tests",
         "Run: python test_app.py  — 7 tests will run covering all API endpoints. "
         "All should show 'OK' if everything is working correctly."),
    ]

    for i, (title, desc) in enumerate(steps_run, 1):
        e += step_card(i, title, desc)

    e.append(space(8))
    e += info_box("⚠️ Important Notes", [
        "The model files (models/diabetes_model.joblib and models/scaler.joblib) must exist "
        "before starting the server. If they don't, run python train_model.py first.",
        "The default port is 8000. If that port is busy, change the port in app.py: "
        "uvicorn.run('app:app', port=8001)",
        "For batch predictions, your CSV must have these exact column names: "
        "Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age",
    ], C_AMBER)
    return e

# ─────────────────────────────────────────────
#  SECTION 11 – EDA PLOTS
# ─────────────────────────────────────────────
def section_plots():
    e = []
    e += chapter_header("11", "Data Analysis Visualisations",
                        "Charts generated by train_model.py — what they show.")

    plot_info = [
        ("static/eda_plots/correlation_matrix.png",
         "Correlation Heatmap",
         "Shows how strongly each pair of features is related. "
         "Values close to +1 (dark blue) = strong positive correlation. "
         "Values close to -1 (dark red) = strong negative correlation. "
         "Notice that Glucose has the strongest positive correlation with diabetes Outcome."),
        ("static/eda_plots/risk_distribution.png",
         "Risk Distribution by Outcome",
         "Four plots showing how Glucose, BMI, Age, and Diabetes Pedigree Function "
         "are distributed differently for diabetic (orange) vs non-diabetic (green) patients. "
         "Diabetic patients clearly have higher average glucose and BMI."),
        ("static/eda_plots/feature_importance.png",
         "Feature Importance (Random Forest)",
         "Shows which of the 8 features the Random Forest model considers most important. "
         "Glucose tops the chart, followed by BMI and Age. This confirms medical knowledge — "
         "blood sugar level is the primary diabetes indicator."),
        ("static/eda_plots/model_comparison.png",
         "Model Comparison Bar Chart",
         "Side-by-side comparison of Accuracy, F1-Score, and ROC-AUC for all 5 models. "
         "Useful for understanding trade-offs — e.g., SVM has perfect Recall (catches every "
         "diabetic case) but the lowest ROC-AUC among the models."),
    ]

    base_dir = r"d:\Kavya\New folder"
    for path, title, desc in plot_info:
        full_path = os.path.join(base_dir, path.replace("/", os.sep))
        e.append(Paragraph(title, sSec))
        e.append(Paragraph(desc, sBody))
        if os.path.exists(full_path):
            try:
                img = Image(full_path, width=13*cm, height=8*cm)
                img.hAlign = "CENTER"
                e.append(img)
                e.append(Paragraph(f"Figure: {title}", sCaption))
            except Exception as ex:
                e.append(Paragraph(f"[Chart image could not be loaded: {ex}]", sNote))
        else:
            e.append(Paragraph(f"[Image not found at: {full_path}]", sNote))
        e.append(space(10))

    return e

# ─────────────────────────────────────────────
#  SECTION 12 – GLOSSARY
# ─────────────────────────────────────────────
def section_glossary():
    e = []
    e += chapter_header("12", "Glossary of Terms",
                        "Plain-English definitions of every technical term used in this project.")

    terms = [
        ("API", "Application Programming Interface — a way for two programs to communicate. Like a waiter who takes your order (request) to the kitchen (server) and brings back food (response)."),
        ("Batch Prediction", "Running the AI model on many patients at once by uploading a spreadsheet (CSV file) instead of entering one patient at a time."),
        ("BMI (Body Mass Index)", "A number calculated from height and weight. Below 18.5 = underweight, 18.5–24.9 = normal, 25–29.9 = overweight, 30+ = obese."),
        ("Classification", "A type of machine learning where the output is a category (e.g., 'diabetic' or 'not diabetic') rather than a number."),
        ("Cross-Validation", "A technique to test the model on multiple different train/test splits to check if it performs consistently, not just by luck."),
        ("CSV", "Comma-Separated Values — a simple spreadsheet format where each row is a patient and each column is separated by commas."),
        ("DataFrame", "A table structure in Pandas similar to a spreadsheet with named columns, used to hold and manipulate dataset rows."),
        ("Ensemble", "Combining multiple models to make a better prediction. Random Forest is an ensemble of many decision trees."),
        ("F1-Score", "A score between 0 and 1 that balances Precision and Recall. Important when false negatives (missing a diabetic patient) are costly."),
        ("FastAPI", "A modern Python web framework for building APIs. Automatically validates inputs and generates documentation."),
        ("Feature", "An individual measurable property of a patient, e.g., glucose level, BMI, or age."),
        ("Gradient Boosting", "An ML technique where models are built sequentially, each correcting the previous model's mistakes."),
        ("Imputation", "Filling in missing or invalid data values with a statistical estimate (like the median)."),
        ("Joblib", "A Python library that saves (serialises) Python objects like ML models to disk files so they can be reloaded later."),
        ("Logistic Regression", "A classification algorithm that estimates the probability of a binary outcome using a mathematical S-shaped curve (sigmoid)."),
        ("ML (Machine Learning)", "A method of teaching computers to learn from examples rather than explicit programming rules."),
        ("Model", "The mathematical function that a machine learning algorithm has 'learned' from training data to make predictions."),
        ("Normalisation / Scaling", "Rescaling features to have similar ranges so no single feature dominates the model due to its large numerical value."),
        ("Pydantic", "A Python library for data validation. Ensures all input data follows the expected types and value ranges."),
        ("Random Forest", "An ensemble method that builds many decision trees on random subsets of data and takes a majority vote."),
        ("ROC-AUC", "Receiver Operating Characteristic — Area Under Curve. A metric from 0.5 (random) to 1.0 (perfect) measuring classification quality."),
        ("SQLite", "A lightweight, file-based database system built into Python. No separate database server needed."),
        ("StandardScaler", "A scikit-learn tool that scales each feature to have mean=0 and standard deviation=1."),
        ("SVM (Support Vector Machine)", "An algorithm that finds the best boundary line (or hyperplane) to separate two classes of data."),
        ("Train/Test Split", "Dividing the dataset: ~80% to teach the model (training), ~20% to test it on unseen data (testing)."),
        ("XGBoost", "Extreme Gradient Boosting — a fast, regularised implementation of gradient boosting, extremely popular in competitions."),
    ]

    g_data = [["Term", "Plain English Definition"]]
    for term, defn in terms:
        g_data.append([term, defn])

    g_tbl = Table(g_data, colWidths=[115, 348])
    g_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), C_GRAY_800),
        ("TEXTCOLOR",     (0,0),(-1,0), white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, C_GRAY_50]),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("FONTNAME",      (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,1),(-1,-1), "Helvetica"),
        ("GRID",          (0,0),(-1,-1), 0.3, C_GRAY_200),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("TEXTCOLOR",     (0,1),(0,-1), C_BLUE),
        ("TEXTCOLOR",     (1,1),(1,-1), C_GRAY_700),
    ]))
    e.append(g_tbl)
    e.append(space(8))
    return e

# ─────────────────────────────────────────────
#  PAGE HEADER / FOOTER CANVAS
# ─────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Header bar
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, h - 1.6*cm, w, 1.6*cm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(LEFT_M, h - 1.0*cm, "AI Diabetes Risk Prediction System — Project Documentation")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - RIGHT_M, h - 1.0*cm, "Kavya | 2024")

    # Footer bar
    canvas.setFillColor(C_GRAY_100)
    canvas.rect(0, 0, w, 1.4*cm, fill=1, stroke=0)
    canvas.setFillColor(C_GRAY_600)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(LEFT_M, 0.6*cm,
        "⚕  For educational purposes only. Not a substitute for professional medical advice.")
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(C_BLUE)
    canvas.drawRightString(w - RIGHT_M, 0.6*cm, f"Page {doc.page}")

    canvas.restoreState()

# ─────────────────────────────────────────────
#  MAIN – BUILD THE PDF
# ─────────────────────────────────────────────
def build_pdf():
    output_path = r"d:\Kavya\New folder\AI_Diabetes_Prediction_Project_Report.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_M,
        rightMargin=RIGHT_M,
        topMargin=TOP_M + 0.8*cm,   # extra for header bar
        bottomMargin=BOT_M + 0.2*cm,
        title="AI Diabetes Risk Prediction System — Project Report",
        author="Kavya",
        subject="Beginner-Friendly ML Project Documentation",
    )

    story = []

    # Cover page (no header/footer)
    story += cover_page()

    # All sections
    story += section_intro()
    story.append(PageBreak())
    story += section_problem()
    story.append(PageBreak())
    story += section_dataset()
    story.append(PageBreak())
    story += section_libraries()
    story.append(PageBreak())
    story += section_structure()
    story.append(PageBreak())
    story += section_flow()
    story.append(PageBreak())
    story += section_code()
    story.append(PageBreak())
    story += section_performance()
    story.append(PageBreak())
    story += section_api()
    story.append(PageBreak())
    story += section_howto()
    story.append(PageBreak())
    story += section_plots()
    story.append(PageBreak())
    story += section_glossary()

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"\nPDF generated successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    build_pdf()
