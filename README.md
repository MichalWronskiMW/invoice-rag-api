# Invoice RAG API

## Opis projektu

Invoice RAG API to aplikacja oparta o FastAPI umożliwiająca automatyczne przetwarzanie faktur i innych dokumentów graficznych.

System realizuje pełny pipeline:

1. przesłanie obrazu dokumentu,
2. wykonanie OCR,
3. zapisanie odczytanego tekstu,
4. budowę indeksu semantycznego,
5. wyszukiwanie fragmentów dokumentów,
6. zadawanie pytań do dokumentów metodą RAG (Retrieval Augmented Generation),
7. generowanie odpowiedzi przy użyciu lokalnego modelu LLM uruchomionego przez Ollama.

Projekt został przygotowany jako implementacja systemu AI wykorzystującego OCR, embeddingi, bazę wektorową oraz lokalny model językowy.

---

# Architektura systemu

```
Użytkownik
     │
     ▼
 FastAPI
     │
     ├── Upload dokumentu
     │
     ├── OCR (Tesseract OCR)
     │
     ├── Storage (JSON)
     │
     ├── ChromaDB
     │       │
     │       ▼
     │   Embeddings
     │
     └── RAG
             │
             ▼
        Ollama + Mistral
             │
             ▼
        Odpowiedź
```

---

# Wykorzystane technologie

## Backend

* Python 3.11
* FastAPI
* Pydantic
* Uvicorn

## OCR

* Tesseract OCR
* pytesseract
* Pillow

## Embeddingi

* Sentence Transformers
* all-MiniLM-L6-v2

## Baza wektorowa

* ChromaDB

## LLM

* Ollama
* Mistral

## Konteneryzacja

* Docker
* Docker Compose

---

# Funkcjonalności

Aplikacja umożliwia:

* przesyłanie obrazów dokumentów,
* wykonywanie OCR,
* przechowywanie odczytanego tekstu,
* indeksowanie dokumentów,
* wyszukiwanie semantyczne,
* zadawanie pytań do dokumentów,
* zwracanie odpowiedzi wraz ze źródłami,
* uruchomienie w kontenerze Docker.

---

# Struktura projektu

```
invoice-rag-api/
│
├── app/
│   ├── main.py
│   ├── ocr.py
│   ├── rag.py
│   ├── storage.py
│   ├── schemas.py
│   └── config.py
│
├── data/
│   ├── uploads/
│   ├── processed/
│   ├── vector_store/
│   └── documents.json
│
├── scripts/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── README.md
```

---

# Endpointy API

## Upload dokumentu

```
POST /documents/upload
```

Przesyła plik graficzny do systemu.

Przykładowa odpowiedź:

```json
{
  "document_id": "123456",
  "status": "queued"
}
```

---

## Pobranie dokumentu

```
GET /documents/{document_id}
```

Zwraca status przetwarzania oraz odczytany tekst.

---

## Indeksowanie dokumentu

```
POST /documents/{document_id}/index
```

Tworzy embeddingi i zapisuje dokument w ChromaDB.

---

## Wyszukiwanie semantyczne

```
POST /rag/search
```

Przykładowe zapytanie:

```json
{
  "query": "Who is the seller?",
  "top_k": 3
}
```

---

## Odpowiadanie na pytania

```
POST /rag/answer
```

Przykładowe zapytanie:

```json
{
  "query": "Who is the seller?",
  "top_k": 3
}
```

Przykładowa odpowiedź:

```json
{
  "answer": "Johnson, Coleman and Mccarthy",
  "model": "mistral:latest",
  "sources": [...]
}
```

---

# Obsługa kodów HTTP

| Kod | Znaczenie                                |
| --- | ---------------------------------------- |
| 200 | Poprawne wykonanie operacji              |
| 202 | Dokument przyjęty do przetwarzania       |
| 400 | Niepoprawny plik                         |
| 404 | Nie znaleziono dokumentu                 |
| 409 | Dokument nie został jeszcze przetworzony |
| 422 | Niepoprawne dane wejściowe               |
| 500 | Błąd OCR lub LLM                         |

---

# Uruchomienie lokalne

## Utworzenie środowiska

```bash
python -m venv .venv
```

Aktywacja:

Windows:

```bash
.venv\Scripts\activate
```

Linux:

```bash
source .venv/bin/activate
```

---

## Instalacja zależności

```bash
pip install -r requirements.txt
```

---

## Uruchomienie aplikacji

```bash
uvicorn app.main:app --reload
```

Swagger:

```
http://localhost:8000/docs
```

---

# Ollama

Projekt wykorzystuje lokalny model językowy uruchamiany przez Ollama.

Lista modeli:

```bash
ollama list
```

Pobranie modelu:

```bash
ollama pull mistral
```

Domyślny model:

```text
mistral:latest
```

---

# Uruchomienie w Dockerze

## Budowanie obrazu

```bash
docker compose build
```

## Uruchomienie

```bash
docker compose up
```

Swagger:

```
http://localhost:8000/docs
```

---

# Dlaczego Ollama działa poza kontenerem?

Model Mistral zajmuje kilka gigabajtów i znacząco zwiększa rozmiar obrazu Docker.

Z tego powodu:

* aplikacja FastAPI działa w kontenerze,
* Ollama działa lokalnie na hoście,
* kontener komunikuje się z Ollama przez:

```
host.docker.internal:11434
```

Pozwala to zmniejszyć rozmiar obrazu i skrócić czas budowy.

---

# Dockerfile

Dockerfile jest plikiem definiującym sposób budowania obrazu Docker.

Określa:

* bazowy obraz,
* instalowane pakiety,
* kopiowane pliki,
* polecenie uruchamiające aplikację.

Przykład:

```dockerfile
FROM python:3.11-slim
```

---

# .dockerignore

Plik `.dockerignore` określa, które pliki nie powinny trafiać do obrazu Docker.

Przykładowo:

```text
.venv
.git
__pycache__
```

Dzięki temu:

* obraz jest mniejszy,
* budowa jest szybsza,
* nie kopiujemy niepotrzebnych danych.

---

# Docker Context

Docker Context to zestaw plików wysyłanych do procesu budowania obrazu.

Polecenie:

```bash
docker build .
```

wysyła cały aktualny katalog jako context.

Im mniejszy context:

* szybszy build,
* mniejsze zużycie pamięci.

---

# Warstwy obrazu Docker

Każda instrukcja Dockerfile tworzy osobną warstwę.

Przykład:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
```

tworzy trzy warstwy.

Docker wykorzystuje cache warstw, dzięki czemu kolejne buildy są szybsze.

---

# Znaczenie kolejności instrukcji

Kolejność instrukcji wpływa na czas budowy.

Dobra praktyka:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
```

Zmiana kodu aplikacji nie powoduje ponownej instalacji wszystkich bibliotek.

Przyspiesza to kolejne buildy.

---

# Możliwe kierunki rozwoju

* obsługa PDF,
* ekstrakcja danych strukturalnych do JSON,
* obsługa wielu języków OCR,
* wykorzystanie modeli VLM (Donut, Qwen-VL, LLaVA),
* autoryzacja użytkowników,
* integracja z bazą PostgreSQL,
* asynchroniczne przetwarzanie dokumentów.

---

# Autor

Michał Wroński

SGGW – Implementacja Systemów AI

2026
