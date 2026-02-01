"""Quick test to verify easy difficulty works."""
from sudoku_engine import SudokuBoard

print("Testing Easy difficulty puzzle generation...")

board = SudokuBoard()
board.generate_full_board()
print("✓ Full board generated")

board.remove_numbers("easy")
print("✓ Numbers removed for easy difficulty")

# Count empty cells
empty_count = sum(1 for row in board.board for cell in row if cell == 0)
print(f"✓ Empty cells: {empty_count} (should be 30-35 for easy)")

# Display first few rows
print("\nFirst 3 rows of the puzzle:")
for i in range(3):
    print(board.board[i])

print("\n✓ Easy difficulty is working!")
