import subprocess

proc = subprocess.Popen(
    'start cmd /k "python main.py"',
    creationflags=subprocess.CREATE_NO_WINDOW,
    shell=True
)