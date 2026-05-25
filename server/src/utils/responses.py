from typing import Any, Optional

from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse

from dependencies import templates


def custom_response(status: int, data: Optional[dict] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "ok": True,
            "data": data,
        },
    )


def renderBase(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="src/base.html", context={"request": request}
    )


def renderTemplate(
    request: Request,
    template: str = "index",
    partial: bool = False,
    data: dict[str, Any] | None = None,
) -> HTMLResponse:
    isHx: str | None = request.headers.get("HX-Request")

    context = {
        "request": request,
        **(data or {}),
    }

    if isHx or partial:
        response = templates.TemplateResponse(
            request=request, name=f"{template}.html", context=context
        )
    else:
        context["page"] = f"{template}.html"

        response = templates.TemplateResponse(
            request=request, name="src/base.html", context=context
        )

    return HTMLResponse(content=response.body, status_code=response.status_code)
