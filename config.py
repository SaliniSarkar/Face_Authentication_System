from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "face_auth.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Lower tolerance = stricter matching.
# 0.5 is a reasonable starting point; tune with real-world testing.
FACE_MATCH_TOLERANCE = 0.5
FACE_ENCODING_SIZE = 128
