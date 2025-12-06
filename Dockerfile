# 1. Lekki bazowy obraz Pythona
FROM python:3.12-slim

# 2. Środowisko – brak .pyc, logi na stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. (Opcjonalnie) zależności systemowe – przydatne, jeśli używasz np. orjson, psycopg2 itp.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# 4. Katalog roboczy
WORKDIR /app

# 5. Kopiujemy tylko requirements, żeby mieć lepszy cache warstw
COPY requirements.txt .

# 6. Instalacja zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# 7. Kopiujemy resztę kodu aplikacji
COPY . .

# 8. (Opcjonalnie) użytkownik nie-root
# RUN useradd -m appuser
# USER appuser

# 9. Port – Railway ustawia PORT w env, ale dobrze mieć default
ENV PORT=8000

# 10. Komenda startowa – FastAPI przez Uvicorn
# Aplikacja jest w app.py z obiektem `app = FastAPI()`
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
