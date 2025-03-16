import argparse
import requests
from bs4 import BeautifulSoup
import logging
import re

def setup_logger(log_level=logging.INFO):
    """
    Set up and configure a logger for console output
    
    Args:
        log_level: The logging level (default: logging.INFO)
    
    Returns:
        A configured logger instance
    """
    # Create logger
    logger = logging.getLogger('chess_pgn_analyzer')
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_lichess_game_errors(url):
    """
    Extract moves labeled as Inaccuracy, Mistake, or Blunder from a Lichess game URL.
    
    Args:
        url (str): URL of the Lichess game
        
    Returns:
        dict: Dictionary with move numbers as keys and error details as values
    """
    # Make HTTP GET request to the URL
    logger.info(f"Making a HTTP call to {url}")
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
    
    logger.info(f"Errors by move: {errors_by_move}")
    return errors_by_move

def embellish_pgn(pgn):
    """
    Annotates a PGN file with error types from Lichess.

    Args:
        pgn (str): Raw PGN content

    Returns:
        str: Updated PGN with annotations
    """
    logger.info("In embellish pgn")
    games = pgn.strip().split("\n\n[Event")  # Split PGN into individual games
    updated_pgn = []

    for game in games:
        logger.info("----------------------------")
        logger.info(f"Game: {games.index(game)}")
        lines = game.strip().split("\n")
        logger.info(f"Total number of lines of pgn to parse in this game: {len(lines)}")
        url = None
        moves_line_index = None

        # Extract the game URL
        for i, line in enumerate(lines):
            if line.startswith("[Site"):
                match = re.search(r'"(https://lichess\.org/\w+)"', line)
                if match:
                    url = match.group(1)
            # if not line.startswith("[") and moves_line_index is None:
            if line.startswith("1."):
                logger.info(f"Line of interest: {line}")
                moves_line_index = i
        

        if not url or moves_line_index is None:
            logger.warning("Warning: No URL found")
            updated_pgn.append(game)  # Skip if no URL found
            continue

        errors = get_lichess_game_errors(url)
        moves = lines[moves_line_index].split(" ")
        logger.debug(f"Moves: {moves}")

        # Annotate the moves with errors
        new_moves = []
        move_number = 1
        is_black_move = False

        for move in moves:
            if re.match(r"^\d+\.$", move):  # Detect move numbers (e.g., "1.")
                move_number = int(move[:-1])  # Remove "."
                new_moves.append(move)
                is_black_move = False
                continue

            if move in ["1-0", "0-1", "1/2-1/2"]:  # Detect result
                new_moves.append(move)
                break

            error_info = errors.get(str(move_number), {}).get("black" if is_black_move else "white")

            # if error_info and move == error_info["move"]:
            if error_info:
                move = f"{move} {{{error_info['error_type']}}}"

            new_moves.append(move)
            is_black_move = not is_black_move  # Switch turns

        # Replace original moves line
        lines[moves_line_index] = " ".join(new_moves)
        updated_pgn.append("\n".join(lines))

    return "\n\n[Event ".join(updated_pgn)


def main():
    global logger
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Utility that reads a pgn file,\
            and embellishes the chess moves with error info:\
            1. Inaccuracy\
            2. Blunder\
            3. Mistake'
    )
    parser.add_argument('input_file', help='Path to the input PGN file')
    parser.add_argument('output_file', help='Path to save the embellished PGN file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Set the logging level')
    
    # Parse the arguments
    args = parser.parse_args()

    # Set up logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logger(log_level)

    logger.info(f"Reading from: {args.input_file}")
    # with open( "../dataset/short_lichess.pgn", "r") as input_pgn_file:
    with open(args.input_file, "r") as input_pgn_file:
        input_pgn = input_pgn_file.read()
        embellished_pgn = embellish_pgn(input_pgn)
        # with open( "../dataset/short_lichess_embellished.pgn", "w") as output_pgn_file:
        logger.info(f"Writing the embellished file to : {args.output_file}")
        with open(args.output_file, "w") as output_pgn_file:
            output_pgn_file.write(embellished_pgn)

if __name__ == "__main__":
    main()

#  python3 analyze_game.py ../dataset/short_lichess.pgn ../dataset/short_lichess_embellished.pgn