from pathlib import Path


FORBIDDEN = [
    "src." + "trading",
    "src." + "web",
    "src." + "data." + "data_fetcher",
    "Alpaca" + "Manager",
    "Trade" + "Executor",
    "place" + "_order",
    "execute" + "_portfolio_rebalance",
]


def test_learning_files_do_not_reference_trading_code():
    root = Path(__file__).resolve().parents[1]
    offenders = []
    for path in list(root.rglob("*.py")) + list(root.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                offenders.append(f"{path}: {token}")
    assert offenders == []
