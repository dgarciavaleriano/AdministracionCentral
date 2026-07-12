import uvicorn
from dotenv import load_dotenv
import os
from config.logger import Logger

load_dotenv()

logger = Logger.get_logger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting server on {os.getenv('HOST')}:{os.getenv('PORT')}")
    uvicorn.run("app:app", host=os.getenv("HOST"), port=int(os.getenv("PORT")))