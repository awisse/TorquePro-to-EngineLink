# TorquePro-to-EngineLink

This program transforms TorquePro files from the project [OBD-PIDs-for-HKMC-EVs](https://github.com/JejuSoul/OBD-PIDs-for-HKMC-EVs) to files
readable by the [EngineLink](http://outdoor-apps.com/enginelink.html) app on iOS.

## Installation
1. `tp2el.py` must be in the `$PYTHONPATH`.
2. `tp-to-el.py` must be in the `$PATH`.

## Usage
The program accepts a `<name>.csv` file in TorquePro format. The result is saved in the file `<name>-EL.csv` in the directory
specified in the option `--target-dir`. The default for `--target-dir` is the current directory.

`tp-2-el.py <name>.csv`
