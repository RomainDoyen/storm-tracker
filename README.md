# Storm tracker

This is a simple web application that tracks storms in real-time. It uses the [Tropycal API](https://tropycal.github.io/tropycal/index.html) to get the data.

## Installation

1. Clone the repository

```bash
git clone https://github.com/RomainDoyen/storm-tracker.git
```

2. Install the dependencies

```bash
pip install -r requirements.txt
```

3. Create table in Supabase

```sql
CREATE TABLE Cyclones (
  id VARCHAR(50) PRIMARY KEY,
  idCyclone VARCHAR(50),
  name VARCHAR(100),
  vmax NUMERIC,
  mslp NUMERIC,
  lat NUMERIC,
  lon NUMERIC,
  classification VARCHAR(50)
);
```

4. Set the environment variables in a `.env` file

5. Run the application

```bash
cd storm-tracker
```

```bash	
python run.py
```

## Usage

The application will be running on [http://127.0.0.1:7000/](http://127.0.0.1:7000/)

