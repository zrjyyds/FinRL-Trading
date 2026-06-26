from pathlib import Path

import nbformat
from nbclient import NotebookClient


def test_all_notebooks_execute_offline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("APCA_API_KEY", raising=False)
    root = Path(__file__).resolve().parents[2]
    notebooks = sorted((root / "learning" / "notebooks").glob("*.ipynb"))
    assert len(notebooks) == 8
    for path in notebooks:
        nb = nbformat.read(path, as_version=4)
        client = NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(root)}})
        client.execute()
