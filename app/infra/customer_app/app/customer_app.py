import os
import json
import yaml
from typing import Annotated
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from asyncio import sleep
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")

@app.get(f"/customer/{os.getenv('CUSTOMER_URL')}")
async def create_form(request: Request):
    return templates.TemplateResponse("landing.html", 
                                      {"request": request,
                                       "name": os.getenv("CUSTOMER_NAME"),
                                       "motto": os.getenv("CUSTOMER_MOTTO")})