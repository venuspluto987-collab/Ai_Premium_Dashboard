from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
import pandas as pd

def generate_ai_insight(total_sales, profit_margin, top_region):
    insight = f"Top region: {top_region}. "
    if profit_margin < 20:
        insight += "Profit margin is low. Reduce expenses."
    else:
        insight += "Profit margin healthy. Business performing well."
    return insight

def generate_pdf(df, filename="report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Business Report Summary", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Total Records: {len(df)}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    doc.build(elements)
    return filename