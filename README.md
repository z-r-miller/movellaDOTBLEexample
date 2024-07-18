# movellaDOTBLEexample
Python script that uses Bleak to connect with some of the Movella DOT IMU sensors without the SDK.

The src folder contains some example scripts that I wrote that use the Python library Bleak and Bluetooth LE protocol to communicate with the Movella DOT IMU. This is mainly for users who had trouble using the SDK like I did.
Included in the root directory are a .yml file and requirements.txt file to build a Python environment that matches the exact one I coded the scripts on.

## Installation

To set up the development environment for this project, you have two options: using `pip` with `requirements.txt` or using `conda` with `environment.yml`.

### Option 1: Using `requirements.txt` with pip

1. **Create and activate a virtual environment (optional but recommended)**
```bash
python -m venv myenv
myenv\Scripts\activate
```
2. ** Install required packages
```bash
pip install -r requirements.txt
```

### Option 2: Using environment.yml with conda

1. ** Create conda environment
```conda
conda env create -f movDOTbt.yml
```

2. ** Activate the conda environment
```conda
conda activate movDOTbt
```

## Running Scripts
- I ran everything in VS Code with Python 3.12.4

## Notes
- The MAC addresses in all of the src scripts are my sensors addresses. They will need to be changed with whatever your sensors' addresses are.
- Read referenced.md in docs to find where to Download Movella's documentation for the Movella DOTs so that you can edit the scripts as needed.
- Whenever you change the modes on each sensor, what measurement you are recording, the sensor needs to be fully turned off and on again to properly change the measurement type being printed.
- mDOTbt1.py has commented sections explaining specific lines explaining certain Bluetooth LE elements and how to change them for your needs.
