import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.core.config import settings
from src.core.database import create_tables
from src.core.seed import seed_initial_data
from src.api.v1 import api_v1_router
from src.bot.bot_instance import get_bot, dp

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

bot_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    global bot_task
    logger.info("Initializing database tables and seed catalog...")
    await seed_initial_data()

    bot = get_bot()
    if bot:
        logger.info("Starting Telegram Bot long-polling in background...")
        # Start bot polling as an asynchronous background task in the current event loop
        bot_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    else:
        logger.warning(
            "⚠️ Telegram BOT_TOKEN is not configured or is default. "
            "Bot polling skipped. Admin Web Panel is running normally at http://localhost:8000"
        )

    yield

    # Shutdown
    if bot_task:
        logger.info("Stopping Telegram Bot polling...")
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass

    if bot:
        logger.info("Closing Telegram Bot session...")
        await bot.session.close()


app = FastAPI(
    title="UNIVERSITET IQTIDORLI TALABALAR TIZIMI",
    description="Iqtidorli talabalarni to'garaklarga jalb qilish va ro'yxatga olish tizimi",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "web", "static")
templates_dir = os.path.join(base_dir, "web", "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Register REST API v1
app.include_router(api_v1_router)


# Frontend Web Routes
@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/admin")


@app.get("/login", response_class=HTMLResponse)
async def render_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/admin", response_class=HTMLResponse)
async def render_admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="index.html")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
