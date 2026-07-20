#!/bin/bash

set -e

# Where we install local libs
LOCAL_PREFIX="$HOME/.local"
SRC_DIR="$HOME/src"

mkdir -p "$SRC_DIR"
mkdir -p "$LOCAL_PREFIX"

# Check and install libffi
if [ ! -f "$LOCAL_PREFIX/lib/libffi.so" ]; then
    echo "libffi not found, building..."
    cd "$SRC_DIR"
    wget -nc https://github.com/libffi/libffi/releases/download/v3.4.5/libffi-3.4.5.tar.gz
    tar -xzf libffi-3.4.5.tar.gz
    cd libffi-3.4.5
    ./configure --prefix="$LOCAL_PREFIX"
    make -j$(nproc)
    make install
else
    echo "libffi already installed."
fi

# Check and install readline
if [ ! -f "$LOCAL_PREFIX/lib/libreadline.so" ]; then
    echo "readline not found, building..."
    cd "$SRC_DIR"
    wget -nc https://ftp.gnu.org/gnu/readline/readline-8.2.tar.gz
    tar -xzf readline-8.2.tar.gz
    cd readline-8.2
    ./configure --prefix="$LOCAL_PREFIX"
    make -j$(nproc)
    make install
else
    echo "readline already installed."
fi

# Check and install xz (liblzma)
if [ ! -f "$LOCAL_PREFIX/lib/liblzma.so" ]; then
    echo "liblzma not found, building..."

    cd "$SRC_DIR"
    wget -nc https://tukaani.org/xz/xz-5.4.6.tar.gz
    tar -xzf xz-5.4.6.tar.gz
    cd xz-5.4.6

    ./configure --prefix="$LOCAL_PREFIX"
    make -j$(nproc)
    make install
else
    echo "liblzma already installed."
fi

# Set environment variables for pyenv build
export PKG_CONFIG_PATH="$LOCAL_PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
export CPPFLAGS="-I$LOCAL_PREFIX/include $CPPFLAGS"
export LDFLAGS="-L$LOCAL_PREFIX/lib $LDFLAGS"
export LD_LIBRARY_PATH="$LOCAL_PREFIX/lib:$LD_LIBRARY_PATH"
export PYTHON_CONFIGURE_OPTS="--with-system-ffi"

# Reinstall Python
PYTHON_VERSION="3.11.10"
pyenv uninstall -f $PYTHON_VERSION
pyenv install $PYTHON_VERSION

echo "Python $PYTHON_VERSION installed with libffi and readline."
