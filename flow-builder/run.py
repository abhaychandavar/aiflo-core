# run.py
import uvicorn
from app.config.default import Settings 

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=Settings.HOST, port=Settings.PORT, reload=True)