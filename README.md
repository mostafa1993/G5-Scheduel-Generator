# G5 Spaced Repetition Schedule Generator

A Python tool for generating spaced repetition learning schedules using the G5 method.

## Overview

This tool helps you create and manage learning schedules based on the G5 spaced repetition method. It generates a schedule that includes both learning sessions and review sessions, optimized for long-term retention.

## Features

- Generate complete learning schedules with automatic review dates
- Export schedules to JSON format for easy storage and sharing
- Export schedules to iCalendar (.ics) format for Google Calendar integration
- Command-line interface for easy use
- Customizable start dates and number of sets

## Installation

### Option 1: Install from source

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/g5.git
   cd g5
   ```

2. Install the package:
   ```
   pip install -e .
   ```

### Option 2: Install dependencies only

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/g5.git
   cd g5
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

Generate a schedule with the following command:

```
python g5_generator.py -d DD-MM-YYYY -n NUM_SETS -s SET_NUMBER -o OUTPUT_FILE
```

Or if installed as a package:

```
g5 -d DD-MM-YYYY -n NUM_SETS -s SET_NUMBER -o OUTPUT_FILE
```

Options:
- `-d, --start-date`: Start date in DD-MM-YYYY format (defaults to today)
- `-n, --num-sets`: Number of new sets to add (required)
- `-s, --set-number`: Set number that corresponds to the start date (default: 1)
- `-o, --output`: Path to output JSON file (default: g5_schedule.json)
- `-c, --calendar`: Export schedule to iCalendar (.ics) file for Google Calendar import

### Examples

Generate a schedule starting today with 5 new sets:
```
python g5_generator.py -n 5
```

Generate a schedule starting on a specific date with 10 new sets:
```
python g5_generator.py -d 01-01-2023 -n 10
```

Generate a schedule and export to Google Calendar:
```
python g5_generator.py -n 5 -c g5_schedule.ics
```

## Project Structure

The project is organized into the following modules:

- `g5/models/set.py`: Contains the `Set` class representing a learning set
- `g5/models/schedule.py`: Contains the `G5Schedule` class for managing schedules
- `g5/utils/icalendar_export.py`: Utility for exporting schedules to iCalendar format
- `g5/cli.py`: Command-line interface for the tool

## G5 Method

The G5 method is a spaced repetition learning technique that involves:

1. Learning new material on day 1
2. Reviewing on day 2
3. Reviewing on day 4
4. Reviewing on day 8
5. Reviewing on day 15

This spacing pattern is designed to optimize long-term retention by reviewing material at increasing intervals.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or feedback, please open an issue on the GitHub repository. 