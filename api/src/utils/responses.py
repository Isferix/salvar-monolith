from typing import Optional

from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse

from ..dependencies import templates


def custom_response(status: int, data: Optional[dict] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "ok": True,
            "data": data,
        },
    )


def renderBase(request: Request) -> HTMLResponse:
    html_content = templates.TemplateResponse(
        request=request, name="base.html", context={"request": request}
    ).body.decode("utf-8")  # type: ignore
    return HTMLResponse(content=html_content)


def render(
    request: Request,
    template: str = "index",
    partial: bool = False,
    data: dict = {},
    **kwargs,
) -> HTMLResponse:
    isHx: str | None = request.headers.get("HX-Request")
    context = {**data, **kwargs}
    if isHx or partial:
        html_content = templates.TemplateResponse(
            request=request, name=f"{template}.html", context=context
        ).body.decode("utf-8")  # type: ignore
    else:
        page = f"{template}.html"
        html_content = templates.TemplateResponse(
            request=request,
            name="base.html",
            context={**context, "page": page},
        ).body.decode("utf-8")  # type: ignore
    return HTMLResponse(content=html_content)
