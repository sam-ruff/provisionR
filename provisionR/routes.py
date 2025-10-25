"""API routes for provisionR."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import PlainTextResponse, StreamingResponse
from jinja2 import TemplateNotFound
from sqlalchemy.orm import Session

from provisionR.models import GlobalConfig
from provisionR.config import get_global_config_from_db, update_global_config_in_db
from provisionR.database import get_db
from provisionR.services import KickstartService, ExportService

api_router = APIRouter()


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
