# D-D-Voice-Assisstant
A voice-powered D&amp;D assistant that detects game content and dynamically adapts music to the current scene.

## Development Setup

### 1. Clone the repository or use Github Desktop (it's easier)
```powershell
git clone <repository-url>
cd D-D-Voice-Assisstant
```

### 2. Create a virtual environment
```powershell
python -m venv .venv
```

### 3. Activate the virtual environment in the D-D-Voice-Assisstant folder
**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

The terminal should now show `(.venv)` at the beginning:
```text
(.venv) PS C:\...\D-D-Voice-Assisstant>
```

### 4. Install dependencies
Install all required Python packages using:
```powershell
python -m pip install -r requirements.txt
```

Do not install the packages individually unless adding a new dependency to the project.
### 5. Run the program
From the project root:
```powershell
python main.py
```
### Adding New Dependencies
If you install a new Python package while working on the project, update `requirements.txt`:
```powershell
pip freeze > requirements.txt
```

Commit the updated `requirements.txt` alongside your changes.
### Important
* Do **not** commit the `.venv` folder.
* Always activate `.venv` before running or developing the Python backend.
* Make sure VS Code is using `.venv\Scripts\python.exe` as the Python interpreter.
* Run `main.py` from the project root rather than from inside `src`.
