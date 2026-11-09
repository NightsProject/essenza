# app/routers/pages.py — Jinja2 page routes

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


@router.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse(request, "index.html", {})


@router.get("/methodology", response_class=HTMLResponse, name="methodology")
async def methodology(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse(request, "methodology.html", {})


@router.get("/about", response_class=HTMLResponse, name="about")
async def about(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse(request, "about.html", {})