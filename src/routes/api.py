import structlog
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


log = structlog.get_logger()
router = APIRouter(prefix="/api")

BASE_DIR = os.path.dirname(__file__) 
TEMPLATES_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend", "static", "templates"))
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def page_home(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.get("/user", include_in_schema=False)
async def page_user(request: Request):
    return templates.TemplateResponse("admin/user.html", {"request": request})

@router.get("/admin", include_in_schema=False)
async def page_admin(request: Request):
    return templates.TemplateResponse("admin/admin.html", {"request": request})

@router.get("/lego/cpf", response_class=HTMLResponse, include_in_schema=False)
async def cpf(request: Request):
    return templates.TemplateResponse("lego/html/cpf.html", {"request": request})

@router.get("/lego/dados", response_class=HTMLResponse, include_in_schema=False)
async def dados(request: Request):
    return templates.TemplateResponse("lego/html/dados.html", {"request": request})

@router.get("/lego/resultado", response_class=HTMLResponse, include_in_schema=False)
async def resultado(request: Request, image_url: str = ""):
    return templates.TemplateResponse("lego/html/resultado.html", {"request": request, "image_url": image_url})

@router.get("/lego/termos", response_class=HTMLResponse, include_in_schema=False)
async def termos(request: Request):
    from core.config import settings
    return templates.TemplateResponse("lego/html/termos.html", {"request": request, "use_crm": settings.USE_CRM})

@router.get("/lego/continue", response_class=HTMLResponse, include_in_schema=False)
async def continue_page(request: Request):
    return templates.TemplateResponse("lego/html/continue.html", {"request": request})

@router.get("/lego/erro", response_class=HTMLResponse, include_in_schema=False)
async def erro(request: Request):
    return templates.TemplateResponse("lego/html/erro.html", {"request": request})