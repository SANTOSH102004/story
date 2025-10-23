#!/usr/bin/env python3
"""
Archived CLI: original generate_story.py
"""

# The original CLI file has been archived here. See the repository root for the
# GUI `generate_story_gui.py` which is the primary entry point.

# For convenience, we include the implementation below.

from typing import Optional, List
import argparse
import textwrap

import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast


def load_model(device: torch.device = torch.device('cpu')):
    model_name = 'gpt2'
    print(f"Loading model '{model_name}'... this may take a moment")
    tokenizer = GPT2TokenizerFast.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    model.eval()
    model.to(device)
    return model, tokenizer


def generate_story(
    model: GPT2LMHeadModel,
    tokenizer: GPT2TokenizerFast,
    prompt: str,
    max_length: int = 200,
    temperature: float = 1.0,
    top_k: int = 50,
    top_p: float = 0.95,
    num_return_sequences: int = 1,
    device: torch.device = torch.device('cpu'),
) -> List[str]:
    encoded = tokenizer(prompt, return_tensors='pt')
    input_ids = encoded['input_ids'].to(device)
    attention_mask = encoded.get('attention_mask')
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    with torch.no_grad():
        gen_kwargs = dict(
            do_sample=True,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k if top_k > 0 else None,
            top_p=top_p,
            num_return_sequences=num_return_sequences,
            pad_token_id=tokenizer.eos_token_id,
        )
        if attention_mask is not None:
            gen_kwargs['attention_mask'] = attention_mask
        outputs = model.generate(input_ids, **gen_kwargs)

    results = []
    for output_ids in outputs:
        text = tokenizer.decode(output_ids, skip_special_tokens=True)
        if text.startswith(prompt):
            cont = text[len(prompt):].strip()
        else:
            cont = text
        results.append(cont)
    return results


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description='Simple GPT-2 story generator (top-k / top-p sampling)'
    )
    p.add_argument('--prompt', '-p', type=str, default=None, help='Story prompt. If not provided, the script will ask interactively.')
    p.add_argument('--max_length', '-m', type=int, default=200, help='Maximum total token length for generation (including prompt).')
    p.add_argument('--temperature', '-t', type=float, default=1.0, help='Sampling temperature; higher = more random.')
    p.add_argument('--top_k', type=int, default=50, help='Top-k sampling parameter (0 to disable).')
    p.add_argument('--top_p', type=float, default=0.95, help='Top-p (nucleus) sampling parameter.')
    p.add_argument('--num_return_sequences', '-n', type=int, default=1, help='Number of stories to generate.')
    p.add_argument('--device', '-d', type=str, default=None, help='Device to use: cpu or cuda. Default: auto-detect.')
    return p


def main(argv: Optional[list[str]] = None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.device:
        device = torch.device(args.device)
    else:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    prompt = args.prompt
    if not prompt:
        try:
            prompt = input('Enter a story prompt: ').strip()
        except EOFError:
            print('\nNo prompt provided. Exiting.')
            return
    if not prompt:
        print('Empty prompt, exiting.')
        return

    model, tokenizer = load_model(device)

    print('\nGenerating...\n')
    stories = generate_story(
        model,
        tokenizer,
        prompt,
        max_length=args.max_length,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        num_return_sequences=args.num_return_sequences,
        device=device,
    )

    for i, s in enumerate(stories, start=1):
        print('---')
        print(f'Story #{i}:')
        print(textwrap.fill(prompt + ' ' + s, width=80))
        print('\n')


if __name__ == '__main__':
    main()
