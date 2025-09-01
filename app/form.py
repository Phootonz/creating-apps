import os
import json
import yaml
import logging
from typing import Annotated
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from kubernetes import client, config
from asyncio import sleep
from github import Github
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from .models.forms import CreateApp, Status
from .models.db import Base, Customer
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_PAT")
REPO_OWNER = "Phootonz"
REPO_NAME = "creating-apps"
TEMPLATE_FILE_NAME = "create-customer-template.md" 

FAK = os.getenv("FORM_APP_KEY")
NURL = os.getenv("NGROK_URL")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./sql.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def require_form_passkey(mode_with_key):
    if not FAK or mode_with_key.key != FAK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return True

def github_webhook(create_app: CreateApp):
    body = {
        "url": NURL,
        "name": create_app.name,
        "motto": create_app.motto
    }
    
    body = yaml.safe_dump(body)
    g = Github(GITHUB_TOKEN)
    repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
    title = f"Creating an instance for {create_app.name}" # Default title
    try:
        issue = repo.create_issue(
            title=title,
            body=body, 
            labels=["create-customer"]
        )
    except Exception:
        print(f"Failed to create issue {body}")
        return False
    print(f"Successfully created issue: {issue.html_url}")
    return True


@app.get("/")
async def create_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def create_submit(request: Request, create_app: CreateApp = Form(...)):
    await require_form_passkey(create_app)

    if not github_webhook(create_app):
        #return a failure response
        return
    return templates.TemplateResponse(
        "subbed_form.html", 
        context={"request": request, "name": create_app.name}
    )
    
@app.post("/deploy", response_class=JSONResponse)
async def create_deployment(request: Request, create_app: CreateApp, db: Session = Depends(get_db)):
    await require_form_passkey(create_app)
    customer = Customer(**create_app.model_dump(exclude=['key']))
    db.add(customer)
    try:
        db.commit()
    except Exception:
        return JSONResponse({"error": "Only a single customer with the same name can exist", "code": 1})
    db.refresh(customer)
    return JSONResponse(create_app.model_dump(exclude=['key']))

@app.post("/status", response_class=JSONResponse, status_code=status.HTTP_204_NO_CONTENT)
async def create_deployment(request: Request, state: Status, db: Session = Depends(get_db)):
    await require_form_passkey(state)
    customer = db.query(Customer).filter_by(name=state.name).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find that customer",
        )
        
    customer.status = state.status
    try:
        db.commit()
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unable to update the state",
        )
    db.refresh(customer)
    return JSONResponse(state.model_dump(exclude=['key']))

@app.post("/create", response_class=JSONResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(request: Request, create_app: CreateApp, db: Session = Depends(get_db)):
    await require_form_passkey(create_app)
    customer = Customer(name=create_app.name, motto=create_app.motto, status='db updated')
    db.add(customer)
    try:
        db.commit()
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some info was incorrect, maybe the customer already exists",
        )
    db.refresh(customer) 
    return JSONResponse(create_app.model_dump(exclude=['key'])), 201


@app.get("/instances")
async def instances():
    try:
        config.load_kube_config()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load kube config: {e}",
        )

    namespace = "funwithkubes"
    try:
        apps_v1 = client.AppsV1Api()
        deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
        dps = [
            {
                "Deployment Name": dp.metadata.name,
                "Replicas": dp.spec.replicas,
            }
            for dp in deployments.items
        ]
        return dps
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list deployments: {e}",
        )

async def deployment_status(name, db: Session):
    try:
        for _ in range(60):
                customer = db.query(Customer).filter_by(name=name).first()
                state = {"status": "initilizing"}
                if customer:
                    print(customer.status)
                    state["status"] = customer.status
                yield f"data: {json.dumps(state)}\n\n"
                if customer:
                    db.refresh(customer)
                await sleep(5)
    finally:
        db.close()


@app.get("/deployment/{name}")
async def deployment(name,  db: Session = Depends(get_db)):
    return StreamingResponse(deployment_status(name, db), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('static/favicon.ico')