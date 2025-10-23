# GPT-2 Story Generator

A minimal standalone Python project that generates short stories using the pretrained GPT-2 ("gpt2") model from Hugging Face Transformers and PyTorch.

Features:
- Loads the GPT-2 small model and tokenizer
- Sampling with temperature, top-k, and top-p (nucleus) sampling
- GUI entry point via `generate_story_gui.py` (primary)
- Archived CLI available at `archive/generate_story_cli.py`

Requirements
------------
- Python 3.8+
- PyTorch
- transformers

Installation (recommended: create a virtual environment)

PowerShell commands (Windows):

```powershell
# create venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1
# upgrade pip
python -m pip install --upgrade pip
# install dependencies
pip install -r requirements.txt
```

If you have a CUDA-capable GPU and want to use it, install a suitable torch build from https://pytorch.org instead of the plain `pip install torch` that may install CPU-only PyTorch.

Usage
-----
Primary (GUI)
-------------
Run the Tkinter GUI (recommended):

```powershell
python .\generate_story_gui.py
```

The GUI loads the GPT-2 model the first time you click Generate (this may take a
minute on the first run). Use the sliders and inputs to adjust sampling parameters.

Archived CLI
------------
If you prefer the original command-line interface, it has been archived at:

```
archive/generate_story_cli.py
```
Run it the same as before (requires Python and dependencies):

```powershell
python .\archive\generate_story_cli.py --prompt "A mysterious door appeared in the forest"
```
```

Notes
-----
- The first run will download the GPT-2 model weights from Hugging Face; this requires internet access and a few hundred MB of disk space.
- To reduce memory usage, use smaller `max_length` and set `num_return_sequences` to 1.
- The script is intentionally straightforward and commented for learning and modification.

License
-------
This project is provided under the MIT license. See `LICENSE`.
