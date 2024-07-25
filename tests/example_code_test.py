import runpy
import os


def test_example_code():
    """Test that example code runs without error."""
    os.chdir("doc/source/")
    runpy.run_path("example_code.py")
    os.chdir("../..")
    os.remove("doc/source/mets.xml")
