from flask import Flask, render_template, request, redirect, url_for, flash
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Base directory for file explorer (workspace folder)
BASE_DIR = Path(__file__).parent / "workspace"
BASE_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------
# Task 1: Import Modules
# ------------------------------------------------------
# Already imported above


# ------------------------------------------------------
# Utility: Check if path is safe
# ------------------------------------------------------
def is_safe_path(path):
    """Prevent directory traversal outside BASE_DIR"""
    try:
        resolved = Path(path).resolve()
        return resolved.is_relative_to(BASE_DIR)
    except:
        return False


# ------------------------------------------------------
# Utility: Format file size
# ------------------------------------------------------
def format_size(size_bytes):
    """Convert bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


# ------------------------------------------------------
# Task 2: Handle the Root Route
# ------------------------------------------------------
@app.route("/")
def index():
    current_dir = request.args.get("dir", "")
    full_path = BASE_DIR / current_dir

    if not is_safe_path(full_path):
        flash("Access denied to this directory.", "danger")
        return redirect(url_for("index"))

    if not full_path.exists() or not full_path.is_dir():
        flash("Directory does not exist.", "danger")
        return redirect(url_for("index"))

    items = []
    for item in full_path.iterdir():
        item_info = {
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": format_size(item.stat().st_size) if item.is_file() else "-",
            "path": str(item.relative_to(BASE_DIR))
        }
        items.append(item_info)

    # Sort: directories first, then files
    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

    breadcrumbs = []
    parts = Path(current_dir).parts
    cumulative = ""
    for part in parts:
        cumulative = str(Path(cumulative) / part)
        breadcrumbs.append({"name": part, "path": cumulative})

    return render_template(
        "index.html",
        items=items,
        current_dir=current_dir,
        breadcrumbs=breadcrumbs
    )


# ------------------------------------------------------
# Task 4: Handle the Change Directory Route
# ------------------------------------------------------
@app.route("/change_dir")
def change_dir():
    target_dir = request.args.get("dir", "")
    return redirect(url_for("index", dir=target_dir))


# ------------------------------------------------------
# Task 5: Handle the Make Directory Route
# ------------------------------------------------------
@app.route("/make_dir", methods=["POST"])
def make_dir():
    current_dir = request.form.get("current_dir", "")
    dir_name = request.form.get("dir_name", "").strip()

    if not dir_name:
        flash("Directory name cannot be empty.", "danger")
        return redirect(url_for("index", dir=current_dir))

    full_path = BASE_DIR / current_dir / dir_name

    if not is_safe_path(full_path):
        flash("Invalid directory path.", "danger")
        return redirect(url_for("index", dir=current_dir))

    if full_path.exists():
        flash("Directory already exists.", "warning")
        return redirect(url_for("index", dir=current_dir))

    try:
        full_path.mkdir(parents=True)
        flash(f"Directory '{dir_name}' created successfully.", "success")
    except Exception as e:
        flash(f"Error creating directory: {e}", "danger")

    return redirect(url_for("index", dir=current_dir))


# ------------------------------------------------------
# Task 6: Handle the Remove Directory Route
# ------------------------------------------------------
@app.route("/remove_dir", methods=["POST"])
def remove_dir():
    current_dir = request.form.get("current_dir", "")
    dir_path = request.form.get("dir_path", "")

    full_path = BASE_DIR / dir_path

    if not is_safe_path(full_path):
        flash("Invalid directory path.", "danger")
        return redirect(url_for("index", dir=current_dir))

    if not full_path.exists() or not full_path.is_dir():
        flash("Directory does not exist.", "danger")
        return redirect(url_for("index", dir=current_dir))

    try:
        full_path.rmdir()
        flash(f"Directory '{full_path.name}' removed successfully.", "success")
    except OSError:
        flash("Directory is not empty or cannot be removed.", "danger")
    except Exception as e:
        flash(f"Error removing directory: {e}", "danger")

    return redirect(url_for("index", dir=current_dir))


# ------------------------------------------------------
# Task 7: Handle the Make File Functionality
# ------------------------------------------------------
@app.route("/make_file", methods=["POST"])
def make_file():
    current_dir = request.form.get("current_dir", "")
    file_name = request.form.get("file_name", "").strip()

    if not file_name:
        flash("File name cannot be empty.", "danger")
        return redirect(url_for("index", dir=current_dir))

    full_path = BASE_DIR / current_dir / file_name

    if not is_safe_path(full_path):
        flash("Invalid file path.", "danger")
        return redirect(url_for("index", dir=current_dir))

    if full_path.exists():
        flash("File already exists.", "warning")
        return redirect(url_for("index", dir=current_dir))

    try:
        full_path.touch()
        flash(f"File '{file_name}' created successfully.", "success")
    except Exception as e:
        flash(f"Error creating file: {e}", "danger")

    return redirect(url_for("index", dir=current_dir))


# ------------------------------------------------------
# Task 8: Handle the Remove File Functionality
# ------------------------------------------------------
@app.route("/remove_file", methods=["POST"])
def remove_file():
    current_dir = request.form.get("current_dir", "")
    file_path = request.form.get("file_path", "")

    full_path = BASE_DIR / file_path

    if not is_safe_path(full_path):
        flash("Invalid file path.", "danger")
        return redirect(url_for("index", dir=current_dir))

    if not full_path.exists() or not full_path.is_file():
        flash("File does not exist.", "danger")
        return redirect(url_for("index", dir=current_dir))

    try:
        full_path.unlink()
        flash(f"File '{full_path.name}' removed successfully.", "success")
    except Exception as e:
        flash(f"Error removing file: {e}", "danger")

    return redirect(url_for("index", dir=current_dir))


# ------------------------------------------------------
# Task 9: Handle the View File Functionality
# ------------------------------------------------------
@app.route("/view_file")
def view_file():
    current_dir = request.args.get("current_dir", "")
    file_path = request.args.get("file_path", "")

    full_path = BASE_DIR / file_path

    if not is_safe_path(full_path):
        flash("Invalid file path.", "danger")
        return redirect(url_for("index", dir=current_dir))

    if not full_path.exists() or not full_path.is_file():
        flash("File does not exist.", "danger")
        return redirect(url_for("index", dir=current_dir))

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        flash(f"Error reading file: {e}", "danger")
        return redirect(url_for("index", dir=current_dir))

    return render_template(
        "view_file.html",
        file_name=full_path.name,
        file_path=file_path,
        content=content,
        current_dir=current_dir
    )


# ------------------------------------------------------
# Task 10: Handle the Write File Functionality
# ------------------------------------------------------
@app.route("/write_file", methods=["POST"])
def write_file():
    current_dir = request.form.get("current_dir", "")
    file_path = request.form.get("file_path", "")
    content = request.form.get("content", "")

    full_path = BASE_DIR / file_path

    if not is_safe_path(full_path):
        flash("Invalid file path.", "danger")
        return redirect(url_for("index", dir=current_dir))

    if not full_path.exists() or not full_path.is_file():
        flash("File does not exist.", "danger")
        return redirect(url_for("index", dir=current_dir))

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        flash(f"File '{full_path.name}' saved successfully.", "success")
    except Exception as e:
        flash(f"Error writing file: {e}", "danger")

    return redirect(url_for("view_file", file_path=file_path, current_dir=current_dir))


# ------------------------------------------------------
# Task 3: Render the Root Route (already handled above in index)
# ------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)