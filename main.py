"""FastAPI Sudoku game server."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, List, Literal
from uuid import uuid4
from sudoku_engine import SudokuBoard
import os
import json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

app = FastAPI(title="Sudoku Game API", version="1.0.0")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for active games
games: Dict[str, SudokuBoard] = {}

# Load translations
SUPPORTED_LANGS = ['en', 'nl', 'it', 'pt', 'fa']
translations = {}


def load_translations() -> None:
    """Load translation files into memory."""
    global translations
    loaded = {}
    for lang in SUPPORTED_LANGS:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            loaded[lang] = json.load(f)
    translations = loaded


load_translations()

def get_translation(lang: str, key_path: str) -> str:
    """Get translation for a given language and key path."""
    keys = key_path.split('.')

    def resolve_key_path(root: dict, path_keys: List[str]):
        value = root
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
        return value if isinstance(value, str) else None

    current_lang_value = resolve_key_path(translations.get(lang, {}), keys)
    if current_lang_value is not None:
        return current_lang_value

    english_value = resolve_key_path(translations.get('en', {}), keys)
    if english_value is not None:
        return english_value

    # If key is missing, refresh translation cache in case files changed while server is running.
    try:
        load_translations()
    except Exception:
        return key_path

    current_lang_value = resolve_key_path(translations.get(lang, {}), keys)
    if current_lang_value is not None:
        return current_lang_value

    english_value = resolve_key_path(translations.get('en', {}), keys)
    if english_value is not None:
        return english_value

    return key_path

# Add translation function to Jinja2 globals
templates.env.globals['translate'] = get_translation

def get_current_lang(request: Request) -> str:
    """Get current language from query parameter, cookie, or default to English."""
    query_lang = request.query_params.get('lang')
    if query_lang in SUPPORTED_LANGS:
        return query_lang

    cookie_lang = request.cookies.get('lang', 'en')
    return cookie_lang if cookie_lang in SUPPORTED_LANGS else 'en'

@app.get("/set-lang/{lang}")
async def set_language(lang: str, request: Request):
    """Set language preference and redirect back."""
    if lang not in SUPPORTED_LANGS:
        lang = 'en'

    referer = request.headers.get('referer', '/')
    parsed = urlparse(referer)
    query_items = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query_items['lang'] = lang
    redirect_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path or '/',
        parsed.params,
        urlencode(query_items),
        parsed.fragment,
    ))

    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key='lang', value=lang, max_age=365*24*60*60, path='/')  # 1 year
    return response


class NewGameRequest(BaseModel):
    """Request model for creating a new game."""
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Difficulty level of the puzzle"
    )


class NewGameResponse(BaseModel):
    """Response model for new game creation."""
    game_id: str
    board: List[List[int]]
    difficulty: str
    message: str


class GameStateResponse(BaseModel):
    """Response model for game state."""
    game_id: str
    board: List[List[int]]
    is_complete: bool
    is_correct: bool


class MoveRequest(BaseModel):
    """Request model for making a move."""
    row: int = Field(..., ge=0, le=8, description="Row index (0-8)")
    col: int = Field(..., ge=0, le=8, description="Column index (0-8)")
    num: int = Field(..., ge=0, le=9, description="Number to place (1-9, or 0 to clear)")


class MoveResponse(BaseModel):
    """Response model for move result."""
    success: bool
    board: List[List[int]]
    is_complete: bool
    is_correct: bool
    message: str


class SolutionResponse(BaseModel):
    """Response model for solution."""
    game_id: str
    solution: List[List[int]]


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the game hub home page."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("home.html", {"request": request, "lang": lang})


@app.get("/sudoku", response_class=HTMLResponse)
async def sudoku(request: Request):
    """Sudoku page endpoint serving the Sudoku game interface."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("index.html", {"request": request, "lang": lang})


@app.get("/tictactoe", response_class=HTMLResponse)
async def tictactoe(request: Request):
    """Tic-Tac-Toe page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("tictactoe.html", {"request": request, "lang": lang})


@app.get("/towers-of-hanoi", response_class=HTMLResponse)
async def towers_of_hanoi(request: Request):
    """Towers of Hanoi page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("towers_of_hanoi.html", {"request": request, "lang": lang})


@app.get("/dots-and-boxes", response_class=HTMLResponse)
async def dots_and_boxes(request: Request):
    """Dots and Boxes page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("dots_and_boxes.html", {"request": request, "lang": lang})


@app.get("/minesweeper", response_class=HTMLResponse)
async def minesweeper(request: Request):
    """Minesweeper page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("minesweeper.html", {"request": request, "lang": lang})


@app.get("/chess", response_class=HTMLResponse)
async def chess(request: Request):
    """Chess page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("chess.html", {"request": request, "lang": lang})


@app.get("/connect-four", response_class=HTMLResponse)
async def connect_four(request: Request):
    """Connect Four page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("connect_four.html", {"request": request, "lang": lang})


@app.get("/kenken", response_class=HTMLResponse)
async def kenken(request: Request):
    """KenKen page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("kenken.html", {"request": request, "lang": lang})


@app.get("/solitaire", response_class=HTMLResponse)
async def solitaire(request: Request):
    """Solitaire (Peg Solitaire) page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("solitaire.html", {"request": request, "lang": lang})


@app.get("/gems", response_class=HTMLResponse)
async def gems(request: Request):
    """Gems (Match-3) page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("gems.html", {"request": request, "lang": lang})


@app.get("/api")
async def api_root():
    """API root endpoint with API information."""
    return {
        "message": "Sudoku Game API",
        "endpoints": {
            "POST /api/games/new": "Create a new game",
            "GET /api/games/{game_id}": "Get game state",
            "POST /api/games/{game_id}/move": "Make a move",
            "GET /api/games/{game_id}/solution": "Get the solution",
            "GET /api/games/{game_id}/validate": "Validate current solution",
            "DELETE /api/games/{game_id}": "Delete a game"
        }
    }


@app.post("/games/new", response_model=NewGameResponse)
async def create_game(request: NewGameRequest):
    """Create a new Sudoku game.
    
    Args:
        request: New game request with difficulty level
        
    Returns:
        Game ID and initial board state
    """
    game_id = str(uuid4())
    
    # Create new board
    board = SudokuBoard()
    board.generate_full_board()
    board.remove_numbers(request.difficulty)
    
    # Store the game
    games[game_id] = board
    
    return NewGameResponse(
        game_id=game_id,
        board=board.get_board(),
        difficulty=request.difficulty,
        message=f"New {request.difficulty} game created successfully"
    )


@app.get("/games/{game_id}", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    """Get the current state of a game.
    
    Args:
        game_id: Unique game identifier
        
    Returns:
        Current board state and completion status
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    board = games[game_id]
    
    return GameStateResponse(
        game_id=game_id,
        board=board.get_board(),
        is_complete=board.is_complete(),
        is_correct=board.is_correct() if board.is_complete() else False
    )


@app.post("/games/{game_id}/move", response_model=MoveResponse)
async def make_move(game_id: str, move: MoveRequest):
    """Make a move in the game.
    
    Args:
        game_id: Unique game identifier
        move: Move details (row, col, number)
        
    Returns:
        Move result and updated board state
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    board = games[game_id]
    
    # Attempt to place the number
    success = board.place_number(move.row, move.col, move.num)
    
    if not success:
        return MoveResponse(
            success=False,
            board=board.get_board(),
            is_complete=board.is_complete(),
            is_correct=False,
            message=f"Invalid move: cannot place {move.num} at ({move.row}, {move.col})"
        )
    
    is_complete = board.is_complete()
    is_correct = board.is_correct() if is_complete else False
    
    message = "Move successful"
    if is_complete:
        if is_correct:
            message = "Congratulations! You solved the puzzle correctly!"
        else:
            message = "Puzzle complete but solution is incorrect. Try again!"
    
    return MoveResponse(
        success=True,
        board=board.get_board(),
        is_complete=is_complete,
        is_correct=is_correct,
        message=message
    )


@app.get("/games/{game_id}/solution", response_model=SolutionResponse)
async def get_solution(game_id: str):
    """Get the solution for a game.
    
    Args:
        game_id: Unique game identifier
        
    Returns:
        The complete solution
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    board = games[game_id]
    
    return SolutionResponse(
        game_id=game_id,
        solution=board.get_solution()
    )


@app.get("/games/{game_id}/validate")
async def validate_solution(game_id: str):
    """Validate the current solution.
    
    Args:
        game_id: Unique game identifier
        
    Returns:
        Validation result
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    board = games[game_id]
    
    is_complete = board.is_complete()
    is_correct = board.is_correct() if is_complete else False
    
    if not is_complete:
        return {
            "valid": False,
            "complete": False,
            "message": "Puzzle is not yet complete"
        }
    
    if is_correct:
        return {
            "valid": True,
            "complete": True,
            "message": "Solution is correct!"
        }
    else:
        return {
            "valid": False,
            "complete": True,
            "message": "Solution is incorrect. Keep trying!"
        }


@app.delete("/games/{game_id}")
async def delete_game(game_id: str):
    """Delete a game.
    
    Args:
        game_id: Unique game identifier
        
    Returns:
        Deletion confirmation
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del games[game_id]
    
    return {"message": f"Game {game_id} deleted successfully"}


@app.get("/games")
async def list_games():
    """List all active games.
    
    Returns:
        List of active game IDs
    """
    return {
        "active_games": len(games),
        "game_ids": list(games.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

