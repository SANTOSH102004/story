#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Story generator with local image generation using PIL
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from transformers import pipeline, set_seed
import torch
import random
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import textwrap
import io

class StoryGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Story Generator")
        
        # Set up the story generator
        self.generator = pipeline('text-generation', model='gpt2')
        set_seed(42)  # For reproducibility
        
        # Configure main window
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=3)  # Story area takes more space
        self.main_frame.rowconfigure(1, weight=1)     # Make input/output areas expand
        
        self.create_widgets()
        self.setup_styles()
        
    def setup_styles(self):
        # Configure styles for widgets
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        
    def create_widgets(self):
        # Create and configure widgets
        # Left column (input controls)
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky='nsew')
        
        # Genre selection
        ttk.Label(input_frame, text="Genre:").pack(pady=(0, 5), anchor='w')
        self.genre_var = tk.StringVar(value="fantasy")
        genres = ["fantasy", "sci-fi", "mystery", "romance", "horror"]
        genre_combo = ttk.Combobox(input_frame, textvariable=self.genre_var, values=genres, state='readonly')
        genre_combo.pack(fill='x', pady=(0, 10))
        
        # Length selection
        ttk.Label(input_frame, text="Story Length:").pack(pady=(0, 5), anchor='w')
        self.length_var = tk.StringVar(value="medium")
        lengths = ["short", "medium", "long"]
        length_combo = ttk.Combobox(input_frame, textvariable=self.length_var, values=lengths, state='readonly')
        length_combo.pack(fill='x', pady=(0, 10))
        
        # Theme/prompt input
        ttk.Label(input_frame, text="Theme/Prompt:").pack(pady=(0, 5), anchor='w')
        self.prompt_entry = ttk.Entry(input_frame)
        self.prompt_entry.pack(fill='x', pady=(0, 10))
        self.prompt_entry.insert(0, "A magical forest")
        
        # Generate button
        self.generate_btn = ttk.Button(input_frame, text="Generate Story", command=self.generate_story)
        self.generate_btn.pack(fill='x', pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(input_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill='x', pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(input_frame, textvariable=self.status_var, wraplength=200)
        self.status_label.pack(fill='x', pady=(0, 10))
        
        # Right side (story display and image)
        story_frame = ttk.Frame(self.main_frame)
        story_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky='nsew')
        story_frame.columnconfigure(0, weight=1)
        story_frame.rowconfigure(1, weight=1)
        
        # Story title
        self.title_var = tk.StringVar(value="Your Story Will Appear Here")
        title_label = ttk.Label(story_frame, textvariable=self.title_var, font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Image frame
        self.image_frame = ttk.Frame(story_frame)
        self.image_frame.grid(row=1, column=0, pady=(0, 10), sticky='nsew')
        
        # Image label (placeholder for now)
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(pady=(0, 10))
        
        # Story text
        self.story_text = scrolledtext.ScrolledText(story_frame, wrap=tk.WORD, width=50, height=20)
        self.story_text.grid(row=2, column=0, sticky='nsew')
        self.story_text.configure(font=('Arial', 11))
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def generate_story(self):
        # Disable the generate button
        self.generate_btn.configure(state='disabled')
        self.update_status("Generating story...")
        self.update_progress(0)
        
        # Start generation in a separate thread
        thread = threading.Thread(target=self._generate_story_thread)
        thread.daemon = True
        thread.start()
        
    def _generate_story_thread(self):
        try:
            # Clear previous story
            self.story_text.delete(1.0, tk.END)
            self.root.update_idletasks()
            
            # Get input values
            genre = self.genre_var.get()
            length = self.length_var.get()
            prompt = self.prompt_entry.get()
            
            # Determine max length based on selection
            max_length = {"short": 100, "medium": 200, "long": 300}[length]
            
            # Create story prompt
            story_prompt = f"Write a {genre} story about {prompt}. "
            
            self.update_progress(20)
            self.update_status("Generating story text...")
            
            # Generate the story
            story = self.generator(story_prompt, 
                                 max_length=max_length,
                                 num_return_sequences=1,
                                 temperature=0.7,
                                 pad_token_id=50256)[0]['generated_text']
            
            self.update_progress(60)
            self.update_status("Creating story image...")
            
            # Generate a simple image based on the prompt
            image = self.create_prompt_image(prompt)
            
            # Update the UI with the results
            self.display_results(story, image)
            
            self.update_progress(100)
            self.update_status("Story generated successfully!")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            # Re-enable the generate button
            self.generate_btn.configure(state='normal')
            
    def create_prompt_image(self, prompt, size=(400, 300)):
        """Create a simple image with the prompt text."""
        # Create a new image with a gradient background
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        for y in range(size[1]):
            r = int(255 * (1 - y/size[1]))  # Red goes from 255 to 0
            g = int(200 * (y/size[1]))      # Green goes from 0 to 200
            b = int(255 * (y/size[1]))      # Blue goes from 0 to 255
            draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        
        # Try to load a font, fall back to default if not found
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        wrapped_text = textwrap.fill(prompt, width=20)
        
        # Get text size
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate position to center text
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw text with outline for better visibility
        outline_color = 'white'
        text_color = 'black'
        
        # Draw text outline
        for adj in range(-2, 3):
            for adj2 in range(-2, 3):
                draw.text((x+adj, y+adj2), wrapped_text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), wrapped_text, font=font, fill=text_color)
        
        return image
        
    def display_results(self, story, image):
        # Update story text
        self.story_text.delete(1.0, tk.END)
        self.story_text.insert(1.0, story)
        
        # Convert PIL image to PhotoImage and display
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # Keep a reference
        
        # Update title
        words = story.split()[:5]  # Take first 5 words for title
        title = " ".join(words) + "..."
        self.title_var.set(title)

if __name__ == "__main__":
    root = tk.Tk()
    app = StoryGeneratorGUI(root)
    root.mainloop()