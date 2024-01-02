from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path

import json

from backend.app.functions import pdf_to_structured_json

app = FastAPI()

templates = Jinja2Templates(directory = './frontend/templates')
app.mount('/static', StaticFiles(directory = './frontend/static'), name = 'static')

UPLOAD_DIR = Path() / 'data/input'
@app.post('/')
async def upload_file(request: Request, pdf_name: UploadFile):


    data = await pdf_name.read()

    with open(f"data/input/{pdf_name.filename}", 'wb') as f:
        f.write(data)

    list_of_pargraphs = pdf_to_structured_json('./data/input', pdf_name.filename)

    with open(f"data/output/{pdf_name.filename.split('.pdf')[0]}.json", 'w') as f:
        json.dump(list_of_pargraphs, f)

    list_of_pargraphs_jsoned = json.dumps(list_of_pargraphs)

    return templates.TemplateResponse("result.html", {'request' : request, 'filename': pdf_name.filename, 'pdf_jsoned' : list_of_pargraphs_jsoned})


@app.get("/", response_class=HTMLResponse)
async def read_upload(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

