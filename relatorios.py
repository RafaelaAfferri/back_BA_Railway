import pdfkit
from jinja2 import Environment, FileSystemLoader
import os

def generate_pdf(context, template_path, css_path, output_path):
    template_dir = os.path.dirname(os.path.abspath(template_path))
    template_file = os.path.basename(template_path)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    context['logo_path'] = os.path.abspath(context['logo_path'])
    html_out = template.render(context)
    css_abs_path = os.path.abspath(css_path)
    
    pdfkit.from_string(html_out, output_path, options={"enable-local-file-access": ""}, css=css_abs_path)


context = {
    "dre": "DRE - IP",
    "unidade_escolar": "00971 - EMEF LUIZ GONZAGA DO NASCIMENTO JR. - GONZAGUINHA",
    "endereco": "DAS LÁGRIMAS, 1029 - IPIRANGA",
    "contato": "(80) 1 22-7316",
    "turma": "EF - 9D",
    "estudante": "HALLEY HENRIQUE COSTA BARROS (5596013)",
    "rf": "7938985",
    "usuario": "LETICIA DE ASSIS LOBATO",
    "data": "22/05/2024",
    "data_ocorrencia": "22/05/2024",
    "tipo_ocorrencia": "Atendimento aos Pais/Responsáveis",
    "titulo_ocorrencia": "Frequencia escolar",
    "descricao": ("Nesta data, o responsável pelo estudante compareceu à escola para tomar ciência das faltas referentes ao "
                 "primeiro bimestre. Foi orientado quanto: reprovação, encaminhamento ao conselho tutelar em caso de "
                 "reincidência de falta, realização de tarefas de compensação ausências aos todos os feriados decorrentes "
                 "das ausências. Foram notados que o aluno é encaminhado para vir à escola, mas ele, muitas vezes, não vem "
                 "Comprometeu-se a zelar pela frequência do estudante e manter o diálogo com a escola."),
    "assinatura_responsavel": "Antonia C. A. Costa",
    "data_assinatura": "Data assinatura",
    "logo_path": "logo.png"
}


template_path = os.path.abspath('template.html')
css_path = os.path.abspath('template.css')
output_pdf_path = os.path.abspath('ocorrencia_escolar.pdf')

generate_pdf(context, template_path, css_path, output_pdf_path)