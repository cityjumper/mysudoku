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

app = FastAPI(title="Sudoku Game API", version="1.0.0")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for active games
games: Dict[str, SudokuBoard] = {}

# Load translations
translations = {}
for lang in ['en', 'nl', 'it', 'pt', 'fa']:
    with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
        translations[lang] = json.load(f)

def get_translation(lang: str, key_path: str) -> str:
    """Get translation for a given language and key path."""
    keys = key_path.split('.')
    value = translations.get(lang, translations['en'])
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, {})
        else:
            # If we encounter a non-dict value before traversing all keys,
            # return the key_path as fallback
            return key_path
    return value if isinstance(value, str) else key_path

# Add translation function to Jinja2 globals
templates.env.globals['translate'] = get_translation

def get_current_lang(request: Request) -> str:
    """Get current language from cookie or default to English."""
    return request.cookies.get('lang', 'en')

@app.get("/set-lang/{lang}")
async def set_language(lang: str, request: Request):
    """Set language preference and redirect back."""
    if lang not in ['en', 'nl', 'it', 'pt', 'fa']:
        lang = 'en'
    response = RedirectResponse(url=request.headers.get('referer', '/'), status_code=302)
    response.set_cookie(key='lang', value=lang, max_age=365*24*60*60)  # 1 year
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


@app.get("/connect-four-3d", response_class=HTMLResponse)
async def connect_four_3d(request: Request):
    """3D Connect Four page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("connect_four_3d.html", {"request": request, "lang": lang})


@app.get("/tetris-3d", response_class=HTMLResponse)
async def tetris_3d(request: Request):
    """3D Tetris page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("tetris_3d.html", {"request": request, "lang": lang})


@app.get("/tictactoe-3d", response_class=HTMLResponse)
async def tictactoe_3d(request: Request):
    """3D Tic-Tac-Toe page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("tictactoe_3d.html", {"request": request, "lang": lang})


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


@app.get("/checkers", response_class=HTMLResponse)
async def checkers(request: Request):
    """Checkers page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("checkers.html", {"request": request, "lang": lang})


@app.get("/robot-runner", response_class=HTMLResponse)
async def robot_runner(request: Request):
    """Robot Runner page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("robot_runner.html", {"request": request, "lang": lang})


@app.get("/math-lanes", response_class=HTMLResponse)
async def math_lanes(request: Request):
    """Math Lanes page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("math_lanes.html", {"request": request, "lang": lang})


@app.get("/memory-match", response_class=HTMLResponse)
async def memory_match(request: Request):
    """Memory Match page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("memory_match.html", {"request": request, "lang": lang})


SNL_I18N_KEYS = [
    'setup_heading', 'setup_subheading', 'color_label', 'shape_label', 'player_placeholder',
    'start_game', 'players_heading', 'play_again', 'change_players', 'start_label', 'roll_dice',
    'turn_banner', 'msg_overshoot', 'msg_moved', 'msg_ladder', 'msg_snake', 'msg_extra_turn',
    'win_title', 'win_subtitle',
]


@app.get("/snakes-and-ladders", response_class=HTMLResponse)
async def snakes_and_ladders(request: Request):
    """Snakes and Ladders page endpoint."""
    lang = get_current_lang(request)
    snl_i18n = {key: get_translation(lang, f'games.snakes_and_ladders.{key}') for key in SNL_I18N_KEYS}
    return templates.TemplateResponse(
        "snakes_and_ladders.html",
        {"request": request, "lang": lang, "snl_i18n": snl_i18n},
    )


MASTERMIND_I18N_KEYS = [
    'ready', 'pick_colors', 'keep_guessing', 'win_title', 'win_message',
    'lose_title', 'lose_message', 'gave_up_title', 'no_best',
]


@app.get("/mastermind", response_class=HTMLResponse)
async def mastermind(request: Request):
    """Mastermind page endpoint."""
    lang = get_current_lang(request)
    mm_i18n = {key: get_translation(lang, f'games.mastermind.{key}') for key in MASTERMIND_I18N_KEYS}
    return templates.TemplateResponse(
        "mastermind.html",
        {"request": request, "lang": lang, "mm_i18n": mm_i18n},
    )


@app.get("/go", response_class=HTMLResponse)
async def go_game(request: Request):
    """Go (board game) page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("go.html", {"request": request, "lang": lang})


@app.get("/chinese-checkers", response_class=HTMLResponse)
async def chinese_checkers(request: Request):
    """Chinese Checkers page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("chinese_checkers.html", {"request": request, "lang": lang})


@app.get("/backgammon", response_class=HTMLResponse)
async def backgammon(request: Request):
    """Backgammon page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("backgammon.html", {"request": request, "lang": lang})


@app.get("/reversi", response_class=HTMLResponse)
async def reversi(request: Request):
    """Reversi (Othello) page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("reversi.html", {"request": request, "lang": lang})


TRB_I18N_KEYS = [
    'player_placeholder', 'start_game', 'players_heading', 'play_again', 'change_players',
    'roll_dice', 'turn_banner', 'choose_peg', 'msg_exit', 'msg_moved', 'msg_bump',
    'msg_blocked', 'msg_extra_turn', 'msg_home', 'win_title', 'win_subtitle',
]


@app.get("/trouble", response_class=HTMLResponse)
async def trouble(request: Request):
    """Trouble board game page endpoint."""
    lang = get_current_lang(request)
    trb_i18n = {key: get_translation(lang, f'games.trouble.{key}') for key in TRB_I18N_KEYS}
    return templates.TemplateResponse(
        "trouble.html",
        {"request": request, "lang": lang, "trb_i18n": trb_i18n},
    )


SPADES_I18N_KEYS = [
    'setup_heading', 'setup_subheading', 'name_placeholder', 'start_game', 'teams_note',
    'bid_heading', 'bid_nil', 'bid_prompt', 'bid_confirm', 'player_bid', 'player_bid_nil',
    'trick_lead', 'you_win_trick', 'player_wins_trick', 'spades_broken',
    'round_summary', 'made_bid', 'missed_bid', 'nil_made', 'nil_broken',
    'your_team', 'opp_team', 'bags_label', 'score_label', 'continue_round',
    'win_title', 'lose_title', 'final_score', 'play_again', 'change_players',
    'north', 'south', 'east', 'west',
]


@app.get("/spades", response_class=HTMLResponse)
async def spades(request: Request):
    """Spades card game page endpoint."""
    lang = get_current_lang(request)
    spades_i18n = {key: get_translation(lang, f'games.spades.{key}') for key in SPADES_I18N_KEYS}
    return templates.TemplateResponse(
        "spades.html",
        {"request": request, "lang": lang, "spades_i18n": spades_i18n},
    )


MATCHSTICK_I18N_KEYS = [
    'title', 'subtitle', 'difficulty', 'easy', 'medium', 'hard',
    'new_game', 'give_up', 'reset', 'undo', 'instruction', 'pick_hint',
    'moves_used', 'moves_target', 'reads_as', 'reads_incomplete',
    'win_title', 'win_message', 'wrong_count_message', 'gave_up_title',
    'solved_heading', 'solved_count', 'current_streak', 'best_streak',
    'legend_heading', 'rule_1', 'rule_2', 'rule_3', 'rule_4',
]


@app.get("/matchstick-puzzles", response_class=HTMLResponse)
async def matchstick_puzzles(request: Request):
    """Matchstick Puzzles page endpoint."""
    lang = get_current_lang(request)
    ms_i18n = {key: get_translation(lang, f'games.matchstick_puzzles.{key}') for key in MATCHSTICK_I18N_KEYS}
    return templates.TemplateResponse(
        "matchstick_puzzles.html",
        {"request": request, "lang": lang, "ms_i18n": ms_i18n},
    )


HEARTS_I18N_KEYS = [
    'you', 'west', 'north', 'east', 'new_game', 'next_hand', 'pass_button',
    'selected_count', 'select_three', 'pass_left', 'pass_right', 'pass_across', 'pass_none',
    'waiting_pass', 'your_turn', 'ai_thinking', 'leads_two_clubs', 'trick_winner',
    'hearts_broken', 'hand_complete', 'moon_shot', 'round_summary', 'game_over', 'you_win',
    'final_scores', 'scoreboard', 'hand_points', 'total_points',
]


@app.get("/hearts", response_class=HTMLResponse)
async def hearts(request: Request):
    """Hearts card game page endpoint."""
    lang = get_current_lang(request)
    hearts_i18n = {key: get_translation(lang, f'games.hearts.{key}') for key in HEARTS_I18N_KEYS}
    return templates.TemplateResponse(
        "hearts.html",
        {"request": request, "lang": lang, "hearts_i18n": hearts_i18n},
    )


@app.get("/eight-queens", response_class=HTMLResponse)
async def eight_queens(request: Request):
    """Eight Queens puzzle page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("eight_queens.html", {"request": request, "lang": lang})


@app.get("/tetris", response_class=HTMLResponse)
async def tetris(request: Request):
    """Tetris page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("tetris.html", {"request": request, "lang": lang})


@app.get("/simcity", response_class=HTMLResponse)
async def simcity(request: Request):
    """SimCity-lite city builder page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("simcity.html", {"request": request, "lang": lang})


@app.get("/math-crossword", response_class=HTMLResponse)
async def math_crossword(request: Request):
    """Math crossword puzzle page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("math_crossword.html", {"request": request, "lang": lang})


@app.get("/math-pyramid", response_class=HTMLResponse)
async def math_pyramid(request: Request):
    """Math pyramid puzzle page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("math_pyramid.html", {"request": request, "lang": lang})


UNO_I18N_KEYS = [
    'name', 'description', 'title', 'subtitle', 'setup_heading', 'setup_subheading',
    'name_placeholder', 'opponents_label', 'opponents_1', 'opponents_2', 'opponents_3',
    'start_game', 'you', 'west', 'north', 'east', 'your_turn', 'ai_thinking',
    'draw_card', 'pass_turn', 'choose_color', 'color_red', 'color_yellow', 'color_green',
    'color_blue', 'msg_play', 'msg_draw', 'msg_draw_n', 'msg_skip', 'msg_reverse',
    'msg_uno', 'msg_no_moves', 'round_summary', 'round_win', 'you_win_round',
    'points_label', 'scoreboard', 'total_points', 'next_round', 'win_title', 'lose_title',
    'final_scores', 'play_again', 'change_players',
    'rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5',
]


@app.get("/uno", response_class=HTMLResponse)
async def uno(request: Request):
    """Uno card game page endpoint."""
    lang = get_current_lang(request)
    uno_i18n = {key: get_translation(lang, f'games.uno.{key}') for key in UNO_I18N_KEYS}
    return templates.TemplateResponse(
        "uno.html",
        {"request": request, "lang": lang, "uno_i18n": uno_i18n},
    )


@app.get("/bus-parking", response_class=HTMLResponse)
async def bus_parking(request: Request):
    """Bus Parking color-matching puzzle page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("bus_parking.html", {"request": request, "lang": lang})


CLUEDO_I18N_KEYS = [
    'name', 'description', 'title', 'subtitle',
    'setup_heading', 'setup_subheading', 'name_placeholder', 'character_label',
    'opponents_label', 'opponents_1', 'opponents_2', 'opponents_3', 'opponents_4', 'opponents_5',
    'start_game', 'you', 'ai_suffix', 'your_turn', 'ai_thinking',
    'suggest_heading', 'suspect_label', 'weapon_label', 'room_label',
    'suggest_button', 'accuse_button', 'skip_turn',
    'accuse_confirm_title', 'accuse_confirm_body', 'accuse_confirm_yes', 'accuse_confirm_no',
    'accuse_room_hint',
    'give_up_button', 'give_up_confirm_title', 'give_up_confirm_body', 'give_up_confirm_yes', 'give_up_confirm_no',
    'notebook_heading', 'notebook_hint', 'notebook_you_col', 'notebook_solution_col',
    'suspects_heading', 'weapons_heading', 'rooms_heading', 'hand_heading', 'players_heading', 'log_heading',
    'board_heading', 'roll_dice', 'secret_passage', 'skip_move', 'move_hint',
    'asking_in_room', 'move_into_room_hint',
    'msg_suggest', 'msg_cannot_disprove', 'msg_shows_hidden', 'msg_you_show', 'msg_shown_to_you',
    'msg_no_one_disprove', 'msg_solution_deduced', 'msg_roll', 'msg_enter_room', 'msg_passage',
    'choose_card_title', 'choose_card_body',
    'msg_wrong_accusation', 'msg_you_wrong_accusation',
    'win_title', 'lose_title', 'stuck_title', 'solution_reveal',
    'play_again', 'change_players', 'eliminated_tag',
    'rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5', 'rule_6',
    'suspect_scarlett', 'suspect_mustard', 'suspect_white', 'suspect_green', 'suspect_peacock', 'suspect_plum',
    'weapon_candlestick', 'weapon_knife', 'weapon_leadpipe', 'weapon_revolver', 'weapon_rope', 'weapon_wrench',
    'room_kitchen', 'room_ballroom', 'room_conservatory', 'room_diningroom', 'room_billiardroom',
    'room_library', 'room_lounge', 'room_hall', 'room_study',
]


@app.get("/cluedo", response_class=HTMLResponse)
async def cluedo(request: Request):
    """Cluedo deduction game page endpoint."""
    lang = get_current_lang(request)
    cluedo_i18n = {key: get_translation(lang, f'games.cluedo.{key}') for key in CLUEDO_I18N_KEYS}
    return templates.TemplateResponse(
        "cluedo.html",
        {"request": request, "lang": lang, "cluedo_i18n": cluedo_i18n},
    )


CRAZY_EIGHTS_I18N_KEYS = [
    'name', 'description', 'title', 'subtitle', 'setup_heading', 'setup_subheading',
    'name_placeholder', 'opponents_label', 'opponents_1', 'opponents_2', 'opponents_3',
    'start_game', 'you', 'west', 'north', 'east', 'your_turn', 'ai_thinking',
    'draw_card', 'pass_turn', 'choose_suit', 'suit_hearts', 'suit_diamonds', 'suit_clubs', 'suit_spades',
    'msg_play', 'msg_draw', 'msg_eight', 'msg_no_moves', 'round_summary', 'round_win', 'you_win_round',
    'points_label', 'scoreboard', 'total_points', 'next_round', 'win_title', 'lose_title',
    'final_scores', 'play_again', 'change_players',
    'rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5',
]


@app.get("/crazy-eights", response_class=HTMLResponse)
async def crazy_eights(request: Request):
    """Crazy Eights card game page endpoint."""
    lang = get_current_lang(request)
    crazy_eights_i18n = {key: get_translation(lang, f'games.crazy_eights.{key}') for key in CRAZY_EIGHTS_I18N_KEYS}
    return templates.TemplateResponse(
        "crazy_eights.html",
        {"request": request, "lang": lang, "crazy_eights_i18n": crazy_eights_i18n},
    )


@app.get("/number-match", response_class=HTMLResponse)
async def number_match(request: Request):
    """Number Match clearing puzzle page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("number_match.html", {"request": request, "lang": lang})


@app.get("/rubiks-cube", response_class=HTMLResponse)
async def rubiks_cube(request: Request):
    """Rubik's Cube 3D puzzle page endpoint."""
    lang = get_current_lang(request)
    return templates.TemplateResponse("rubiks_cube.html", {"request": request, "lang": lang})


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

