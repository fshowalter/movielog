# Movielog Application Documentation

## Overview

Movielog is a Python-based console application for managing a personal movie log, including reviews, viewings, and watchlists. The application exports data in JSON format and powers the website [franksmovielog.com](https://www.franksmovielog.com/).

## Architecture

### Core Components

1. **CLI Module** (`movielog/cli/`)
   - Interactive command-line interface for managing the movie log
   - Features for adding directors, performers, writers, viewings, and reviews
   - Collection and watchlist management

2. **Repository Module** (`movielog/repository/`)
   - Data access layer with validation and update functionality
   - JSON-based data storage for titles, cast/crew, collections, ratings
   - IMDb data integration and HTTP fetching capabilities
   - SQLite database for title and name searches

3. **Exports Module** (`movielog/exports/`)
   - Generates JSON exports for various data views
   - Includes specialized exports for statistics, watchlists, and curated lists
   - Protocol-based type definitions for consistency

4. **Utils Module** (`movielog/utils/`)
   - Common utilities for logging, list operations, and path handling

## Data Model

### Key Entities

- **Title**: Movie information including IMDb ID, release year, genres, runtime
- **Review**: User reviews with grades, dates, and associated viewings
- **Viewing**: Individual movie watching sessions with date, venue, and medium
- **Cast & Crew**: Directors, writers, and performers with their filmographies
- **Collection**: Curated lists of movies (e.g., franchises, themes)
- **Watchlist**: Titles queued for viewing, organized by cast/crew or collections

### Data Storage

- Reviews: Markdown files in `reviews/` directory
- Cast & Crew: JSON files in `cast-and-crew/` directory
- Collections: JSON files in `collections/` directory
- Exports: Generated JSON files in `export/` directory
- Database: SQLite database for efficient searching

## Key Features

### CLI Commands

The main entry point is `uv run movielog`, which provides an interactive menu for:

- **Add Viewing**: Log a new movie viewing with date, venue, and medium
- **Manage Watchlist**: Add/remove directors, performers, writers, or collections
- **Manage Collections**: Create and edit movie collections
- **Add to Collection**: Add titles to existing collections
- **Review Management**: Create and edit movie reviews

### Export Types

1. **reviewed-titles.json**: All reviewed movies with detailed metadata
2. **viewings.json**: Complete viewing history
3. **watchlist-titles.json**: Movies on the watchlist with attribution
4. **all-time-stats.json**: Aggregate statistics across all viewings
5. **year-stats/**: Annual statistics files
6. **cast-and-crew/**: Individual JSON files for each person
7. **collections/**: Individual JSON files for each collection
8. **overrated.json**: Movies with high IMDb ratings but low personal grades
9. **underrated.json**: Movies with low IMDb ratings but high personal grades
10. **underseen.json**: Hidden gems with low IMDb vote counts

### Type Safety

The exports module uses Protocol definitions (`protocols.py`) to ensure type consistency across different export formats. Key protocols include:

- `TitleProtocol`: Base protocol for all title types
- `ReviewedTitleProtocol`: Titles that have been reviewed
- `MaybeReviewedTitleProtocol`: Titles that may or may not have reviews
- `ReviewedTitleWithGradeProtocol`: Reviewed titles with grade information

## Development

### Setup

```bash
# Requires uv (https://github.com/astral-sh/uv)
uv sync
```

### Running Tests

```bash
uv run pytest
```

### Linting and Type Checking

```bash
uv run ruff check .
uv run mypy .
```

### Code Quality Tools

- **Ruff**: Fast Python linter with extensive rule sets
- **MyPy**: Static type checker with strict mode enabled
- **Pytest**: Testing framework with coverage reporting

## Common Workflows

### Adding a New Viewing

1. Run `uv run movielog`
2. Select "Add viewing"
3. Search for the movie title
4. Enter viewing details (date, venue, medium)
5. Optionally create a review

### Managing the Watchlist

1. Run `uv run movielog`
2. Select "Manage watchlist"
3. Choose to add directors, performers, writers, or collections
4. Search and select the desired person or collection

### Exporting Data

Exports are generated automatically when running the main application. To manually export:

```python
from movielog.exports.api import export_data
export_data()
```

## Data Flow

1. **Input**: User interactions through CLI or direct file edits
2. **Validation**: Repository validators ensure data integrity
3. **Storage**: Data persisted in JSON/Markdown files and SQLite
4. **Export**: Export modules transform data for web consumption
5. **Output**: JSON files consumed by the static site generator

## Notes

- The application uses IMDb IDs as primary identifiers for movies and people
- All dates are stored in ISO format (YYYY-MM-DD)
- Grades use a letter-based system (A+ to F)
- The SQLite database is primarily for search functionality, not primary storage

## Pre-Pull Request Checklist

**IMPORTANT**: Before creating any pull request, always:

1. **Rebase on main**:

   ```bash
   git pull --rebase origin main
   ```

2. **Run all checks**:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy .
   uv run pytest
   npm run format  # checks prettier formatting
   ```

3. **Fix any issues** found by the checks before proceeding with the PR
