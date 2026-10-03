# ZeroTrust AI – ZT Code Base

Backend codebase for the ZeroTrust AI project.

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- Git
- pip

Check installation:

```bash
python --version
pip --version
git --version
```

## 1. Clone the Repository

```bash
git clone https://github.com/Meenakshi-1306/ZT-Code-base.git
```

Move into the project:

```bash
cd ZT-Code-base
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.\.venv\Scripts\activate
```

After activation, the terminal should look similar to:

```text
(.venv) PS C:\...\ZT-Code-base>
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Environment Variables

If the project requires environment variables, create a `.env` file in the project root.

Example:

```env
DATABASE_URL=your_database_url
API_KEY=your_api_key
```

Do not commit the `.env` file to GitHub.

## 5. Start the Backend

If the FastAPI application is defined as `app` inside `main.py`, run:

```bash
uvicorn main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Quick Start

For Windows:

```bash
git clone https://github.com/Meenakshi-1306/ZT-Code-base.git
cd ZT-Code-base
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Pull Latest Changes

Before starting new work:

```bash
git pull origin main
```

## Push Your Changes

```bash
git add .
git commit -m "Describe your changes"
git push origin main
```

## Deactivate Virtual Environment

When finished:

```bash
deactivate
```

## Project

**ZeroTrust AI – Zero Trust Access Monitoring & Analytics System**
