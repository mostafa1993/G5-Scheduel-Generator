"""
Command-line interface for the G5 Spaced Repetition Schedule Generator.
"""

import argparse
from datetime import datetime
import pandas as pd

from g5.models.schedule import G5Schedule


def generate_g5_schedule(
    start_date_str,
    new_sets,
    set_number=1,
    json_path="g5_schedule.json",
    return_schedule=False,
):
    """
    Generate a G5 review schedule for spaced repetition learning.

    Args:
      start_date_str: String date in format 'DD-MM-YYYY' to start the schedule
      new_sets: Number of new sets to add to the schedule
      set_number: The set number that corresponds to start_date (default: 1 for first set)
      json_path: Path to JSON file for storing schedule data
      return_schedule: Whether to return the G5Schedule object in addition to DataFrame

    Returns:
      If return_schedule is False: DataFrame containing the complete schedule
      If return_schedule is True: (DataFrame, G5Schedule) tuple
    """
    try:
        # Convert start date from string to datetime
        given_date = datetime.strptime(start_date_str, "%d-%m-%Y")

        # Validate input
        if new_sets <= 0:
            raise ValueError("Number of new sets must be positive")

        if set_number < 1:
            raise ValueError("Set number must be positive")

        # Create schedule object directly from the given date and set number
        schedule = G5Schedule(given_date)

        # Add only the requested sets with the correct set numbers
        schedule.add_new_sets(new_sets, set_number)

        # Save to JSON
        schedule.save_to_json(json_path)

        # Calculate the theoretical day number for display
        # If this is set 1, day 1 is fine. Otherwise we need to offset
        day_offset = set_number - 1  # Each set is 1 day apart

        # Get DataFrame with the correct offset for day numbers
        df = schedule.to_dataframe(day_offset)

        # Return appropriate result based on return_schedule parameter
        if return_schedule:
            return df, schedule, None, set_number
        else:
            return df

    except Exception as e:
        print(f"Error generating schedule: {e}")
        raise


def main():
    """Command line interface for the G5 schedule generator."""
    parser = argparse.ArgumentParser(
        description="Generate a G5 spaced repetition schedule"
    )
    parser.add_argument(
        "-d",
        "--start-date",
        type=str,
        help="Start date in DD-MM-YYYY format (defaults to today if not specified)",
        default=datetime.now().strftime("%d-%m-%Y"),
    )
    parser.add_argument(
        "-n", "--num-sets", type=int, required=True, help="Number of new sets to add"
    )
    parser.add_argument(
        "-s",
        "--set-number",
        type=int,
        default=1,
        help="Set number that corresponds to the start date (default: 1)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="g5_schedule.json",
        help="Path to output JSON file (default: g5_schedule.json)",
    )
    parser.add_argument(
        "-c",
        "--calendar",
        type=str,
        help="Export schedule to iCalendar (.ics) file for Google Calendar import",
    )

    args = parser.parse_args()

    try:
        # Generate the schedule
        df, schedule, _, _ = generate_g5_schedule(
            start_date_str=args.start_date,
            new_sets=args.num_sets,
            set_number=args.set_number,
            json_path=args.output,
            return_schedule=True,
        )

        # Display the schedule
        print(f"\nG5 Schedule (saved to {args.output}):")
        print(f"Starting with Set {args.set_number:02d} on {args.start_date}")
        pd.set_option("display.max_colwidth", 100)
        print(df.to_string(index=False))

        # Export to iCalendar if requested
        if args.calendar:
            # Add .ics extension if not provided
            calendar_path = args.calendar
            if not calendar_path.lower().endswith(".ics"):
                calendar_path = f"{calendar_path}.ics"

            # Export calendar
            if schedule.export_to_ical(calendar_path):
                print(f"Schedule exported to iCalendar: {calendar_path}")
                print("You can import this file into Google Calendar:")
                print("1. Go to Google Calendar website")
                print("2. Click the '+' button next to 'Other calendars'")
                print("3. Select 'Import'")
                print("4. Upload the .ics file")

        return df

    except Exception as e:
        print(f"Failed to generate schedule: {e}")
        return None


if __name__ == "__main__":
    df = main()
