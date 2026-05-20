from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from app.database import init_db, get_activities_today, get_emails_today
from app.sync import sync_all
from app.ai import answer_question

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup():
    init_db()
    scheduler.add_job(sync_all, "interval", hours=1, id="sync")
    scheduler.start()
    sync_all()


@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    activities = get_activities_today()
    emails = get_emails_today()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "activities": activities,
        "emails": emails,
    })


@app.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, question: str = Form(...)):
    activities = get_activities_today()
    emails = get_emails_today()
    answer = answer_question(question, activities, emails)
    return templates.TemplateResponse("query.html", {
        "request": request,
        "question": question,
        "answer": answer,
    })


@app.post("/sync")
async def manual_sync():
    sync_all()
    return {"status": "ok"}
