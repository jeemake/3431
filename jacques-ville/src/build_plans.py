"""Compatibility entry point for the current Capitude revision."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_capitude.py')),run_name='__main__')
