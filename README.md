# PDF to structured JSON

## Description

This repository provides an API for converting PDF documents into structured JSON data. The API is build using FastAPI web framework for building APIs with Python. The conversion process utilizes industry-standard libraries for PDF parsing and JSON serialization, ensuring accurate extraction of content from PDF files.

## Features

* PDF to JSON conversion
* File upload functionality
* Displaying structured JSON output

## Technologies Used

* backend language - Python,
* backend framework - FastAPI,
* frontend - HTML, CSS, JavaScript,
* Docker

## Setup Instructions


1. Clone the repository

```bash
git clone https://github.com/justkr/pdf_to_structured_json.git
```

2. Build and run the Docker container

```bash
docker build -t pdf_reader_api .
docker run -p 8000:80 pdf_reader_api
```

3. Access the API at
```bash
http://localhost:8000
```
Press CTRL+C to quit API

## API Documentation

### Introduction

This FastAPI-based API provides functionality for uploading PDF files and extracting structured text for them.

### Endpoints

1. 
    * **Method:** 'POST'
    * **Endpoint:** '/'
    * **Description:** Upload a PDF file for text extraction

</br>

2. 
    * **Method:** 'GET'
    * **Endpoint:** '/'
    * **Description:** Display extracted text from PDF in structured JSON form