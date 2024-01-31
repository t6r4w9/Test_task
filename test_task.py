import os
import shutil
import hashlib
import logging
import time
import argparse

def setup_logger(log_file):
    # Set up logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_file_hash(file_path):
    # Generate a hash for the given file using the specified algorithm
    hash_func = hashlib.new("sha256")
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def synchronize_folders(original_path, copy_path, logger):
    # List files in original directory + attributes
    original_files = {entry.name: entry.stat() for entry in os.scandir(original_path) if entry.is_file()}

    # List files in copy directory + attributes
    copy_files = {entry.name: entry.stat() for entry in os.scandir(copy_path) if entry.is_file()}

    # Compare and take actions
    for file_name, original_stats in original_files.items():
        copy_stats = copy_files.get(file_name)

        if not copy_stats or copy_stats.st_mtime != original_stats.st_mtime:
            source_file_path = os.path.join(original_path, file_name)
            destination_file_path = os.path.join(copy_path, file_name)
            shutil.copy2(source_file_path, destination_file_path)
            logger.info(f"Copied {file_name} to {copy_path}")
            print(f"Copied {file_name} to {copy_path}")
        else:
            original_hash = generate_file_hash(os.path.join(original_path, file_name))
            copy_hash = generate_file_hash(os.path.join(copy_path, file_name))
            if original_hash != copy_hash:
                source_file_path = os.path.join(original_path, file_name)
                destination_file_path = os.path.join(copy_path, file_name)
                shutil.copy2(source_file_path, destination_file_path)
                logger.info(f"Copied {file_name} to {copy_path} (content updated)")
                print(f"Copied {file_name} to {copy_path} (content updated)")

    for file_name, copy_stats in copy_files.items():
        if file_name not in original_files:
            file_path = os.path.join(copy_path, file_name)
            os.remove(file_path)
            logger.info(f"Removed {file_name} from {copy_path}")
            print(f"Removed {file_name} from {copy_path}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Periodically synchronize folders")
    parser.add_argument("original_path", help="Path to the original folder")
    parser.add_argument("copy_path", help="Path to the copy folder")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    original_path = args.original_path
    copy_path = args.copy_path
    sync_interval = args.sync_interval
    log_file = args.log_file

    # Set up logging
    setup_logger(log_file)
    logger = logging.getLogger()

    # Run the synchronization loop with the specified interval
    while True:
        synchronize_folders(original_path, copy_path, logger)
        time.sleep(sync_interval)

if __name__ == "__main__":
    main()
