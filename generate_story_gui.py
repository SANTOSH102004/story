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
        self.root.geometry("1400x900")
        self.root.configure(bg='#2E3440')  # Nordic dark theme background
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=4)  # Give more space to story area
        self.main_frame.rowconfigure(1, weight=1)
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        # Configure styles for widgets using a modern dark theme
        style = ttk.Style()
        
        # Configure colors
        bg_color = '#2E3440'      # Dark background
        fg_color = '#ECEFF4'      # Light text
        accent_color = '#88C0D0'  # Nordic blue
        card_bg = '#3B4252'       # Slightly lighter background for cards
        muted_text = '#D8DEE9'    # Muted text color
        border_color = '#434C5E'  # Border color for cards
        
        # Frame styles
        style.configure('TFrame', background=bg_color)
        
        style.configure('Card.TFrame',
                       background=card_bg,
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Input.TFrame',
                       background=card_bg,
                       relief='flat')
        
        # Label styles
        style.configure('TLabel', 
                       background=bg_color, 
                       foreground=fg_color, 
                       font=('Segoe UI', 11))
        
        style.configure('Title.TLabel',
                       background=bg_color,
                       foreground=accent_color,
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Header.TLabel',
                       background=card_bg,
                       foreground=fg_color,
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Description.TLabel',
                       background=card_bg,
                       foreground=muted_text,
                       font=('Segoe UI', 9, 'italic'))
        
        # Statistics label style
        style.configure('Stat.TLabel',
                       background=card_bg,
                       foreground=accent_color,
                       font=('Segoe UI', 9, 'bold'))
        
        # Button styles
        style.configure('TButton', 
                       font=('Segoe UI', 12, 'bold'),
                       padding=15,
                       background=accent_color,
                       foreground=bg_color)
        
        style.map('TButton',
                 background=[('active', '#8FBCBB'), ('disabled', '#4C566A')],
                 foreground=[('disabled', muted_text)])
        
        # Combobox styles
        style.configure('TCombobox', 
                       padding=10,
                       foreground=fg_color,
                       fieldbackground=bg_color,
                       background=accent_color,
                       arrowcolor=fg_color,
                       font=('Segoe UI', 11))
        
        # Enhanced dropdown style
        style.configure('Dropdown.TCombobox',
                       padding=12,
                       foreground=fg_color,
                       fieldbackground=card_bg,
                       background=accent_color,
                       arrowcolor=accent_color,
                       font=('Segoe UI', 11))
        
        # Combobox mapping for hover and selection effects
        style.map('TCombobox',
                 fieldbackground=[('readonly', card_bg), ('active', card_bg)],
                 selectbackground=[('readonly', accent_color)],
                 selectforeground=[('readonly', bg_color)])
        
        style.map('Dropdown.TCombobox',
                 fieldbackground=[('readonly', card_bg), 
                                ('active', card_bg),
                                ('focus', card_bg)],
                 selectbackground=[('readonly', accent_color)],
                 selectforeground=[('readonly', bg_color)],
                 bordercolor=[('focus', accent_color)])
        
        # Entry styles
        style.configure('TEntry', 
                       fieldbackground=bg_color,
                       foreground=fg_color,
                       padding=10,
                       font=('Segoe UI', 11))
        
        style.map('TEntry',
                 fieldbackground=[('focus', '#434C5E')],
                 bordercolor=[('focus', accent_color)])
        
        # Progressbar styles
        style.configure('Horizontal.TProgressbar',
                       background=accent_color,
                       troughcolor=bg_color,
                       bordercolor=border_color,
                       lightcolor=accent_color,
                       darkcolor=accent_color)
        
    def create_widgets(self):
        # Left column (input controls)
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20, sticky='nsew')
        
        # Title for input section with icon
        title_frame = ttk.Frame(input_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        input_title = ttk.Label(title_frame, text="✨ Story Creator", style='Title.TLabel')
        input_title.pack(side='left', pady=(0, 10))
        
        # Create a frame for the form with subtle border
        form_frame = ttk.Frame(input_frame, style='Card.TFrame', padding=15)
        form_frame.pack(fill='x', expand=True)
        
        # Genre selection with icon and tooltip
        genre_header = ttk.Frame(form_frame)
        genre_header.pack(fill='x', pady=(0, 5))
        genre_icon = ttk.Label(genre_header, text="📚", font=('Segoe UI', 14))
        genre_icon.pack(side='left', padx=(0, 5))
        ttk.Label(genre_header, text="Choose Your Genre", style='Header.TLabel').pack(side='left')
        
        self.genre_var = tk.StringVar(value="Fantasy")
        self.genre_icons = {
            "Fantasy": "🔮",
            "Sci-Fi": "🚀",
            "Mystery": "🔍",
            "Romance": "💝",
            "Horror": "👻",
            "Adventure": "🗺️",
            "Fairy Tale": "🏰"
        }
        genres = list(self.genre_icons.keys())
        
        genre_frame = ttk.Frame(form_frame, style='Input.TFrame', padding=5)
        genre_frame.pack(fill='x', pady=(0, 15))
        
        # Custom Combobox with icons
        self.genre_combo = ttk.Combobox(genre_frame, 
                                      textvariable=self.genre_var,
                                      values=[f"{self.genre_icons[g]} {g}" for g in genres], 
                                      state='readonly', 
                                      style='Dropdown.TCombobox')
        self.genre_combo.pack(fill='x')
        
        # Genre description frame
        self.genre_desc_frame = ttk.Frame(form_frame, style='Card.TFrame', padding=5)
        self.genre_desc_frame.pack(fill='x', pady=(0, 15))
        
        self.genre_desc_var = tk.StringVar()
        self.genre_desc_label = ttk.Label(self.genre_desc_frame, 
                                        textvariable=self.genre_desc_var,
                                        style='Description.TLabel',
                                        wraplength=250,
                                        justify='left')
        self.genre_desc_label.pack(fill='x', pady=5)
        
        # Genre descriptions
        self.genre_descriptions = {
            "Fantasy": "Create magical worlds filled with wonder and enchantment ✨",
            "Sci-Fi": "Explore future technologies and distant galaxies 🌠",
            "Mystery": "Unravel intriguing puzzles and solve compelling cases 🔎",
            "Romance": "Craft touching tales of love and relationships 💕",
            "Horror": "Weave spine-chilling stories of suspense and fear 🌙",
            "Adventure": "Tell exciting tales of exploration and discovery 🗺️",
            "Fairy Tale": "Spin classic stories of magic and wonder 🏰"
        }
        
        def update_genre_desc(*args):
            genre = self.genre_var.get().split(" ")[-1]  # Remove icon if present
            self.genre_desc_var.set(self.genre_descriptions.get(genre, ""))
        
        self.genre_var.trace('w', update_genre_desc)
        update_genre_desc()  # Set initial description
        
        # Length selection with icon and description
        length_header = ttk.Frame(form_frame)
        length_header.pack(fill='x', pady=(0, 5))
        length_icon = ttk.Label(length_header, text="📏", font=('Segoe UI', 14))
        length_icon.pack(side='left', padx=(0, 5))
        ttk.Label(length_header, text="Story Length", style='Header.TLabel').pack(side='left')
        
        self.length_icons = {
            "Short": "⚡",
            "Medium": "📖",
            "Long": "📚"
        }
        lengths = list(self.length_icons.keys())
        
        length_frame = ttk.Frame(form_frame, style='Input.TFrame', padding=5)
        length_frame.pack(fill='x', pady=(0, 5))
        
        # Custom length combobox with icons
        self.length_var = tk.StringVar()
        self.length_combo = ttk.Combobox(length_frame,
                                        textvariable=self.length_var,
                                        values=[f"{self.length_icons[l]} {l}" for l in lengths],
                                        state='readonly',
                                        style='Dropdown.TCombobox')
        # Set initial value with icon
        self.length_var.set(f"{self.length_icons['Medium']} Medium")
        self.length_combo.pack(fill='x')
        
        # Length description frame
        length_desc_frame = ttk.Frame(form_frame, style='Card.TFrame', padding=5)
        length_desc_frame.pack(fill='x', pady=(0, 15))
        
        # Length description with enhanced details
        self.length_desc = {
            "Short": {
                "desc": "A quick tale perfect for a brief read",
                "words": "~100 words",
                "time": "1-2 minute read"
            },
            "Medium": {
                "desc": "A satisfying story with more detail",
                "words": "~200 words",
                "time": "3-4 minute read"
            },
            "Long": {
                "desc": "An epic tale with rich storytelling",
                "words": "~300 words",
                "time": "5-6 minute read"
            }
        }
        
        # Create description labels
        self.length_desc_var = tk.StringVar()
        self.length_words_var = tk.StringVar()
        self.length_time_var = tk.StringVar()
        
        desc_label = ttk.Label(length_desc_frame, 
                             textvariable=self.length_desc_var,
                             style='Description.TLabel',
                             wraplength=250)
        desc_label.pack(fill='x')
        
        details_frame = ttk.Frame(length_desc_frame, style='Card.TFrame')
        details_frame.pack(fill='x', pady=(5, 0))
        
        words_label = ttk.Label(details_frame,
                              textvariable=self.length_words_var,
                              style='Stat.TLabel')
        words_label.pack(side='left', padx=5)
        
        time_label = ttk.Label(details_frame,
                             textvariable=self.length_time_var,
                             style='Stat.TLabel')
        time_label.pack(side='right', padx=5)
        
        def update_length_desc(*args):
            length = self.length_var.get().split(" ")[-1]  # Remove icon if present
            info = self.length_desc.get(length, {"desc": "", "words": "", "time": ""})
            self.length_desc_var.set(info["desc"])
            self.length_words_var.set(info["words"])
            self.length_time_var.set(info["time"])
            
        self.length_var.trace('w', update_length_desc)
        update_length_desc()  # Set initial description
        
        # Theme/prompt input with icon and placeholder
        prompt_header = ttk.Frame(form_frame)
        prompt_header.pack(fill='x', pady=(0, 5))
        prompt_icon = ttk.Label(prompt_header, text="💡", font=('Segoe UI', 14))
        prompt_icon.pack(side='left', padx=(0, 5))
        ttk.Label(prompt_header, text="Your Story Idea", style='Header.TLabel').pack(side='left')
        
        prompt_frame = ttk.Frame(form_frame, style='Input.TFrame', padding=5)
        prompt_frame.pack(fill='x', pady=(0, 5))
        self.prompt_entry = ttk.Entry(prompt_frame, style='TEntry')
        self.prompt_entry.pack(fill='x')
        self.prompt_entry.insert(0, "A magical forest")
        
        # Prompt suggestions
        suggestions_label = ttk.Label(form_frame, text="Try: 'A mysterious door', 'An ancient spell', 'A hidden city'",
                                    style='Description.TLabel', wraplength=250)
        suggestions_label.pack(fill='x', pady=(0, 20))
        
        # Create a frame for the action section
        action_frame = ttk.Frame(form_frame, style='Card.TFrame', padding=15)
        action_frame.pack(fill='x', pady=(10, 0))
        
        # Generate button with icon and improved styling
        button_frame = ttk.Frame(action_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.generate_btn = ttk.Button(
            button_frame, 
            text="✨ Generate Story ✨", 
            command=self.generate_story,
            style='TButton'
        )
        self.generate_btn.pack(fill='x', pady=(0, 5))
        
        # Button description
        btn_desc = ttk.Label(
            button_frame,
            text="Click to create your unique story",
            style='Description.TLabel',
            justify='center'
        )
        btn_desc.pack(fill='x')
        
        # Progress section
        progress_frame = ttk.Frame(action_frame, style='Card.TFrame')
        progress_frame.pack(fill='x', expand=True)
        
        # Progress bar with percentage
        progress_header = ttk.Frame(progress_frame, style='Card.TFrame')
        progress_header.pack(fill='x', pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_text = tk.StringVar(value="0%")
        
        progress_label = ttk.Label(
            progress_header,
            text="Progress",
            style='Header.TLabel'
        )
        progress_label.pack(side='left')
        
        progress_percent = ttk.Label(
            progress_header,
            textvariable=self.progress_text,
            style='Header.TLabel'
        )
        progress_percent.pack(side='right')
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style='Horizontal.TProgressbar',
            length=200
        )
        self.progress.pack(fill='x', pady=(0, 10))
        
        # Status label with icon
        status_frame = ttk.Frame(progress_frame, style='Card.TFrame')
        status_frame.pack(fill='x')
        
        self.status_var = tk.StringVar(value="Ready to create your story...")
        status_icon = ttk.Label(
            status_frame,
            text="📝",
            font=('Segoe UI', 12)
        )
        status_icon.pack(side='left', padx=(0, 5))
        
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style='Description.TLabel',
            wraplength=250
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        # Right side (story display and image)
        story_frame = ttk.Frame(self.main_frame)
        story_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky='nsew')
        story_frame.columnconfigure(0, weight=1)
        story_frame.rowconfigure(2, weight=1)  # Make story text expand
        
        # Story title with improved styling
        self.title_var = tk.StringVar(value="Your Story Will Appear Here")
        title_label = ttk.Label(story_frame, textvariable=self.title_var, 
                               style='Title.TLabel', wraplength=600, justify='center')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Image frame with improved styling
        self.image_frame = ttk.Frame(story_frame)
        self.image_frame.grid(row=1, column=0, pady=(0, 20), sticky='nsew')
        
        # Image label with border and padding
        self.image_label = ttk.Label(self.image_frame, style='TLabel')
        self.image_label.pack(padx=20, pady=(0, 20))
        
        # Story text with improved styling
        text_frame = ttk.Frame(story_frame)
        text_frame.grid(row=2, column=0, sticky='nsew')
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.story_text = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD,
            font=('Segoe UI', 12),
            width=60,
            height=15,
            bg='#3B4252',  # Slightly lighter than background
            fg='#ECEFF4',  # Light text color
            insertbackground='#88C0D0',  # Cursor color
            selectbackground='#88C0D0',  # Selection color
            selectforeground='#2E3440',  # Selected text color
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.story_text.grid(row=0, column=0, sticky='nsew')
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.progress_text.set(f"{int(value)}%")
        self.root.update_idletasks()
        
    def update_status(self, message):
        status_icons = {
            "Generating story...": "✍️",
            "Creating story image...": "🎨",
            "Story generated successfully!": "✨",
            "Error:": "❌",
            "Ready": "📝"
        }
        
        # Find the matching icon or use default
        icon = "📝"  # default icon
        for key in status_icons:
            if message.startswith(key):
                icon = status_icons[key]
                break
        
        self.status_var.set(f"{message}")
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
            
            # Get input values and remove icons
            genre = self.genre_var.get().split(" ")[-1]  # Remove icon
            length = self.length_var.get().split(" ")[-1]  # Remove icon
            prompt = self.prompt_entry.get()
            
            # Determine max length based on selection
            max_length = {"Short": 100, "Medium": 200, "Long": 300}[length]
            
            # Create story prompt
            story_prompt = f"Write a {genre} story about {prompt}. "
            
            self.update_progress(20)
            self.update_status("Generating story text...")
            
            # Generate the story with explicit truncation
            story = self.generator(story_prompt, 
                                max_length=max_length,
                                num_return_sequences=1,
                                temperature=0.7,
                                truncation=True,
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
            
    def create_prompt_image(self, prompt, size=(500, 400)):
        """Create a visually appealing image with the prompt text."""
        # Create a new image with a gradient background
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        # Create a more sophisticated gradient background
        def interpolate(color1, color2, t):
            return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
        
        # Nordic theme colors
        color1 = (46, 52, 64)    # Nord dark
        color2 = (94, 129, 172)  # Nord blue
        color3 = (136, 192, 208) # Nord light blue
        
        # Create multi-color gradient
        height = size[1]
        for y in range(height):
            if y < height/2:
                t = y / (height/2)
                color = interpolate(color1, color2, t)
            else:
                t = (y - height/2) / (height/2)
                color = interpolate(color2, color3, t)
            draw.line([(0, y), (size[0], y)], fill=color)
        
        # Add some decorative elements
        margin = 20
        # Draw border
        draw.rectangle([margin, margin, size[0]-margin, size[1]-margin], 
                      outline=(236, 239, 244), width=2)  # Nord white
        
        # Try to load a nicer font, fall back to default if not found
        try:
            main_font = ImageFont.truetype("arial.ttf", 36)
            sub_font = ImageFont.truetype("arial.ttf", 24)
        except:
            main_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
        
        # Wrap text with better width
        wrapped_text = textwrap.fill(prompt, width=25)
        
        # Get text size
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=main_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate position to center text
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw text with improved visibility
        outline_color = (236, 239, 244)  # Nord white
        text_color = (229, 233, 240)     # Nord light
        shadow_color = (46, 52, 64)      # Nord dark
        
        # Draw shadow
        shadow_offset = 3
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((x + dx*shadow_offset, y + dy*shadow_offset), 
                     wrapped_text, font=main_font, fill=shadow_color)
        
        # Draw main text
        draw.text((x, y), wrapped_text, font=main_font, fill=text_color)
        
        # Add a decorative subtitle with the current genre
        genre = self.genre_var.get().split(" ")[-1]  # Remove icon
        genre_text = f"✨ A {genre} Tale ✨"
        sub_bbox = draw.textbbox((0, 0), genre_text, font=sub_font)
        sub_width = sub_bbox[2] - sub_bbox[0]
        sub_x = (size[0] - sub_width) // 2
        sub_y = y + text_height + 20
        
        # Draw subtitle with shadow
        draw.text((sub_x + 1, sub_y + 1), genre_text, 
                 font=sub_font, fill=shadow_color)
        draw.text((sub_x, sub_y), genre_text, 
                 font=sub_font, fill=outline_color)
        
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