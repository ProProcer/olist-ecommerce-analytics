# python scripts/split_dataset.py --csv_path data/processed/order_delivery_dataset.csv --datetime_column order_approved_at --cutoff_date 01-01-2018 --name handling_days
import argparse
import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_path', help = 'path of the dataset')
    parser.add_argument('--datetime_column', help = 'name of the datetime column')
    parser.add_argument('--cutoff_date', help = 'cutoff date to split training and testing')
    parser.add_argument('--name', help = 'name of the dataset')
    args = parser.parse_args()

    df = pd.read_csv(args.csv_path)
    df[args.datetime_column] = pd.to_datetime(df[args.datetime_column])

    df_train = df[df[args.datetime_column] < args.cutoff_date]
    df_test = df[df[args.datetime_column] >= args.cutoff_date]
    df_train.to_csv(f"data/processed/{args.name}_train.csv", index = False)
    df_test.to_csv(f"data/processed/{args.name}_test.csv", index = False)