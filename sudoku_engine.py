"""Sudoku game engine with board generation, validation, and solving."""
import random
from typing import List, Optional, Tuple


class SudokuBoard:
    """Represents a Sudoku board with game logic."""
    
    def __init__(self, size: int = 9):
        """Initialize a Sudoku board.
        
        Args:
            size: Size of the board (default 9 for standard Sudoku)
        """
        self.size = size
        self.board: List[List[int]] = [[0 for _ in range(size)] for _ in range(size)]
        self.solution: List[List[int]] = [[0 for _ in range(size)] for _ in range(size)]
        
    def is_valid_move(self, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid according to Sudoku rules.
        
        Standard Sudoku rules:
        1. Each row must contain unique numbers 1-9
        2. Each column must contain unique numbers 1-9
        3. Each 3x3 box must contain unique numbers 1-9
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)
            
        Returns:
            True if the move is valid, False otherwise
        """
        # Temporarily store the current value and clear the cell
        current_value = self.board[row][col]
        self.board[row][col] = 0
        
        # Rule 1: Check row - no duplicate in same row
        for c in range(self.size):
            if self.board[row][c] == num:
                self.board[row][col] = current_value
                return False
        
        # Rule 2: Check column - no duplicate in same column
        for r in range(self.size):
            if self.board[r][col] == num:
                self.board[row][col] = current_value
                return False
        
        # Rule 3: Check 3x3 box - no duplicate in same 3x3 box
        # Calculate which 3x3 box this cell belongs to
        box_row_start = 3 * (row // 3)
        box_col_start = 3 * (col // 3)
        
        # Check all cells in the 3x3 box
        for i in range(box_row_start, box_row_start + 3):
            for j in range(box_col_start, box_col_start + 3):
                if self.board[i][j] == num:
                    self.board[row][col] = current_value
                    return False
        
        # Restore the original value and return success
        self.board[row][col] = current_value
        return True
    
    def solve(self, board: Optional[List[List[int]]] = None) -> bool:
        """Solve the Sudoku puzzle using backtracking.
        
        Args:
            board: Board to solve (uses self.board if None)
            
        Returns:
            True if solved, False if no solution exists
        """
        if board is None:
            board = self.board
            
        # Find empty cell
        empty = self._find_empty_cell(board)
        if not empty:
            return True  # Board is complete
        
        row, col = empty
        
        # Try numbers 1-9
        for num in range(1, 10):
            if self._is_valid_for_board(board, row, col, num):
                board[row][col] = num
                
                if self.solve(board):
                    return True
                
                # Backtrack
                board[row][col] = 0
        
        return False
    
    def _find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find an empty cell (with value 0) in the board."""
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def _is_valid_for_board(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid for a specific board."""
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        if num in [board[i][col] for i in range(self.size)]:
            return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False
        
        return True
    
    def generate_full_board(self) -> None:
        """Generate a complete valid Sudoku board."""
        # Start with empty board
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Fill diagonal 3x3 boxes first (they don't affect each other)
        for box in range(0, self.size, 3):
            self._fill_box(box, box)
        
        # Solve the rest
        self.solve()
        
        # Store the solution
        self.solution = [row[:] for row in self.board]
    
    def _fill_box(self, row_start: int, col_start: int) -> None:
        """Fill a 3x3 box with random valid numbers."""
        nums = list(range(1, 10))
        random.shuffle(nums)
        
        idx = 0
        for i in range(3):
            for j in range(3):
                self.board[row_start + i][col_start + j] = nums[idx]
                idx += 1
    
    def remove_numbers(self, difficulty: str = "medium") -> None:
        """Remove numbers from the board based on difficulty.
        
        Args:
            difficulty: "easy" (30-35 removed), "medium" (40-45 removed), 
                       "hard" (50-55 removed)
        """
        # Determine how many cells to remove
        remove_count = {
            "easy": random.randint(30, 35),
            "medium": random.randint(40, 45),
            "hard": random.randint(50, 55)
        }.get(difficulty, 40)
        
        # Remove numbers randomly
        cells = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(cells)
        
        for i in range(remove_count):
            row, col = cells[i]
            self.board[row][col] = 0
    
    def place_number(self, row: int, col: int, num: int) -> bool:
        """Place a number on the board.
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9, or 0 to clear)
            
        Returns:
            True if placement was successful, False otherwise
        """
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        if num == 0:
            self.board[row][col] = 0
            return True
        
        if not (1 <= num <= 9):
            return False
        
        if self.is_valid_move(row, col, num):
            self.board[row][col] = num
            return True
        
        return False
    
    def is_complete(self) -> bool:
        """Check if the board is completely filled."""
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def is_correct(self) -> bool:
        """Check if the current board matches the solution."""
        return self.board == self.solution
    
    def get_board(self) -> List[List[int]]:
        """Get the current board state."""
        return [row[:] for row in self.board]
    
    def get_solution(self) -> List[List[int]]:
        """Get the solution board."""
        return [row[:] for row in self.solution]
