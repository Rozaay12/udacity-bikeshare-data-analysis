# Refactored code for better readability

import os
import time
import pandas as pd


CITY_DATA = {
    "chicago": "chicago.csv",
    "new york city": "new_york_city.csv",
    "washington": "washington.csv",
}

MONTHS = ["all", "january", "february", "march", "april", "may", "june"]
DAYS = ["all", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"]


def _resolve_csv_path(filename: str) -> str:
    """
    Resolve a CSV filename to a path that exists.

    Tries:
    1) Current working directory (relative path)
    2) /mnt/data/<filename> (common for hosted notebook/workspace environments)
    """
    if os.path.exists(filename):
        return filename

    mounted = os.path.join("/mnt/data", filename)
    if os.path.exists(mounted):
        return mounted

    return filename


def _prompt_choice(prompt: str, valid_values: list[str]) -> str:
    """
    Prompt the user for an input that must be in valid_values.

    - Case-insensitive
    - Strips whitespace
    - Re-prompts until valid
    """
    valid_set = set(valid_values)

    while True:
        user_in = input(prompt).strip().lower()

        if user_in in valid_set:
            return user_in

        print(f"Invalid input. Please choose from: {', '.join(valid_values)}")


def get_filters() -> tuple[str, str, str]:
    """
    Ask the user to specify a city, month, and day to analyze.

    Returns:
        city (str): city key from CITY_DATA
        month (str): month name in MONTHS, or 'all'
        day (str): day name in DAYS, or 'all'
    """
    print("Hello! Let's explore some US bikeshare data!")
    print("-" * 40)

    city = _prompt_choice(
        "Which city would you like to analyze? (Chicago, New York City, Washington)\n> ",
        list(CITY_DATA.keys()),
    )

    month = _prompt_choice(
        "Which month? (all, January, February, March, April, May, June)\n> ",
        MONTHS,
    )

    day = _prompt_choice(
        "Which day? (all, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)\n> ",
        DAYS,
    )

    print("-" * 40)
    return city, month, day


def load_data(city: str, month: str, day: str) -> pd.DataFrame:
    """
    Load data for the specified city and filter by month and day if applicable.

    Args:
        city: city key in CITY_DATA
        month: month name in MONTHS or 'all'
        day: day name in DAYS or 'all'

    Returns:
        Pandas DataFrame filtered by the selected month/day
    """
    csv_path = _resolve_csv_path(CITY_DATA[city])

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Could not find the file '{CITY_DATA[city]}'. "
            f"Looked for '{CITY_DATA[city]}' and '{os.path.join('/mnt/data', CITY_DATA[city])}'. "
            "Make sure the CSV is in the same folder as this script (or available under /mnt/data)."
        ) from e

    # Convert Start Time to datetime
    df["Start Time"] = pd.to_datetime(df["Start Time"])

    # Create derived columns for filtering
    df["month"] = df["Start Time"].dt.month  # 1-12
    # monday, ...
    df["day_of_week"] = df["Start Time"].dt.day_name().str.lower()

    # Filter by month
    if month != "all":
        month_num = MONTHS.index(month)  # january->1, ... june->6
        df = df[df["month"] == month_num]

    # Filter by day
    if day != "all":
        df = df[df["day_of_week"] == day]

    return df


def time_stats(df: pd.DataFrame) -> None:
    """Display statistics on the most frequent times of travel."""
    print("\nCalculating The Most Frequent Times of Travel...\n")
    start_time = time.time()

    # Most common month
    common_month_num = int(df["month"].mode()[0])
    common_month_name = MONTHS[common_month_num] if 1 <= common_month_num <= 6 else str(
        common_month_num)
    print(f"Most common month: {common_month_name.title()}")

    # Most common day of week
    common_day = df["day_of_week"].mode()[0]
    print(f"Most common day of week: {common_day.title()}")

    # Most common start hour
    common_hour = int(df["Start Time"].dt.hour.mode()[0])
    print(f"Most common start hour: {common_hour}:00")

    print(f"\nThis took {time.time() - start_time:.4f} seconds.")
    print("-" * 40)


def station_stats(df: pd.DataFrame) -> None:
    """Display statistics on the most popular stations and trip."""
    print("\nCalculating The Most Popular Stations and Trip...\n")
    start_time = time.time()

    # Most commonly used start station
    start_station = df["Start Station"].mode()[0]
    print(f"Most commonly used start station: {start_station}")

    # Most commonly used end station
    end_station = df["End Station"].mode()[0]
    print(f"Most commonly used end station: {end_station}")

    # Most frequent combination of start and end station
    combo = df.groupby(["Start Station", "End Station"]
                       ).size().sort_values(ascending=False).index[0]
    print(f"Most frequent trip: {combo[0]}  ->  {combo[1]}")

    print(f"\nThis took {time.time() - start_time:.4f} seconds.")
    print("-" * 40)


def trip_duration_stats(df: pd.DataFrame) -> None:
    """Display statistics on the total and average trip duration."""
    print("\nCalculating Trip Duration...\n")
    start_time = time.time()

    # Total travel time
    total_seconds = df["Trip Duration"].sum()
    total_hours = total_seconds / 3600
    print(
        f"Total travel time: {total_seconds:,} seconds ({total_hours:,.2f} hours)")

    # Mean travel time
    mean_seconds = df["Trip Duration"].mean()
    mean_minutes = mean_seconds / 60
    print(
        f"Mean travel time: {mean_seconds:,.2f} seconds ({mean_minutes:,.2f} minutes)")

    print(f"\nThis took {time.time() - start_time:.4f} seconds.")
    print("-" * 40)


def user_stats(df: pd.DataFrame) -> None:
    """Display statistics on bikeshare users."""
    print("\nCalculating User Stats...\n")
    start_time = time.time()

    # Counts of user types
    if "User Type" in df.columns:
        print("Counts of user types:")
        print(df["User Type"].value_counts())
        print()
    else:
        print("User Type column not available.\n")

    # Counts of gender (not available in Washington dataset)
    if "Gender" in df.columns:
        print("Counts of gender:")
        print(df["Gender"].value_counts(dropna=False))
        print()
    else:
        print("Gender column not available for this city.\n")

    # Birth year stats (not available in Washington dataset)
    if "Birth Year" in df.columns:
        # Handle possible missing values
        birth_years = df["Birth Year"].dropna()
        if not birth_years.empty:
            earliest = int(birth_years.min())
            most_recent = int(birth_years.max())
            most_common = int(birth_years.mode()[0])

            print(f"Earliest year of birth: {earliest}")
            print(f"Most recent year of birth: {most_recent}")
            print(f"Most common year of birth: {most_common}\n")
        else:
            print("Birth Year column exists but contains no usable data.\n")
    else:
        print("Birth Year column not available for this city.\n")

    print(f"This took {time.time() - start_time:.4f} seconds.")
    print("-" * 40)


def display_raw_data(df: pd.DataFrame) -> None:
    """
    Display raw data in chunks of 5 rows upon request.

    Rubric behavior:
    - Prompt user if they want to see 5 lines of raw data
    - If yes, show next 5 rows
    - Repeat until user says no OR no more data
    """
    row_index = 0

    while True:
        choice = input(
            "Would you like to see 5 lines of raw data? Enter yes or no.\n> ").strip().lower()

        if choice == "yes":
            if row_index >= len(df):
                print("No more raw data to display.")
                break

            print(df.iloc[row_index: row_index + 5])
            row_index += 5
            print("-" * 40)

        elif choice == "no":
            break

        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def main() -> None:
    """Main program loop."""
    while True:
        city, month, day = get_filters()
        df = load_data(city, month, day)

        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)

        display_raw_data(df)

        restart = input(
            "\nWould you like to restart? Enter yes or no.\n> ").strip().lower()
        if restart != "yes":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
