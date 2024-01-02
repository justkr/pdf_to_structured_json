from fastapi import FastAPI, Request, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

import json

from backend.app.functions import pdf_to_structured_json

# Create a FastAPI app instance
app = FastAPI()

# Configure Jinja2Templates to use templates from the 'frontend/templates' directory
templates = Jinja2Templates(directory = './frontend/templates')
# Mount the '/static' route to serve static files from the 'frontend/static' directory
app.mount('/static', StaticFiles(directory = './frontend/static'), name = 'static')

# Define a route to handle file uploads via HTTP POST requests

@app.post('/')
async def upload_file(request: Request, pdf_name: UploadFile):

    # Read the content of the uploaded PDF file
    data = await pdf_name.read()

    # Save the PDF file to the specified upload directory
    with open(f"data/input/{pdf_name.filename}", 'wb') as f:
        f.write(data)

    # Convert the PDF file to structured JSON using the custom function
    list_of_pargraphs = pdf_to_structured_json('data/input', pdf_name.filename)

    # Save the structured JSON to an output file
    with open(f"data/output/{pdf_name.filename.split('.pdf')[0]}.json", 'w') as f:
        json.dump(list_of_pargraphs, f)

    # Convert the structured JSON to a JSON-formatted string
    list_of_pargraphs_jsoned = json.dumps(list_of_pargraphs)

    # Render the 'result.html' template with relevant data
    return templates.TemplateResponse("result.html", {'request' : request, 'filename': pdf_name.filename, 'pdf_jsoned' : list_of_pargraphs_jsoned})

# Define a route to handle HTTP GET requests, rendering the 'index.html' template
@app.get("/", response_class=HTMLResponse)
async def read_upload(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

