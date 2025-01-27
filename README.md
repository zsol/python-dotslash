# `./python`

`./python` is a 2.5KB single-file CPython distribution you can check into a repository:

https://github.com/user-attachments/assets/4bd1da5b-6fd3-4cfb-968a-02213827c4b8

## Setup

1. [install dotslash](https://dotslash-cli.com/docs/installation/): `brew install dotslash` or `cargo install dotslash`
2. download one of the files from [latest
   release](https://github.com/zsol/dotslash-python/releases/latest): `curl -L https://github.com/zsol/dotslash-python/releases/latest/download/cpython-3.13 -o python`
3. run it: `chmod +x python && ./python`

## Why?

It's a really simple, cross-platform way to pin a project to a particular Python version.

## How does it work?

The files in [our releases](https://github.com/zsol/dotslash-python/releases) are
[dotslash](https://dotslash-cli.com/docs) descriptors. When executed, dotslash (via a
[shebang](<https://en.wikipedia.org/wiki/Shebang_(Unix)>) on linux/mac or a [companion
exe](https://dotslash-cli.com/docs/windows/#dotslash-windows-shim) on Windows) downloads
and extracts the right version of Python that's appropriate for your machine's
architecture, and runs the interpreter inside it.

The descriptors themselves point to the awesome [standalone Python
builds](https://github.com/astral-sh/python-build-standalone) releases, and pick the
most optimized, "[install
only](https://gregoryszorc.com/docs/python-build-standalone/main/distributions.html#install-only-archive)"
distribution for each of the supported platforms.
