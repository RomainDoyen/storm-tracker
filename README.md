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

3. Set the environment variables in a `.env` file

```bash
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_key>
```

3. Run the application

```bash
cd storm-tracker
```

```bash	
python run.py
```

## Usage

The application will be running on [http://127.0.0.1:7000/](http://127.0.0.1:7000/)

