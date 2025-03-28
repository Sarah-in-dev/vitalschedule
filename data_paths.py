import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Find data paths')
    parser.add_argument('--data_dir', type=str, default='data',
                        help='Path to the data directory')
    return parser.parse_args()

args = parse_arguments()
data_dir = os.path.abspath(args.data_dir)
raw_dir = os.path.join(data_dir, 'raw', 'mimic-iv')
processed_dir = os.path.join(data_dir, 'processed', 'readmission')

print(f"Full data directory path: {data_dir}")
print(f"Raw data path: {raw_dir}")
print(f"Processed data path: {processed_dir}")

if os.path.exists(processed_dir):
    print(f"Files in processed directory:")
    for f in os.listdir(processed_dir):
        print(f"  - {f} ({os.path.getsize(os.path.join(processed_dir, f)) / (1024*1024):.2f} MB)")
