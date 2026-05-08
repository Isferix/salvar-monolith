from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from ..dependencies import get_templates

templates = get_templates()
web = APIRouter()

def render(request, template='index', data={},  **kwargs) -> HTMLResponse:
    isHx: str | None = request.headers.get("HX-Request")
    context = {**data, **kwargs}
    if isHx:
        html_content = templates.TemplateResponse(request=request, name=f'{template}.html', context=context).body.decode('utf-8') # type: ignore
    else:
        html_content = templates.TemplateResponse(request=request, name='base.html', context={**context, "page": f"{template}.html"}).body.decode('utf-8') # type: ignore
    return HTMLResponse(content=html_content)

@web.get("/")
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="base.html", context={"request": request})

@web.get("/index")
async def index(request: Request) -> HTMLResponse:
    return render(request, template="index")