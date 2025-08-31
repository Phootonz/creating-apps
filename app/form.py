import os
import json
from typing import Annotated
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from kubernetes import client, config
from asyncio import sleep
from .models.forms import CreateApp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FAK = os.getenv("FORM_APP_KEY")

templates = Jinja2Templates(directory="templates")


async def require_form_passkey(create_app: CreateApp ):
    if not FAK or create_app.key != FAK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return True


@app.get("/")
async def create_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def create_submit(request: Request, create_app: CreateApp = Form(...)):
    await require_form_passkey(create_app)
    return templates.TemplateResponse(
        "subbed_form.html", 
        context={"request": request, "name": create_app.name}
    )


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

async def waypoints_generator():
    waypoints = open('waypoints.json')
    waypoints = json.load(waypoints)
    for waypoint in waypoints[0: 10]:
        data = json.dumps(waypoint)
        yield f"data: {data}\n\n"
        await sleep(1)

@app.get("/get-waypoints")
async def root():
    return StreamingResponse(waypoints_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('static/favicon.ico')