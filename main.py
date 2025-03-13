from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.constants import projects
import os 
import markdown

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="./templates")

BLOGS_DIR = "./blogs"

def load_blogs():
    blogs = []
    if os.path.exists(BLOGS_DIR):
        for idx, filename in enumerate(sorted(os.listdir(BLOGS_DIR))):
            if filename.endswith(".md"):
                with open(os.path.join(BLOGS_DIR, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract the title from the first line (assuming it's a markdown heading)
                    title = content.split("\n")[0].strip("# ").strip()
                    blogs.append({"id": idx + 1, "title": title, "filename": filename})
    return blogs

# Global list of blogs
blogs = load_blogs()

@app.get("/")
async def read_root(request: Request): 
    return templates.TemplateResponse("index.html", {"request": request, "projects": projects, "blogs": blogs})

@app.get('/project/{project_id}')
def project_detail(request: Request, project_id: int):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project:
        return templates.TemplateResponse("project.html", {"request": request, "project": project})
    return "Project not found", 404

@app.get("/blog/{blog_id}")
def blog_detail(request: Request, blog_id: int):
    # Find the blog by ID
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        return "Blog not found", 404

    # Read and parse the markdown file
    with open(os.path.join(BLOGS_DIR, blog["filename"]), "r", encoding="utf-8") as f:
        markdown_content = f.read()
        html_content = markdown.markdown(markdown_content)

    # Render the blog template
    return templates.TemplateResponse(
        "blog.html", {"request": request, "blog": blog, "content": html_content}
    )

