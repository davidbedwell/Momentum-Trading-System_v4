"""Frozen corrected engine imported by absolute dependency location; no detector edits."""
import importlib.util
from pathlib import Path
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_corrected',O.parent/'iteration8_four_arm/corrected/engine.py')
z=importlib.util.module_from_spec(spec);spec.loader.exec_module(z)
x=z.x;e=z.e;configure=z.configure;fit=z.fit;states=z.states;B=z.B;CUSUM=z.CUSUM;C_ablation=z.C_ablation;contrast=z.contrast;fit_v3=z.fit_v3
