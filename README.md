# Sudoku FastAPI Server

A FastAPI-based server for playing Sudoku with automatic puzzle generation and solving.

## Features

- Generate Sudoku puzzles with three difficulty levels (easy, medium, hard)
- Make moves and validate solutions
- Get hints by revealing the solution
- RESTful API for easy integration
- Interactive web UI with timer and leaderboard

## Prerequisites

Install [uv](https://github.com/astral-sh/uv) - a fast Python package installer:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## Installation

```bash
uv sync
```

## Running the Server

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

## Playing the Game

Simply open your browser to `http://localhost:8000` and enjoy the interactive Sudoku game with:
- Three difficulty levels
- Timer that starts on first move
- Local leaderboard to track your best times
- Visual separation of 3×3 boxes

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Create a New Game
```bash
POST /games/new
Body: {"difficulty": "easy|medium|hard"}
```

### Get Game State
```bash
GET /games/{game_id}
```

### Make a Move
```bash
POST /games/{game_id}/move
Body: {"row": 0-8, "col": 0-8, "num": 1-9 or 0 to clear}
```

### Get Solution
```bash
GET /games/{game_id}/solution
```

### Validate Solution
```bash
GET /games/{game_id}/validate
```

### Delete Game
```bash
DELETE /games/{game_id}
```

### List All Games
```bash
GET /games
```

## Example Usage

```bash
# Create a new game
curl -X POST "http://localhost:8000/games/new" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "medium"}'

# Make a move (example game_id)
curl -X POST "http://localhost:8000/games/{game_id}/move" \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 0, "num": 5}'

# Get current state
curl "http://localhost:8000/games/{game_id}"
```
