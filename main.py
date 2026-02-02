"""FastAPI Sudoku game server."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, List, Literal
from uuid import uuid4
from sudoku_engine import SudokuBoard
import os

app = FastAPI(title="Sudoku Game API", version="1.0.0")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for active games
games: Dict[str, SudokuBoard] = {}


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
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/sudoku", response_class=HTMLResponse)
async def sudoku(request: Request):
    """Sudoku page endpoint serving the Sudoku game interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/tictactoe", response_class=HTMLResponse)
async def tictactoe(request: Request):
    """Tic-Tac-Toe page endpoint."""
    return templates.TemplateResponse("tictactoe.html", {"request": request})


@app.get("/dots-and-boxes", response_class=HTMLResponse)
async def dots_and_boxes(request: Request):
    """Dots and Boxes page endpoint."""
    return templates.TemplateResponse("dots_and_boxes.html", {"request": request})


@app.get("/minesweeper", response_class=HTMLResponse)
async def minesweeper(request: Request):
    """Minesweeper page endpoint."""
    return templates.TemplateResponse("minesweeper.html", {"request": request})


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

