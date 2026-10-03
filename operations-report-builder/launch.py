"""Launch from any folder: python3 /path/to/launch.py"""
from pathlib import Path
import os
import subprocess
import sys
import venv

root=Path(__file__).resolve().parent
env=root/'.venv'
python=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not python.exists():
    print('Creating the app environment…',flush=True)
    venv.create(env,with_pip=True)
print('Checking app dependencies…',flush=True)
subprocess.run([str(python),'-m','pip','install','-r',str(root/'requirements.txt')],cwd=root,check=True)
print('Starting Viv’s Operations Report Builder. Keep this window open.',flush=True)
try:
    subprocess.run([str(python),'-m','streamlit','run',str(root/'app.py')],cwd=root,check=True)
except KeyboardInterrupt:
    print('\nApp stopped.')
