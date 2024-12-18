# fcryptor

fcryptor is a command-line utility for encrypting and decrypting files and directories using AES-256 encryption. It ensures data confidentiality by encrypting file contents into a secure SQLite database. The utility is designed for performance and scalability, leveraging multiprocessing to handle large files efficiently.


## Installation

```bash
curl -sSL https://raw.githubusercontent.com/BytesVault/fcryptor/refs/heads/master/fcryptor-install.sh | sh -
```


## Features

- **AES-256 Encryption**: Secure encryption with randomly generated IVs for every operation.
- **Chunked Processing**: Handles large files efficiently by splitting them into chunks.
- **SQLite Storage**: Stores encrypted data in a database for ease of management.
- **Parallel Processing**: Utilizes multiple CPU cores for encryption and decryption tasks.
- **File and Directory Support**: Encrypt or decrypt individual files or entire directories.
- **Metadata Preservation**: Maintains file structure during decryption.

## Usage

### Encrypt Files or Directories

Encrypt a file or directory into a secure `.fc` database:

```bash
fcryptor --encrypt --file <file_path> --key <encryption_key>
```

```bash
fcryptor --encrypt --directory <directory_path> --key <encryption_key>
```

If the `--key` option is not provided, the utility will prompt you to enter the encryption key interactively.

### Decrypt Encrypted Data

Decrypt an `.fc` database to restore the original files or directories:

```bash
fcryptor --decrypt --file <encrypted_database_path> --key <decryption_key>
```

The decrypted files will be restored to the current working directory.

### Additional Options

- `--key`: Specify the encryption or decryption key. If omitted, the utility will prompt for it interactively.
- `--file`: Specify the file to encrypt or decrypt.
- `--directory`: Specify the directory to encrypt. This option is not used during decryption.

## Examples

### Encrypt a File

```bash
fcryptor --encrypt --file my_document.txt --key MySecureKey
```

This command will create an encrypted `.fc` file containing the encrypted contents of `my_document.txt`.

### Encrypt a Directory

```bash
fcryptor --encrypt --directory my_folder --key MySecureKey
```

This command will create an encrypted `.fc` file containing the encrypted contents of all files within `my_folder`.

### Decrypt a File

```bash
fcryptor --decrypt --file my_folder.fc --key MySecureKey
```

This command will restore the original files from the `my_folder.fc` database.

## Requirements

- Python 3.6+
- cryptography library
- sqlite3 library (included in Python)

## License

fcryptor is open-source software licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Disclaimer

This utility is provided "as-is" without warranty of any kind. Use at your own risk. Always back up your data before encryption.
