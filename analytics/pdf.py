from xhtml2pdf import pisa
from django.template.loader import render_to_string
from io import BytesIO

def generate_pdf(context):
    html_string = render_to_string('core/pdf_template.html', context)
    
    result = BytesIO()
    
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None