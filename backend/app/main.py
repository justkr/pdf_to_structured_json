from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import json

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

app = FastAPI()

templates = Jinja2Templates(directory = './frontend/templates')
app.mount('/static', StaticFiles(directory = './frontend/static'), name = 'static')

@app.get('/')
def hello(request: Request, pdf_path : str = './data/Insurance_Handbook.pdf'):

    pages = extract_pages(pdf_path)
    page = next(pages)

    texts = []
    for element in page:
        if isinstance(element, LTTextContainer):
            texts.append(element.get_text())

    return templates.TemplateResponse('index.html', {'request' : request, 'pdf_jsoned' : texts})
