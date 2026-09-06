import markdown
from xhtml2pdf import pisa
import os

md_path = r"C:\Users\Hi\.gemini\antigravity\brain\210ee057-f08e-4e4e-b0a3-37558bc7e82b\rag_presentation.md"
pdf_path = r"C:\Users\Hi\.gemini\antigravity\brain\210ee057-f08e-4e4e-b0a3-37558bc7e82b\Mitara_RAG_Architecture.pdf"

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

html_content = markdown.markdown(text, extensions=['tables'])

html = f"""
<html>
<head>
<style>
    @page {{
        size: a4 landscape;
        margin: 2cm;
    }}
    body {{ 
        font-family: Helvetica, Arial, sans-serif;
        font-size: 14pt;
        color: #1e293b;
        line-height: 1.6;
        background-color: #f8fafc;
    }}
    h1 {{ color: #0f172a; font-size: 26pt; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; margin-bottom: 5px; }}
    h2 {{ color: #3b82f6; font-size: 18pt; margin-top: 0px; margin-bottom: 25px; font-weight: normal; }}
    h3 {{ color: #1e293b; font-size: 16pt; margin-top: 25px; }}
    p {{ margin-bottom: 15px; }}
    ul {{ margin-top: 10px; margin-bottom: 15px; }}
    li {{ margin-bottom: 8px; }}
    strong {{ color: #0f172a; }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""

with open(pdf_path, "w+b") as result_file:
    pisa_status = pisa.CreatePDF(html, dest=result_file)

if pisa_status.err:
    print("Error generating PDF")
else:
    print("PDF successfully generated at:", pdf_path)
