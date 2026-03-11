from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATA_DIR / "ispring.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"