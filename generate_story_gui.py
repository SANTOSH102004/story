#!/usr/bin/env python3
"""
A minimal Tkinter GUI for the GPT-2 story generator.

This GUI uses the same generation logic as `generate_story.py` but provides a simple
window where users can type a prompt, adjust sampling parameters, and click Generate.

Run: python generate_story_gui.py
"""
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

# We'll replicate a minimal subset of functions from generate_story.py so this GUI is standalone.
MODEL_NAME = 'gpt2'


def load_model_and_tokenizer(device: torch.device = torch.device('cpu')):
    tokenizer = GPT2TokenizerFast.from_pretrained(MODEL_NAME)
    model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
    model.eval()
    model.to(device)
    return model, tokenizer


def generate_text(model, tokenizer, prompt, max_length, temperature, top_k, top_p, device):
    encoded = tokenizer(prompt, return_tensors='pt')
    input_ids = encoded['input_ids'].to(device)
    attention_mask = encoded.get('attention_mask')
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            do_sample=True,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k if top_k > 0 else None,
            top_p=top_p,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=attention_mask,
        )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Return the continuation (strip prompt if present)
    if text.startswith(prompt):
        return text[len(prompt):].strip()
    return text


class StoryGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('GPT-2 Story Generator')
        self.geometry('800x600')

        # Model will be loaded lazily to keep UI responsive
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        # Prompt entry
        ttk.Label(frm, text='Prompt:').grid(column=0, row=0, sticky='w')
        self.prompt_entry = ttk.Entry(frm)
        self.prompt_entry.grid(column=0, row=1, columnspan=3, sticky='ew', pady=4)
        self.prompt_entry.insert(0, 'A mysterious door appeared in the forest')

        # Max length
        ttk.Label(frm, text='Max length:').grid(column=0, row=2, sticky='w')
        self.max_length_var = tk.IntVar(value=200)
        self.max_length_spin = ttk.Spinbox(frm, from_=50, to=1024, increment=10, textvariable=self.max_length_var)
        self.max_length_spin.grid(column=0, row=3, sticky='w')

        # Temperature
        ttk.Label(frm, text='Temperature:').grid(column=1, row=2, sticky='w')
        self.temp_var = tk.DoubleVar(value=1.0)
        self.temp_scale = ttk.Scale(frm, from_=0.1, to=2.0, value=1.0, variable=self.temp_var, orient='horizontal')
        self.temp_scale.grid(column=1, row=3, sticky='ew')

        # Top-k
        ttk.Label(frm, text='Top-k:').grid(column=2, row=2, sticky='w')
        self.top_k_var = tk.IntVar(value=50)
        self.top_k_spin = ttk.Spinbox(frm, from_=0, to=500, increment=10, textvariable=self.top_k_var)
        self.top_k_spin.grid(column=2, row=3, sticky='w')

        # Top-p
        ttk.Label(frm, text='Top-p:').grid(column=3, row=2, sticky='w')
        self.top_p_var = tk.DoubleVar(value=0.95)
        self.top_p_scale = ttk.Scale(frm, from_=0.0, to=1.0, value=0.95, variable=self.top_p_var, orient='horizontal')
        self.top_p_scale.grid(column=3, row=3, sticky='ew')

        # Generate button
        self.generate_btn = ttk.Button(frm, text='Generate', command=self.on_generate)
        self.generate_btn.grid(column=0, row=4, pady=8, sticky='w')

        # Output area
        ttk.Label(frm, text='Generated story:').grid(column=0, row=5, sticky='w')
        self.output_txt = scrolledtext.ScrolledText(frm, wrap='word')
        self.output_txt.grid(column=0, row=6, columnspan=4, sticky='nsew')

        # Make grid expand
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)
        frm.columnconfigure(3, weight=1)
        frm.rowconfigure(6, weight=1)

    def on_generate(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showinfo('Missing prompt', 'Please enter a prompt to generate a story.')
            return
        try:
            max_length = int(self.max_length_var.get())
            temperature = float(self.temp_var.get())
            top_k = int(self.top_k_var.get())
            top_p = float(self.top_p_var.get())
        except Exception as e:
            messagebox.showerror('Invalid parameters', str(e))
            return

        # Load model lazily in a background thread if needed
        if self.model is None or self.tokenizer is None:
            self.generate_btn.config(state='disabled')
            threading.Thread(target=self._load_and_generate, args=(prompt, max_length, temperature, top_k, top_p), daemon=True).start()
        else:
            self.generate_btn.config(state='disabled')
            threading.Thread(target=self._generate, args=(prompt, max_length, temperature, top_k, top_p), daemon=True).start()

    def _load_and_generate(self, prompt, max_length, temperature, top_k, top_p):
        try:
            self.output_txt.insert('end', 'Loading model... this may take a while.\n')
            self.model, self.tokenizer = load_model_and_tokenizer(self.device)
            self.output_txt.insert('end', 'Model loaded. Generating...\n')
            self._generate(prompt, max_length, temperature, top_k, top_p)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load model: {e}')
            self.generate_btn.config(state='normal')

    def _generate(self, prompt, max_length, temperature, top_k, top_p):
        try:
            result = generate_text(self.model, self.tokenizer, prompt, max_length, temperature, top_k, top_p, self.device)
            self.output_txt.insert('end', f"\n---\n{prompt} {result}\n\n")
            self.output_txt.see('end')
        except Exception as e:
            messagebox.showerror('Generation error', str(e))
        finally:
            self.generate_btn.config(state='normal')


if __name__ == '__main__':
    app = StoryGUI()
    app.mainloop()
