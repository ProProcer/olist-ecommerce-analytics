import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine
import argparse
from pathlib import Path
load_dotenv()

def export_sql_to_csv(sql_path, out_path):
    print('helol')
    DB_URL = os.getenv('DB_URL')
    engine = create_engine(DB_URL)
    query = open(sql_path).read()
    df = pd.read_sql_query(query, engine)
    df.to_csv(out_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type = str, help = 'the path to the sql query')
    parser.add_argument('-o', '--output', type = str, help = 'the output path/folder where csv file will be saved')
    args = parser.parse_args()

    out_path = Path(args.output)
    if out_path.is_dir():
        out_path = (out_path / Path(args.input).name).with_suffix('.csv')
    out_path.parent.mkdir(parents = True, exist_ok = True)
    print('helo0')

    export_sql_to_csv(sql_path = args.input, out_path = out_path)