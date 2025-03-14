import requests
from bs4 import BeautifulSoup
import re

def get_lichess_game_errors(url):
    """
    Extract moves labeled as Inaccuracy, Mistake, or Blunder from a Lichess game URL.
    
    Args:
        url (str): URL of the Lichess game
        
    Returns:
        dict: Dictionary with move numbers as keys and error details as values
    """
    # Make HTTP GET request to the URL
    print(f"Making a HTTP call to {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": f"Failed to fetch the URL. Status code: {response.status_code}"}
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the PGN content
    pgn_div = soup.find('div', class_='pgn')
    
    if not pgn_div:
        return {"error": "Could not find PGN content in the page"}
    
    pgn_text = pgn_div.text
    
    # Dictionary to store results
    errors_by_move = {}
    
    # Regular expressions for white moves with errors
    white_pattern = r'(\d+)\.\s+([^\s]+)(\?|\?\?|\?\!)\s+\{\s+\([^)]+\)\s+(Mistake|Blunder|Inaccuracy)\.'
    
    # Regular expressions for black moves with errors
    black_pattern = r'(\d+)\.\.\.\s+([^\s]+)(\?|\?\?|\?\!)\s+\{\s+\([^)]+\)\s+(Mistake|Blunder|Inaccuracy)\.'
    
    # Find white's errors
    white_matches = re.findall(white_pattern, pgn_text)
    for move_number, move, symbol, error_type in white_matches:
        if move_number not in errors_by_move.keys():
            errors_by_move[move_number] = {}
        errors_by_move[move_number]["white"] = {
            "color": "white",
            "move": move,
            "error_type": error_type,
            "symbol": symbol
        }
    
    # Find black's errors
    black_matches = re.findall(black_pattern, pgn_text)
    for move_number, move, symbol, error_type in black_matches:
        # key = f"{move_number}..."  # Use "..." to denote Black's move
        if move_number not in errors_by_move.keys():
            errors_by_move[move_number] = {}
        errors_by_move[move_number]["black"] = {
            "color": "black",
            "move": move,
            "error_type": error_type,
            "symbol": symbol
        }
    
    return errors_by_move

print(get_lichess_game_errors("https://lichess.org/PpwPOZMq"))
