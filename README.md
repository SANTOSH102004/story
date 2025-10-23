# GPT-2 Story Generator

A minimal standalone Python project that generates short stories using the pretrained GPT-2 ("gpt2") model from Hugging Face Transformers and PyTorch.

Features:
- Loads the GPT-2 small model and tokenizer
- Sampling with temperature, top-k, and top-p (nucleus) sampling
- Command-line interface (prompt via --prompt or interactive input)
- Single-file runnable script: `generate_story.py`

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
Examples (PowerShell):

```powershell
# interactive prompt
python .\generate_story.py

# pass prompt and generation settings
python .\generate_story.py --prompt "A mysterious door appeared in the forest" --max_length 250 --top_k 40 --top_p 0.9 --temperature 1.0

# generate multiple different stories
python .\generate_story.py --prompt "On a rainy evening" -n 3 --max_length 180

GUI
---
A simple Tkinter GUI is provided in `generate_story_gui.py`. Run it with:

```powershell
python .\generate_story_gui.py
```

The GUI loads the GPT-2 model the first time you click Generate (this may take a
minute the first run). Use the sliders and inputs to adjust sampling parameters.
```

Notes
-----
- The first run will download the GPT-2 model weights from Hugging Face; this requires internet access and a few hundred MB of disk space.
- To reduce memory usage, use smaller `max_length` and set `num_return_sequences` to 1.
- The script is intentionally straightforward and commented for learning and modification.

License
-------
This project is provided under the MIT license. See `LICENSE`.
