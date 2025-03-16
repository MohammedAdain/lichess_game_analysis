# lichess_game_analysis

## Chess PGN Analyzer

A utility that enhances chess PGN files by automatically annotating moves marked as errors (Inaccuracies, Mistakes, and Blunders) from Lichess game analysis.

## Description

Chess PGN Analyzer parses PGN (Portable Game Notation) files containing Lichess game URLs, retrieves error analysis information from those games, and annotates the original PGN with error labels. This helps chess players quickly identify problematic moves in their game collections without manually checking each game.

## Features

- Extracts Lichess game URLs from PGN files
- Fetches game analysis data from Lichess
- Identifies moves labeled as:
  - Inaccuracy (⁉)
  - Mistake (?)
  - Blunder (??)
- Annotates the original PGN file with error information
- Supports batch processing of multiple games in a single PGN file
- Configurable logging levels

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4
  - argparse
  - logging
  - re

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/MohammedAdain/lichess_game_analysis.git
   cd lichess_game_analysis
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script with an input PGN file and specify an output file:

```
python analyze_game.py input_file.pgn output_file.pgn [--log-level LEVEL]
```

### Arguments

- `input_file`: Path to the input PGN file containing Lichess game URLs
- `output_file`: Path to save the annotated PGN file
- `--log-level`: Optional logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Example

```
python analyze_game.py ../dataset/my_games.pgn ../dataset/my_games_annotated.pgn --log-level INFO
```

Note: To uncompress a pgn.zst file, use the zstd tool
```
zstd -d <PATH_TO_ZST_COMPRESSED_PGN_FILE>.pgn.zst 
```

## How It Works

1. The script parses the input PGN file and extracts Lichess game URLs
2. For each game, it:
   - Makes an HTTP request to the Lichess game URL
   - Parses the HTML to extract the PGN with analysis
   - Identifies moves marked as errors using regex patterns
   - Annotates the original PGN with error information
3. The enhanced PGN is written to the output file

## Input PGN Format Requirements

The input PGN file should include Lichess game URLs in the `[Site "..."]` tag. For example:

```
[Event "Casual Game"]
[Site "https://lichess.org/abc123def456"]
[Date "2023.10.15"]
[White "Player1"]
[Black "Player2"]
...
```

## Output Format

The output PGN will include annotations for erroneous moves. For example:

```
1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 {Inaccuracy} 4. Ng5 d5 {Mistake} 5. exd5 Nxd5 6. Nxf7 {Blunder} Kxf7
```

## Limitations

- Only works with Lichess games that have computer analysis
- Requires an active internet connection to fetch game data
- May be affected by Lichess website structure changes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
