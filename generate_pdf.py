import markdown
from xhtml2pdf import pisa
import os

md_path = r"C:\Users\Hi\.gemini\antigravity\brain\210ee057-f08e-4e4e-b0a3-37558bc7e82b\quotation_plan.md"
pdf_path = r"C:\Users\Hi\.gemini\antigravity\brain\210ee057-f08e-4e4e-b0a3-37558bc7e82b\Mitara_AI_Quotation.pdf"

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Convert markdown to html
html_content = markdown.markdown(text, extensions=['tables'])

# Wrap in basic HTML structure with styles for the PDF
html = f"""
<html>
<head>
<style>
    @page {{
        size: a4 portrait;
        margin: 2cm;
    }}
    body {{ 
        font-family: Helvetica, Arial, sans-serif;
        font-size: 11pt;
        color: #333333;
        line-height: 1.5;
    }}
    h1 {{ color: #2c3e50; font-size: 20pt; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
    h2 {{ color: #2980b9; font-size: 16pt; margin-top: 20px; }}
    h3 {{ color: #34495e; font-size: 13pt; margin-top: 15px; }}
    table {{ 
        border-collapse: collapse; 
        width: 100%; 
        margin-top: 10px;
        margin-bottom: 20px;
    }}
    th, td {{ 
        border: 1px solid #bdc3c7; 
        padding: 10px; 
        text-align: left; 
    }}
    th {{ 
        background-color: #ecf0f1; 
        font-weight: bold;
    }}
    ul {{ margin-top: 5px; margin-bottom: 10px; }}
    li {{ margin-bottom: 5px; }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""

# Create the PDF
with open(pdf_path, "w+b") as result_file:
    pisa_status = pisa.CreatePDF(html, dest=result_file)

if pisa_status.err:
    print("Error generating PDF")
else:
    print("PDF successfully generated at:", pdf_path)
