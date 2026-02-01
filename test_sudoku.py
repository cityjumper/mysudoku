"""Test script to verify Sudoku constraints."""
from sudoku_engine import SudokuBoard

def test_3x3_constraint():
    """Test that 3x3 box constraint is enforced."""
    board = SudokuBoard()
    
    # Create a simple test case
    # Place a 5 at position (0,0) - top-left of first 3x3 box
    board.board[0][0] = 5
    
    # Try to place another 5 in the same 3x3 box
    # Should fail at any other position in the box
    test_positions = [
        (0, 1), (0, 2),  # Same row, same box
        (1, 0), (1, 1), (1, 2),  # Second row, same box
        (2, 0), (2, 1), (2, 2)   # Third row, same box
    ]
    
    print("Testing 3x3 box constraint:")
    print(f"Board has 5 at position (0,0)")
    print(f"\nTrying to place 5 at other positions in the same 3x3 box:")
    
    for row, col in test_positions:
        result = board.is_valid_move(row, col, 5)
        status = "❌ ALLOWED (BUG!)" if result else "✅ BLOCKED (correct)"
        print(f"  Position ({row},{col}): {status}")
    
    # Test that we CAN place 5 in a different 3x3 box
    print(f"\nTrying to place 5 in a different 3x3 box:")
    result = board.is_valid_move(0, 3, 5)  # Different box (same row)
    status = "✅ ALLOWED (correct)" if result else "❌ BLOCKED (BUG!)"
    print(f"  Position (0,3): {status}")
    
    result = board.is_valid_move(3, 0, 5)  # Different box (same column)
    status = "✅ ALLOWED (correct)" if result else "❌ BLOCKED (BUG!)"
    print(f"  Position (3,0): {status}")
    
    # More comprehensive test with multiple numbers
    print("\n" + "="*50)
    print("Comprehensive 3x3 box test:")
    print("="*50)
    
    board2 = SudokuBoard()
    # Fill first 3x3 box with numbers 1-9
    board2.board[0][0] = 1
    board2.board[0][1] = 2
    board2.board[0][2] = 3
    board2.board[1][0] = 4
    board2.board[1][1] = 5
    board2.board[1][2] = 6
    board2.board[2][0] = 7
    board2.board[2][1] = 8
    # Position (2,2) is empty
    
    print("\nFirst 3x3 box contains: 1,2,3,4,5,6,7,8 (9 is missing)")
    print("Position (2,2) is empty")
    
    # Try placing 9 (should work)
    result = board2.is_valid_move(2, 2, 9)
    print(f"\nTrying to place 9 at (2,2): {'✅ ALLOWED (correct)' if result else '❌ BLOCKED (BUG!)'}")
    
    # Try placing any other number 1-8 (should fail)
    print("\nTrying to place numbers 1-8 at (2,2) (all should be blocked):")
    for num in range(1, 9):
        result = board2.is_valid_move(2, 2, num)
        status = "❌ ALLOWED (BUG!)" if result else "✅ BLOCKED (correct)"
        print(f"  Number {num}: {status}")

def test_row_and_column():
    """Test row and column constraints."""
    board = SudokuBoard()
    
    print("\n" + "="*50)
    print("Testing Row and Column constraints:")
    print("="*50)
    
    # Test row constraint
    board.board[0][0] = 7
    print("\nBoard has 7 at position (0,0)")
    result = board.is_valid_move(0, 8, 7)  # Same row, different box
    print(f"Trying to place 7 at (0,8) same row: {'❌ ALLOWED (BUG!)' if result else '✅ BLOCKED (correct)'}")
    
    # Test column constraint
    board2 = SudokuBoard()
    board2.board[0][0] = 7
    result = board2.is_valid_move(8, 0, 7)  # Same column, different box
    print(f"Trying to place 7 at (8,0) same column: {'❌ ALLOWED (BUG!)' if result else '✅ BLOCKED (correct)'}")

if __name__ == "__main__":
    test_3x3_constraint()
    test_row_and_column()
    print("\n" + "="*50)
    print("Test complete!")
    print("="*50)
