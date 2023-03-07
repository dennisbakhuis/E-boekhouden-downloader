# E-Boekhouden - download mutaties as CSV
Simple command-line-interface (CLI) script for downloading mutaties and store it as a comma-separated-values (CSV) file.

## Create environment
Have a working (miniconda) environment and do the following:
```bash
conda create -n mutaties python=3.10
conda activate mutaties
pip install -r requirements.txt
pre-commit install
```

## Usage
Download mutaties through the CLI:
### Credentials as Environment Varialbles:
```bash
python mutaties_to_csv.py
```

### Credentials as parameters
```bash
python mutaties_to_csv.py \
  --username <your_username> \
  --security-code-1 <security_code_1> \
  --security-code-2 <security_code_2>
```

## Aditional info
Credentials can also be environment variables, these need to be stored in the following variable names:
```bash
export EBOEKHOUDEN_USERNAME="<your_username>"
export EBOEKHOUDEN_SECURITY1="<your_security_code_1>"
export EBOEKHOUDEN_SECURITY2="<your_security_code_2>"
```
