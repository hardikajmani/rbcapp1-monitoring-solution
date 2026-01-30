# TEST3: Real Estate Price Per Square Foot Analysis

This project contains a Python script that analyzes real estate data from a CSV file and filters properties sold for less than the average price per square foot. It outputs a new CSV file with the filtered properties and prints some basic statistics.

## Script

Main script file:

- `solution.py`

The script:
- Reads a CSV file with property data.
- Computes price per square foot for each property.
- Calculates the average price per square foot (using only rows with positive square footage).
- Filters properties that are below the average price per square foot.
- Saves filtered results to a new CSV file.
- Prints a short summary and statistics.

---

## 1. Setting up a virtual environment

It is recommended to use a virtual environment so that the dependencies for this project do not interfere with other Python projects on your machine.

### 1.1 Create a virtual environment

From the project directory (where `solution.py` is located), run:

```bash
python -m venv venv
```

This creates a folder called `venv` that contains the virtual environment.

### 1.2 Activate the virtual environment

Activate it based on your operating system.

**On Windows:**

```bash
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
source venv/bin/activate
```

After activation, your terminal prompt will usually show `(venv)` at the beginning.

### 1.3 Install dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

---

## 2. Input data format

The input CSV file must contain at least the following columns:

- `price` – sale price of the property.
- `sq__ft` – square footage of the property.

Additional columns (such as `street`, `city`, etc.) are optional but can be helpful for viewing the filtered results.

---

## 3. Running the script

Make sure your virtual environment is activated and your CSV file is available.

### 3.1 Basic usage

```bash
python solution.py <input_csv>
```

Example:

```bash
python solution.py assignment-data.csv
```

This will:

- Read the CSV file.
- Compute a `price_per_sqft` column.
- Compute the average price per square foot for properties with `sq__ft` > 0.
- Select properties with `price_per_sqft` below the average.
- Save those properties to `properties_below_average_price_per_sqft.csv`.
- Print a brief overview and statistics to the terminal.

### 3.2 Custom output file name

You can provide an explicit output file name as a second argument:

```bash
python solution.py <input_csv> <output_csv>
```

Example:

```bash
python solution.py assignment-data.csv below_avg_properties.csv
```

In this case, the filtered data will be saved to `below_avg_properties.csv`.

---

## 4. Deactivating the virtual environment

When you are done working with the project, you can deactivate the virtual environment:

```bash
deactivate
```

This returns your shell to the global Python environment.
