import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATASET_FILE = "Dataset.csv"
OUTPUT_FILE = "output.txt"
GRAPH_FILE = "location_analysis_graph.png"
HIGH_RATING_LIMIT = 4.0


def get_column(df, possible_names):
    clean_columns = {column.strip().lower(): column for column in df.columns}
    for name in possible_names:
        if name.strip().lower() in clean_columns:
            return clean_columns[name.strip().lower()]
    return None


def add_heading(lines, heading):
    lines.append(heading)
    lines.append("-" * len(heading))


def add_series(lines, title, series, limit=None):
    lines.append(title)
    if series is None or len(series) == 0:
        lines.append("Not available")
        lines.append("")
        return

    if limit is not None:
        series = series.head(limit)

    for index, value in series.items():
        lines.append(f"{index}: {value}")
    lines.append("")


def add_dataframe(lines, title, data, limit=None):
    lines.append(title)
    if data is None or data.empty:
        lines.append("Not available")
        lines.append("")
        return

    if limit is not None:
        data = data.head(limit)

    lines.append(data.to_string())
    lines.append("")


def make_number_column(df, column):
    if column is None:
        return None
    return pd.to_numeric(df[column], errors="coerce")


def most_common_cuisine(values):
    cuisines = []
    for value in values.dropna().astype(str):
        for cuisine in value.split(","):
            cuisine = cuisine.strip()
            if cuisine:
                cuisines.append(cuisine)

    if len(cuisines) == 0:
        return np.nan
    return pd.Series(cuisines).value_counts().index[0]


def most_common_value(values):
    values = values.dropna()
    if len(values) == 0:
        return np.nan
    return values.mode().iloc[0]


def main():
    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError("Dataset.csv must be in the same folder as task4.py")

    df = pd.read_csv(DATASET_FILE)

    city_col = get_column(df, ["City"])
    locality_col = get_column(df, ["Locality", "Locality Verbose"])
    latitude_col = get_column(df, ["Latitude"])
    longitude_col = get_column(df, ["Longitude"])
    country_col = get_column(df, ["Country", "Country Code"])
    rating_col = get_column(df, ["Aggregate rating", "Rating", "Average Rating"])
    price_col = get_column(df, ["Price range", "Price Range"])
    cuisine_col = get_column(df, ["Cuisines", "Cuisine"])

    rating = make_number_column(df, rating_col)
    price = make_number_column(df, price_col)
    latitude = make_number_column(df, latitude_col)
    longitude = make_number_column(df, longitude_col)

    total_rows = len(df)
    lines = []

    add_heading(lines, "Dataset Overview")
    lines.append(f"Number of rows: {df.shape[0]}")
    lines.append(f"Number of columns: {df.shape[1]}")
    lines.append(f"Duplicate rows: {df.duplicated().sum()}")
    lines.append("")

    lines.append("Missing Values")
    for column, missing_count in df.isnull().sum().items():
        lines.append(f"{column}: {missing_count}")
    lines.append("")

    if city_col is not None:
        city_counts = df[city_col].dropna().astype(str).value_counts()
        city_density = pd.DataFrame({
            "restaurant_count": city_counts,
            "percentage_of_total": (city_counts / total_rows * 100).round(2)
        })
    else:
        city_counts = None
        city_density = None

    if locality_col is not None:
        locality_counts = df[locality_col].dropna().astype(str).value_counts()
    else:
        locality_counts = None

    add_heading(lines, "Location Analysis")
    add_series(lines, "Number of Restaurants by City", city_counts)
    add_series(lines, "Number of Restaurants by Locality", locality_counts)
    add_series(lines, "Top 10 Cities by Restaurant Count", city_counts, 10)
    add_series(lines, "Top 10 Localities by Restaurant Count", locality_counts, 10)

    if city_col is not None:
        lines.append(f"Number of unique cities: {df[city_col].nunique(dropna=True)}")
    else:
        lines.append("Number of unique cities: Not available")

    if locality_col is not None:
        lines.append(f"Number of unique localities: {df[locality_col].nunique(dropna=True)}")
    else:
        lines.append("Number of unique localities: Not available")
    lines.append("")

    lines.append("Latitude Range")
    if latitude is not None and latitude.notna().any():
        lines.append(f"Minimum latitude: {latitude.min()}")
        lines.append(f"Maximum latitude: {latitude.max()}")
        lines.append(f"Latitude range: {latitude.max() - latitude.min()}")
    else:
        lines.append("Not available")
    lines.append("")

    lines.append("Longitude Range")
    if longitude is not None and longitude.notna().any():
        lines.append(f"Minimum longitude: {longitude.min()}")
        lines.append(f"Maximum longitude: {longitude.max()}")
        lines.append(f"Longitude range: {longitude.max() - longitude.min()}")
    else:
        lines.append("Not available")
    lines.append("")

    add_dataframe(lines, "Restaurant Density by City", city_density)
    add_dataframe(lines, "Cities Containing the Highest Concentration of Restaurants", city_density, 10)

    if city_density is not None and not city_density.empty:
        low_density = city_density.sort_values(
            ["restaurant_count", "percentage_of_total"], ascending=[True, True]
        )
    else:
        low_density = None
    add_dataframe(lines, "Cities Containing the Lowest Concentration of Restaurants", low_density, 10)

    if country_col is not None:
        country_counts = df[country_col].dropna().astype(str).value_counts()
    else:
        country_counts = None
    add_series(lines, "Distribution of Restaurants Across Countries", country_counts)

    add_heading(lines, "City Analysis")
    add_series(lines, "Restaurants per City", city_counts)

    if city_col is not None and rating is not None:
        city_rating_table = (
            df.assign(_rating=rating)
            .groupby(city_col)["_rating"]
            .agg(["count", "mean", "min", "max"])
            .dropna()
        )
        city_rating_table["mean"] = city_rating_table["mean"].round(2)
        city_rating_table["rating_range"] = (city_rating_table["max"] - city_rating_table["min"]).round(2)
        city_rating_table = city_rating_table.sort_values("mean", ascending=False)
        city_rating_average = city_rating_table["mean"]
        city_rating_range = city_rating_table["rating_range"].sort_values(ascending=False)
    else:
        city_rating_table = None
        city_rating_average = None
        city_rating_range = None

    if city_col is not None and price is not None:
        city_price_table = (
            df.assign(_price=price)
            .groupby(city_col)["_price"]
            .agg(["count", "mean", "min", "max"])
            .dropna()
        )
        city_price_table["mean"] = city_price_table["mean"].round(2)
        city_price_table = city_price_table.sort_values("mean", ascending=False)
        city_price_average = city_price_table["mean"]
    else:
        city_price_table = None
        city_price_average = None

    add_dataframe(lines, "City Rating Statistics", city_rating_table)
    add_series(lines, "Cities with the Highest Average Ratings", city_rating_average, 10)
    add_series(
        lines,
        "Cities with the Lowest Average Ratings",
        None if city_rating_average is None else city_rating_average.sort_values(ascending=True),
        10
    )
    add_series(lines, "Cities with the Widest Range of Ratings", city_rating_range, 10)
    add_dataframe(lines, "City Price Range Statistics", city_price_table)
    add_series(lines, "Cities with the Highest Average Price Range", city_price_average, 10)
    add_series(
        lines,
        "Cities with the Lowest Average Price Range",
        None if city_price_average is None else city_price_average.sort_values(ascending=True),
        10
    )

    add_heading(lines, "Locality Analysis")
    add_series(lines, "Restaurants per Locality", locality_counts)

    if locality_col is not None and rating is not None:
        locality_rating_table = (
            df.assign(_rating=rating)
            .groupby(locality_col)["_rating"]
            .agg(["count", "mean", "min", "max"])
            .dropna()
        )
        locality_rating_table["mean"] = locality_rating_table["mean"].round(2)
        locality_rating_table["rating_range"] = (
            locality_rating_table["max"] - locality_rating_table["min"]
        ).round(2)
        locality_rating_table = locality_rating_table.sort_values("mean", ascending=False)
        locality_rating_average = locality_rating_table["mean"]
    else:
        locality_rating_table = None
        locality_rating_average = None

    if locality_col is not None and price is not None:
        locality_price_table = (
            df.assign(_price=price)
            .groupby(locality_col)["_price"]
            .agg(["count", "mean", "min", "max"])
            .dropna()
        )
        locality_price_table["mean"] = locality_price_table["mean"].round(2)
        locality_price_table = locality_price_table.sort_values("mean", ascending=False)
    else:
        locality_price_table = None

    add_dataframe(lines, "Locality Rating Statistics", locality_rating_table)
    add_series(lines, "Localities with the Highest Average Ratings", locality_rating_average, 10)
    add_series(
        lines,
        "Localities with the Lowest Average Ratings",
        None if locality_rating_average is None else locality_rating_average.sort_values(ascending=True),
        10
    )
    add_dataframe(lines, "Locality Price Range Statistics", locality_price_table)

    add_heading(lines, "Rating Analysis by Location")
    add_series(lines, "Average Rating by City", city_rating_average)
    add_series(lines, "Average Rating by Locality", locality_rating_average)

    if city_col is not None and rating is not None:
        high_rating_city_counts = (
            df.assign(_rating=rating)
            .loc[lambda data: data["_rating"] > HIGH_RATING_LIMIT]
            .groupby(city_col)
            .size()
            .sort_values(ascending=False)
        )
    else:
        high_rating_city_counts = None
    add_series(
        lines,
        f"Cities Containing the Highest Number of Highly Rated Restaurants (Aggregate Rating > {HIGH_RATING_LIMIT})",
        high_rating_city_counts,
        10
    )

    add_heading(lines, "Price Range Analysis by Location")
    add_series(lines, "Average Price Range by City", city_price_average)
    if locality_price_table is not None:
        locality_price_average = locality_price_table["mean"]
    else:
        locality_price_average = None
    add_series(lines, "Average Price Range by Locality", locality_price_average)

    add_heading(lines, "Location Statistics")
    if latitude is not None and longitude is not None:
        valid_coordinates = latitude.notna() & longitude.notna()
        valid_coordinates = valid_coordinates & latitude.between(-90, 90) & longitude.between(-180, 180)
        coordinate_count = int(valid_coordinates.sum())
        coordinate_percent = round(coordinate_count / total_rows * 100, 2) if total_rows > 0 else 0
        lines.append(f"Number of restaurants with valid latitude and longitude: {coordinate_count}")
        lines.append(f"Percentage of restaurants with valid coordinates: {coordinate_percent}%")
    else:
        lines.append("Number of restaurants with valid latitude and longitude: Not available")
        lines.append("Percentage of restaurants with valid coordinates: Not available")
    lines.append("")

    lines.append("Latitude Summary Statistics")
    if latitude is not None and latitude.notna().any():
        for index, value in latitude.describe().round(4).items():
            lines.append(f"{index}: {value}")
    else:
        lines.append("Not available")
    lines.append("")

    lines.append("Longitude Summary Statistics")
    if longitude is not None and longitude.notna().any():
        for index, value in longitude.describe().round(4).items():
            lines.append(f"{index}: {value}")
    else:
        lines.append("Not available")
    lines.append("")

    add_series(lines, "Number of Restaurants per Country", country_counts)
    add_series(lines, "Number of Restaurants per City", city_counts)
    add_series(lines, "Number of Restaurants per Locality", locality_counts)

    add_heading(lines, "Interesting Location Patterns")
    if city_counts is not None and len(city_counts) > 0:
        top_city = city_counts.index[0]
        top_city_count = city_counts.iloc[0]
        top_city_percent = round(top_city_count / total_rows * 100, 2) if total_rows > 0 else 0
        lines.append(f"City with the highest restaurant count: {top_city}")
        lines.append(f"Highest city restaurant count: {top_city_count}")
        lines.append(f"Highest city percentage of total restaurants: {top_city_percent}%")
        lines.append("")
    else:
        lines.append("City with the highest restaurant count: Not available")
        lines.append("")

    if city_col is not None and cuisine_col is not None and city_counts is not None:
        top_cities = list(city_counts.head(10).index)
        cuisine_rows = []
        for city in top_cities:
            city_data = df[df[city_col].astype(str) == str(city)]
            cuisine_rows.append({
                "City": city,
                "Most Common Cuisine": most_common_cuisine(city_data[cuisine_col])
            })
        common_cuisine_table = pd.DataFrame(cuisine_rows).set_index("City")
    else:
        common_cuisine_table = None
    add_dataframe(lines, "Most Common Cuisine in Each of the Top Cities", common_cuisine_table)

    if city_col is not None and price is not None and city_counts is not None:
        price_data = df.assign(_price=price)
        top_cities = list(city_counts.head(10).index)
        price_rows = []
        for city in top_cities:
            city_data = price_data[price_data[city_col].astype(str) == str(city)]
            price_rows.append({
                "City": city,
                "Most Common Price Range": most_common_value(city_data["_price"])
            })
        common_price_table = pd.DataFrame(price_rows).set_index("City")
    else:
        common_price_table = None
    add_dataframe(lines, "Most Common Price Range in Each of the Top Cities", common_price_table)

    add_series(
        lines,
        f"Top Cities by Highly Rated Restaurant Count (Aggregate Rating > {HIGH_RATING_LIMIT})",
        high_rating_city_counts,
        10
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(lines).strip() + "\n")

    if city_counts is not None and len(city_counts) > 0:
        top_10_cities = city_counts.head(10)
        plt.figure(figsize=(10, 6))
        top_10_cities.sort_values().plot(kind="barh", color="steelblue")
        plt.title("Top 10 Cities by Restaurant Count")
        plt.xlabel("Number of Restaurants")
        plt.ylabel("City")
        plt.tight_layout()
        plt.savefig(GRAPH_FILE)
        plt.close()

    print("Analysis completed. Results saved to output.txt")
    if city_counts is not None and len(city_counts) > 0:
        print("Graph saved to location_analysis_graph.png")


if __name__ == "__main__":
    main()
