from fastapi import FastAPI, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import certifi
import datetime
import pytz
from bson.objectid import ObjectId
import os

app = FastAPI()

templates = Jinja2Templates(directory='templates')

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')

client = MongoClient(f'mongodb+srv://{db_user}:{db_pass}@jobbl.0rotaoy.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.lecords
records = db.records

levels = {
    '1': 'Internal Listening',
    '2': 'Focused Listening',
    '3': 'Global Listening'
}

@app.get('/')
async def root(request: Request):
    #Get all records for History
    recs = list(records.find())
    recs_sorted = sorted(recs, key=lambda obj: datetime.datetime.fromisoformat(obj["date"]), reverse=True)
    #Get record if any record for today already exists
    today = datetime.datetime.now()
    today_rec = records.find_one({"date": {"$eq": str(today.date())}})

    return templates.TemplateResponse('index.html', {'request': request, 'records': recs_sorted if len(recs) != 0 else None, 'today': today_rec})

@app.post('/record')
async def add_record(request: Request, level: str = Form(default='level')):
    #If level not selected, do nothing
    if level == '0':
        return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)

    #Add level to the DB with date
    my_date = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    records.insert_one({'level': levels[level], 'date': str(my_date.date())})

    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)

@app.post('/{id}')
async def remove_record(request: Request, id: str):

    #Remove the record with given id
    if records.count_documents({'_id': ObjectId(id)}) != 0:
        records.delete_one({'_id': ObjectId(id)})
        
    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)