from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db, Base
from ussd_handler import handle_ussd
import models  # noqa: F401 — registers models with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="SafeAlert USSD", lifespan=lifespan)


@app.post("/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
    db: AsyncSession = Depends(get_db),
) -> str:
    return await handle_ussd(
        session_id=sessionId,
        phone_number=phoneNumber,
        text=text,
        db=db,
    )
