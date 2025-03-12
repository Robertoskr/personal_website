from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.constants import projects

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="./templates")




@app.get("/")
async def read_root(request: Request): 
    return templates.TemplateResponse("index.html", {"request": request, "projects": projects})

@app.get('/project/{project_id}')
def project_detail(request: Request, project_id: int):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project:
        return templates.TemplateResponse("project.html", {"request": request, "project": project})
    return "Project not found", 404


