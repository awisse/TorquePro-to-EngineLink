# TorquePro-to-EngineLink

This program transforms TorquePro files from the project [OBD-PIDs-for-HKMC-EVs](https://github.com/JejuSoul/OBD-PIDs-for-HKMC-EVs) to files
readable by the [EngineLink](http://outdoor-apps.com/enginelink.html) app on iOS.

## Installation
1. `tp2el.py` must be in the `$PATH`.
2. `tp_to_el.py` must be in the `$PYTHONPATH`.

### Other option
`tp2el.py` and `tp_to_el.py` in the same directory and execute `tp2el.py` from that directory.

## Usage
The program accepts a `<name>.csv` file in TorquePro format. The result is saved in the file `<name>-EL.csv` in the directory
specified in the option `--target-dir`. The default for `--target-dir` is the current directory.

`tp2el.py <name>.csv`

## Note
This is a small program without packaging. It is probably not worthwile to install it in site-packages. I might add packaging in the future if there is an interest.
