import hashlib
import os
import sqlite3
import sys
import time
from argparse import ArgumentParser
from getpass import getpass
from multiprocessing import Pool, cpu_count
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

CHUNK_SIZE = 1024 * 1024 * 256


def get_key_iv(key_str):
    key = hashlib.sha256(key_str.encode()).digest()
    iv = os.urandom(16)
    return key, iv


def encrypt_chunk(args):
    key, iv, chunk_index, chunk = args
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_chunk = padder.update(chunk) + padder.finalize()
    encrypted_chunk = encryptor.update(padded_chunk) + encryptor.finalize()
    return chunk_index, encrypted_chunk


def decrypt_chunk(args):
    key, iv, chunk_index, chunk = args
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    padded_chunk = decryptor.update(chunk) + decryptor.finalize()
    decrypted_chunk = unpadder.update(padded_chunk) + unpadder.finalize()
    return chunk_index, decrypted_chunk


def process_file_encrypt(file_path, key, iv):
    file_size = os.path.getsize(file_path)
    tasks = []

    with open(file_path, "rb") as f:
        for chunk_index in range((file_size + CHUNK_SIZE - 1) // CHUNK_SIZE):
            chunk = f.read(CHUNK_SIZE)
            tasks.append((key, iv, chunk_index, chunk))

    with Pool(cpu_count() * 2) as pool:
        encrypted_chunks = pool.map(encrypt_chunk, tasks)

    return file_path, encrypted_chunks, file_size


def process_file_decrypt(file_path, key, iv, chunks):
    tasks = [(key, iv, chunk_index, chunk) for chunk_index, chunk in chunks]

    with Pool(cpu_count() * 2) as pool:
        decrypted_chunks = pool.map(decrypt_chunk, tasks)

    with open(file_path, "wb") as f:
        for _, chunk in sorted(decrypted_chunks):
            f.write(chunk)


def encrypt_directory(directory, db_path, key):
    key, iv = get_key_iv(key)
    total_size = 0
    start_time = time.time()

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT,
            chunk_index INTEGER,
            data BLOB
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            iv BLOB
        )
        """)
        conn.commit()
        conn.execute("INSERT INTO metadata (iv) VALUES (?)", (iv,))

        files = list(Path(directory).rglob("*") if Path(directory).is_dir() else [Path(directory)])
        for file in files:
            if file.is_file():
                print(f"Encrypting: {file}")
                file_path, chunks, file_size = process_file_encrypt(str(file), key, iv)
                total_size += file_size
                for chunk_index, data in chunks:
                    conn.execute(
                        "INSERT INTO files (original_path, chunk_index, data) VALUES (?, ?, ?)",
                        (file_path, chunk_index, data)
                    )
        conn.commit()

    elapsed_time = time.time() - start_time
    print(f"Encryption completed: {total_size / (1024 * 1024):.2f} MB processed in {elapsed_time:.2f} seconds")


def decrypt_directory(db_path, output_dir, key):
    key = hashlib.sha256(key.encode()).digest()
    start_time = time.time()
    total_size = 0

    with sqlite3.connect(db_path) as conn:
        iv = conn.execute("SELECT iv FROM metadata").fetchone()[0]
        records = conn.execute("SELECT original_path, chunk_index, data FROM files").fetchall()

        files = {}
        for original_path, chunk_index, data in records:
            if original_path not in files:
                files[original_path] = []
            files[original_path].append((chunk_index, data))

        output_dir = Path(output_dir)
        for file_path, chunks in files.items():
            print(f"Decrypting: {file_path}")
            relative_path = Path(file_path).relative_to(Path(file_path).anchor)
            output_file = output_dir / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            total_size += sum(len(chunk[1]) for chunk in chunks)
            process_file_decrypt(str(output_file), key, iv, chunks)

    elapsed_time = time.time() - start_time
    print(f"Decryption completed: {total_size / (1024 * 1024):.2f} MB processed in {elapsed_time:.2f} seconds")


def main():
    parser = ArgumentParser(description="Encrypt or decrypt files and directories.")
    parser.add_argument("-e", "--encrypt", help="Encrypt a file or directory.", action="store_true")
    parser.add_argument("-d", "--decrypt", help="Decrypt a database.", action="store_true")
    parser.add_argument("--file", help="File to process.")
    parser.add_argument("-r", "--directory", help="Directory to process.")
    parser.add_argument("--key", help="Encryption/Decryption key.")

    args = parser.parse_args()
    key = args.key or getpass("Enter encryption/decryption key: ")

    if args.encrypt:
        if args.file:
            output = f"{Path(args.file).name}.fc"
        elif args.directory:
            output = f"{Path(args.directory).name}.fc"
        else:
            print("Error: Please provide a file or directory for encryption.")
            sys.exit(1)
    elif args.decrypt:
        output = None
    else:
        print("Error: Please specify --encrypt or --decrypt.")
        sys.exit(1)

    if args.encrypt and (args.file or args.directory):
        encrypt_directory(args.file or args.directory, output, key)
    elif args.decrypt:
        if not args.file:
            print("Error: Please provide a .fc file for decryption.")
            sys.exit(1)
        decrypt_directory(args.file, os.getcwd(), key)
    else:
        print("Invalid arguments. Use -h for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
