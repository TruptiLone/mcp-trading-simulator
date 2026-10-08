"""Validate and execute local notebook cells; never run cells tagged live."""
from pathlib import Path
import ast
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
ROOT = Path(__file__).resolve().parents[1]
for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"{path.name}:{index}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    NotebookClient(notebook, km=manager, timeout=120, skip_cells_with_tag="live", resources={"metadata": {"path": str(ROOT)}}).execute()
    nbformat.write(notebook, path)
    print("PASS", path.name, flush=True)
