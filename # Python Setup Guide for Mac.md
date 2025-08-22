# Python Setup Guide for Mac

## 1. Install Python

Most Macs come with Python pre-installed. To install the latest version:

```bash
brew install python
```
*Requires [Homebrew](https://brew.sh/).*

Check Python version:
```bash
python3 --version
```
If you see a version number (e.g., `Python 3.11.5`), Python is installed.

## 2. Create a Virtual Environment

Navigate to your project folder:
```bash
cd /path/to/your/project
```

Create a virtual environment named `myenv`:
```bash
python3 -m venv myenv
```
This creates a folder called `myenv` containing a clean Python installation.

## 3. Activate the Virtual Environment

Activate using:
```bash
source myenv/bin/activate
```
You should see `(myenv)` in your terminal prompt.  
Now, any Python or pip command will use the environment’s isolated packages.

## 4. Install Requirements from requirements.txt

Make sure your `requirements.txt` file is in the project folder. Then run:
```bash
pip install -r requirements.txt
```
This installs all dependencies listed in the file.  
If you add new packages, use `pip install package-name` and then run `pip freeze > requirements.txt` to update the file.

## 5. Deactivate the Environment

When done, deactivate with:
```bash
deactivate
```
This returns your shell to the global Python environment.

---

**Explanation:**
- **Virtual environments** isolate project dependencies, preventing conflicts between projects.
- **requirements.txt** lists packages your project needs for easy setup and sharing.
- Activating the environment ensures you use the correct Python and pip.
- Deactivating returns you to your system’s default Python setup.
- Use `which python` and `which pip` to confirm you’re using the environment’s