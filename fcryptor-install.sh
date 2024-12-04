#!/bin/bash

install_fcryptor() {
  if [[ "$(uname -s)" == "Linux" && "$(uname -m)" == "x86_64" ]]; then
    echo "Detected Linux amd64 system. Proceeding with installation..."
    
    mkdir -p ~/.local/bin
    
    wget https://github.com/BytesVault/fcryptor/releases/download/v1.0.0/fcryptor-linux-amd64 -O ~/.local/bin/fcryptor
    
    chmod +x ~/.local/bin/fcryptor
    
    echo "fcryptor installed successfully to ~/.local/bin/"
    echo "Make sure ~/.local/bin/ is in your PATH to use 'fcryptor' globally."
  else
    echo "Unsupported system. This script only supports Linux amd64 systems."
    exit 1
  fi
}

install_fcryptor
