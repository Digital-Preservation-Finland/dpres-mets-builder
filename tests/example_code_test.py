import runpy
import shutil
from pathlib import Path


def test_example_code(monkeypatch, tmpdir):
    """Test that example code runs without error."""
    # Copy doc source files to a temporary location to avoid accidentally
    # modifying the original directory if the test crashes for some reason
    doc_path = Path(tmpdir / "doc" / "source")

    doc_path.parent.mkdir(parents=True)
    shutil.copytree("doc/source", doc_path)

    monkeypatch.chdir(doc_path)
    runpy.run_path("example_code.py")

    # 'mets.xml' was created
    assert (doc_path / "mets.xml").is_file()
