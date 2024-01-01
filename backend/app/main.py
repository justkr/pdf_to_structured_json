from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import json

from backend.app.functions import pdf_to_structured_json

app = FastAPI()

templates = Jinja2Templates(directory = './frontend/templates')
app.mount('/static', StaticFiles(directory = './frontend/static'), name = 'static')

@app.get('/')
def hello(request: Request, pdf_name : str = 'Factsheet Leben Risiko'):

    list_of_pargraphs = pdf_to_structured_json('./data/input', pdf_name)

    with open(f'data/output/{pdf_name}.json', 'w') as f:
        json.dump(list_of_pargraphs, f)

    return templates.TemplateResponse('index.html', {'request' : request, 'pdf_jsoned' : list_of_pargraphs})
