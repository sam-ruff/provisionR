"""API routes for provisionR."""

from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Depends,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import PlainTextResponse, StreamingResponse
from jinja2 import TemplateNotFound
from sqlalchemy.orm import Session

from provisionR.models import GlobalConfig
from provisionR.config import get_global_config_from_db, update_global_config_in_db
from provisionR.database import get_db
from provisionR.services import KickstartService, ExportService

api_router = APIRouter(tags=["provisionR API"])


@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "provisionR"}


@api_router.get("/v1/config", response_model=GlobalConfig)
async def get_config(db: Session = Depends(get_db)):
    """Get the current global configuration from the database."""
    return get_global_config_from_db(db)


@api_router.put("/v1/config", response_model=GlobalConfig)
async def update_config(new_config: GlobalConfig, db: Session = Depends(get_db)):
    """Update the global configuration in the database."""
    return update_global_config_in_db(db, new_config)


@api_router.get("/v1/machines/export")
async def export_machine_passwords(db: Session = Depends(get_db)):
    """Export all machine passwords as a CSV file."""
    export_service = ExportService(db)
    csv_content = export_service.export_machine_passwords_csv()

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=machine_passwords.csv"},
    )


@api_router.get("/v1/templates/{template_name}", response_class=PlainTextResponse)
async def get_template(template_name: str = "default"):
    """Get the content of a template file."""
    templates_dir = Path(__file__).parent / "templates"
    template_file = templates_dir / f"{template_name}.ks.j2"

    if not template_file.exists():
        raise HTTPException(
            status_code=404, detail=f"Template '{template_name}' not found"
        )

    try:
        return template_file.read_text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")


@api_router.post("/v1/templates")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    use_as_default: bool = Form(False),
):
    """Upload a new template file."""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    # Validate template name
    if not template_name or ".." in template_name or "/" in template_name:
        raise HTTPException(status_code=400, detail="Invalid template name")

    try:
        # Read the uploaded file content
        content = await file.read()
        content_str = content.decode("utf-8")

        # Save to the specified template name
        template_file = templates_dir / f"{template_name}.ks.j2"
        template_file.write_text(content_str)

        # If use_as_default, also save as default.ks.j2
        if use_as_default:
            default_file = templates_dir / "default.ks.j2"
            default_file.write_text(content_str)

        return {
            "message": "Template uploaded successfully",
            "template_name": template_name,
            "use_as_default": use_as_default,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading template: {str(e)}"
        )


@api_router.get("/v1/ks", response_class=PlainTextResponse)
async def generate_kickstart(
    request: Request,
    mac: Annotated[str, Query(description="MAC address of the machine")],
    uuid: Annotated[str, Query(description="UUID of the machine")],
    serial: Annotated[str, Query(description="Serial number of the machine")],
    template_name: Annotated[
        str, Query(description="Template name (without .ks.j2)")
    ] = "default",
    db: Session = Depends(get_db),
):
    """
    Generate a Kickstart file from the provided parameters.

    All query parameters beyond mac, uuid, serial, and template_name will be available
    in the template for rendering.

    If the machine (identified by mac+uuid+serial) has been seen before,
    previously generated passwords will be reused.
    """
    kickstart_service = KickstartService(db)

    try:
        rendered = kickstart_service.generate(
            mac=mac,
            uuid=uuid,
            serial=serial,
            template_name=template_name,
            query_params=dict(request.query_params),
        )
        return rendered
    except TemplateNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_name}' not found. Expected file: {template_name}.ks.j2",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering template: {str(e)}"
        )
