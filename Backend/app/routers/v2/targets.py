from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.schemas.schemas import SiteIn, SiteOut, DBCredIn, DBCredOut
from app.models.models import WebTarget, DBCredential

router = APIRouter()

@router.post("/tech/auto/web/targets", response_model=SiteOut)
def create_site(payload: SiteIn, db: Session = Depends(get_db)):
    site_id = str(uuid4())
    db.add(WebTarget(site_id=site_id, url=str(payload.url)))
    db.commit()
    return SiteOut(site_id=site_id)

@router.post("/tech/auto/db/credentials", response_model=DBCredOut)
def create_db_cred(payload: DBCredIn, db: Session = Depends(get_db)):
    cred_id = str(uuid4())
    db.add(DBCredential(
        cred_id=cred_id,
        db_type=payload.db_type.value,
        host=payload.host,
        port=payload.port,
        database=payload.database,
        username=payload.username,
        password=payload.password.get_secret_value(),
    ))
    db.commit()
    return DBCredOut(cred_id=cred_id)