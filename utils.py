import pdfkit
from jinja2 import Environment, FileSystemLoader
import os


def generate_pdf(context, output_path):
    template_dir = os.path.dirname(os.path.abspath('./template/template.html'))
    template_file = os.path.basename('./template.html')
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    html_out = template.render(context)
    css_abs_path = os.path.abspath('./template/template.css')
    PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/app/bin/wkhtmltopdf')
    # PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")

    
    pdfkit.from_string(html_out, output_path, options={"enable-local-file-access": ""}, css=css_abs_path, configuration=PDFKIT_CONFIG)