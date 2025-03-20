import os
import json
import tkinter as tk
import random
from tkinter import ttk, filedialog, messagebox
import shutil

# Try to import PIL, but continue if not available
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class GameEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Mining Game Editor")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Game paths
        self.game_dir = "."
        self.maps_dir = os.path.join(self.game_dir, "maps")
        
        # Ensure directories exist
        os.makedirs(self.maps_dir, exist_ok=True)
        
        # Module data - parsed from components/module.py
        self.module_types = ["ENGINE", "SHIELD", "WEAPON", "SCANNER", 
                            "FACILITY", "JUMP_ENGINE", "HANGAR", "AUX"]
        
        # Item types
        self.item_types = ["REGULAR", "ORE"]
        
        # Current data
        self.current_module = None
        self.current_item = None
        self.current_map = None
        
        # Status bar - initialize first
        self.status_var = tk.StringVar()
        self.status_var.set("Starting up...")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.modules_tab = ttk.Frame(self.notebook)
        self.items_tab = ttk.Frame(self.notebook)
        self.maps_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.modules_tab, text="Modules")
        self.notebook.add(self.items_tab, text="Items")
        self.notebook.add(self.maps_tab, text="Maps")
        
        # Set up each tab
        self.setup_modules_tab()
        self.setup_items_tab()
        self.setup_maps_tab()
        
        self.status_var.set("Ready")

    def setup_modules_tab(self):
        # Split into list and editor panels
        module_paned = ttk.PanedWindow(self.modules_tab, orient=tk.HORIZONTAL)
        module_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Module list
        list_frame = ttk.LabelFrame(module_paned, text="Module List")
        module_paned.add(list_frame, weight=1)
        
        # Module list toolbar
        list_toolbar = ttk.Frame(list_frame)
        list_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(list_toolbar, text="New Module", 
                  command=self.new_module).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_toolbar, text="Load Modules", 
                  command=self.load_modules).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_toolbar, text="Delete Selected", 
                  command=self.delete_module).pack(side=tk.LEFT, padx=2)
        
        # Module type filter
        self.module_filter_var = tk.StringVar(value="All")
        ttk.Label(list_toolbar, text="Filter:").pack(side=tk.LEFT, padx=(10, 2))
        module_filter = ttk.Combobox(list_toolbar, textvariable=self.module_filter_var,
                                    values=["All"] + self.module_types)
        module_filter.pack(side=tk.LEFT, padx=2)
        module_filter.bind("<<ComboboxSelected>>", self.filter_modules)
        
        # Module list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.module_listbox = tk.Listbox(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", 
                                 command=self.module_listbox.yview)
        self.module_listbox.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.module_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.module_listbox.bind("<<ListboxSelect>>", self.select_module)
        
        # Right panel - Module editor
        editor_frame = ttk.LabelFrame(module_paned, text="Module Editor")
        module_paned.add(editor_frame, weight=2)
        
        # Editor form
        form_frame = ttk.Frame(editor_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        row = 0
        # Module name
        ttk.Label(form_frame, text="Name:").grid(row=row, column=0, 
                                               sticky=tk.W, pady=2)
        self.module_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.module_name_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Module type
        ttk.Label(form_frame, text="Type:").grid(row=row, column=0, 
                                               sticky=tk.W, pady=2)
        self.module_type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.module_type_var,
                    values=self.module_types).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Module description
        ttk.Label(form_frame, text="Description:").grid(row=row, column=0, 
                                                      sticky=tk.W, pady=2)
        self.module_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.module_desc_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Module value
        ttk.Label(form_frame, text="Value:").grid(row=row, column=0, 
                                                sticky=tk.W, pady=2)
        self.module_value_var = tk.IntVar()
        ttk.Entry(form_frame, textvariable=self.module_value_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Module stats frame
        ttk.Label(form_frame, text="Stats:").grid(row=row, column=0, 
                                                sticky=tk.NW, pady=2)
        stats_frame = ttk.Frame(form_frame)
        stats_frame.grid(row=row, column=1, sticky=tk.EW, pady=2)
        
        # Stats table
        self.stats_frame = ttk.LabelFrame(editor_frame, text="Module Stats")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Stats table with add/remove buttons
        stats_toolbar = ttk.Frame(self.stats_frame)
        stats_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(stats_toolbar, text="Add Stat", 
                  command=self.add_module_stat).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_toolbar, text="Remove Selected", 
                  command=self.remove_module_stat).pack(side=tk.LEFT, padx=2)
        
        # Stats table
        self.stats_tree = ttk.Treeview(self.stats_frame, columns=('Name', 'Value'), 
                                      show='headings')
        self.stats_tree.heading('Name', text='Stat Name')
        self.stats_tree.heading('Value', text='Value')
        
        stats_scroll = ttk.Scrollbar(self.stats_frame, orient="vertical", 
                                    command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        ttk.Button(editor_frame, text="Save Module", 
                  command=self.save_module).pack(pady=10)

    def setup_items_tab(self):
        # Similar layout to modules tab
        item_paned = ttk.PanedWindow(self.items_tab, orient=tk.HORIZONTAL)
        item_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Item list
        list_frame = ttk.LabelFrame(item_paned, text="Item List")
        item_paned.add(list_frame, weight=1)
        
        # Item list toolbar
        list_toolbar = ttk.Frame(list_frame)
        list_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(list_toolbar, text="New Item", 
                  command=self.new_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_toolbar, text="Load Items", 
                  command=self.load_items).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_toolbar, text="Delete Selected", 
                  command=self.delete_item).pack(side=tk.LEFT, padx=2)
        
        # Item type filter
        self.item_filter_var = tk.StringVar(value="All")
        ttk.Label(list_toolbar, text="Filter:").pack(side=tk.LEFT, padx=(10, 2))
        item_filter = ttk.Combobox(list_toolbar, textvariable=self.item_filter_var,
                                  values=["All"] + self.item_types)
        item_filter.pack(side=tk.LEFT, padx=2)
        item_filter.bind("<<ComboboxSelected>>", self.filter_items)
        
        # Item list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.item_listbox = tk.Listbox(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", 
                                 command=self.item_listbox.yview)
        self.item_listbox.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.item_listbox.bind("<<ListboxSelect>>", self.select_item)
        
        # Right panel - Item editor
        editor_frame = ttk.LabelFrame(item_paned, text="Item Editor")
        item_paned.add(editor_frame, weight=2)
        
        # Editor form
        form_frame = ttk.Frame(editor_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        row = 0
        # Item name
        ttk.Label(form_frame, text="Name:").grid(row=row, column=0, 
                                               sticky=tk.W, pady=2)
        self.item_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.item_name_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Item type
        ttk.Label(form_frame, text="Type:").grid(row=row, column=0, 
                                               sticky=tk.W, pady=2)
        self.item_type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.item_type_var,
                    values=self.item_types).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Item description
        ttk.Label(form_frame, text="Description:").grid(row=row, column=0, 
                                                      sticky=tk.W, pady=2)
        self.item_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.item_desc_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Item value
        ttk.Label(form_frame, text="Value:").grid(row=row, column=0, 
                                                sticky=tk.W, pady=2)
        self.item_value_var = tk.IntVar()
        ttk.Entry(form_frame, textvariable=self.item_value_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Item max stack
        ttk.Label(form_frame, text="Max Stack:").grid(row=row, column=0, 
                                                    sticky=tk.W, pady=2)
        self.item_stack_var = tk.IntVar(value=20)
        ttk.Entry(form_frame, textvariable=self.item_stack_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # For Ore items - Color picker
        self.ore_frame = ttk.LabelFrame(form_frame, text="Ore Properties")
        self.ore_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        ttk.Label(self.ore_frame, text="Ore Color (RGB):").grid(row=0, column=0, 
                                                              sticky=tk.W, pady=2)
        color_frame = ttk.Frame(self.ore_frame)
        color_frame.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        self.ore_r_var = tk.IntVar(value=100)
        self.ore_g_var = tk.IntVar(value=100)
        self.ore_b_var = tk.IntVar(value=100)
        
        ttk.Label(color_frame, text="R:").pack(side=tk.LEFT)
        ttk.Spinbox(color_frame, from_=0, to=255, width=5, 
                   textvariable=self.ore_r_var).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(color_frame, text="G:").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Spinbox(color_frame, from_=0, to=255, width=5, 
                   textvariable=self.ore_g_var).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(color_frame, text="B:").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Spinbox(color_frame, from_=0, to=255, width=5, 
                   textvariable=self.ore_b_var).pack(side=tk.LEFT, padx=2)
        
        # Color preview
        self.color_preview = tk.Canvas(color_frame, width=30, height=20)
        self.color_preview.pack(side=tk.LEFT, padx=(10, 0))
        self.update_color_preview()
        
        # Update color when values change
        self.ore_r_var.trace_add("write", lambda *args: self.update_color_preview())
        self.ore_g_var.trace_add("write", lambda *args: self.update_color_preview())
        self.ore_b_var.trace_add("write", lambda *args: self.update_color_preview())
        
        # Hide ore frame initially
        self.ore_frame.grid_remove()
        
        # Watch for type changes to show/hide ore frame
        self.item_type_var.trace_add("write", self.toggle_ore_frame)
        
        # Save button
        ttk.Button(editor_frame, text="Save Item", 
                  command=self.save_item).pack(pady=10)

    def setup_maps_tab(self):
        # Map tab with list and editor
        map_paned = ttk.PanedWindow(self.maps_tab, orient=tk.HORIZONTAL)
        map_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Map list
        list_frame = ttk.LabelFrame(map_paned, text="Map List")
        map_paned.add(list_frame, weight=1)
        
        # Map list toolbar
        list_toolbar = ttk.Frame(list_frame)
        list_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(list_toolbar, text="New Map", 
                  command=self.new_map).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_toolbar, text="Load Maps", 
                  command=self.load_maps).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_toolbar, text="Delete Selected", 
                  command=self.delete_map).pack(side=tk.LEFT, padx=2)
        
        # Map list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.map_listbox = tk.Listbox(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", 
                                 command=self.map_listbox.yview)
        self.map_listbox.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.map_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.map_listbox.bind("<<ListboxSelect>>", self.select_map)
        
        # Right panel - Map editor
        editor_frame = ttk.LabelFrame(map_paned, text="Map Editor")
        map_paned.add(editor_frame, weight=2)
        
        # Editor with notebook for different sections
        map_notebook = ttk.Notebook(editor_frame)
        map_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Basic info tab
        basic_frame = ttk.Frame(map_notebook)
        map_notebook.add(basic_frame, text="Basic Info")
        
        basic_form = ttk.Frame(basic_frame)
        basic_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        row = 0
        # Map ID
        ttk.Label(basic_form, text="ID:").grid(row=row, column=0, 
                                             sticky=tk.W, pady=2)
        self.map_id_var = tk.StringVar()
        ttk.Entry(basic_form, textvariable=self.map_id_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Map name
        ttk.Label(basic_form, text="Name:").grid(row=row, column=0, 
                                               sticky=tk.W, pady=2)
        self.map_name_var = tk.StringVar()
        ttk.Entry(basic_form, textvariable=self.map_name_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Map type
        ttk.Label(basic_form, text="Type:").grid(row=row, column=0, 
                                               sticky=tk.W, pady=2)
        self.map_type_var = tk.StringVar()
        ttk.Combobox(basic_form, textvariable=self.map_type_var,
                    values=["empty", "asteroid_field", "inhabited"]).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Map background
        ttk.Label(basic_form, text="Background:").grid(row=row, column=0, 
                                                     sticky=tk.W, pady=2)
        self.map_bg_var = tk.StringVar()
        ttk.Combobox(basic_form, textvariable=self.map_bg_var,
                    values=["starfield_sparse", "starfield_dense", "deep_space", "nebula"]).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Connections frame
        conn_frame = ttk.LabelFrame(basic_form, text="Connections")
        conn_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # North connection
        ttk.Label(conn_frame, text="North:").grid(row=0, column=0, 
                                                sticky=tk.W, pady=2)
        self.map_north_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.map_north_var).grid(
            row=0, column=1, sticky=tk.EW, pady=2)
        
        # East connection
        ttk.Label(conn_frame, text="East:").grid(row=1, column=0, 
                                               sticky=tk.W, pady=2)
        self.map_east_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.map_east_var).grid(
            row=1, column=1, sticky=tk.EW, pady=2)
        
        # South connection
        ttk.Label(conn_frame, text="South:").grid(row=2, column=0, 
                                                sticky=tk.W, pady=2)
        self.map_south_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.map_south_var).grid(
            row=2, column=1, sticky=tk.EW, pady=2)
        
        # West connection
        ttk.Label(conn_frame, text="West:").grid(row=3, column=0, 
                                               sticky=tk.W, pady=2)
        self.map_west_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.map_west_var).grid(
            row=3, column=1, sticky=tk.EW, pady=2)
        
        # Objects tab
        objects_frame = ttk.Frame(map_notebook)
        map_notebook.add(objects_frame, text="Objects")
        
        # Objects toolbar
        obj_toolbar = ttk.Frame(objects_frame)
        obj_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(obj_toolbar, text="Add Asteroid", 
                  command=lambda: self.add_map_object("asteroid")).pack(side=tk.LEFT, padx=2)
        ttk.Button(obj_toolbar, text="Add Station", 
                  command=lambda: self.add_map_object("station")).pack(side=tk.LEFT, padx=2)
        ttk.Button(obj_toolbar, text="Remove Selected", 
                  command=self.remove_map_object).pack(side=tk.LEFT, padx=2)
        
        # Objects treeview
        self.objects_tree = ttk.Treeview(objects_frame, 
                                        columns=('Type', 'X', 'Y', 'Properties'), 
                                        show='headings')
        self.objects_tree.heading('Type', text='Type')
        self.objects_tree.heading('X', text='X')
        self.objects_tree.heading('Y', text='Y')
        self.objects_tree.heading('Properties', text='Properties')
        
        self.objects_tree.column('Type', width=80)
        self.objects_tree.column('X', width=60)
        self.objects_tree.column('Y', width=60)
        self.objects_tree.column('Properties', width=200)
        
        obj_scroll = ttk.Scrollbar(objects_frame, orient="vertical", 
                                  command=self.objects_tree.yview)
        self.objects_tree.configure(yscrollcommand=obj_scroll.set)
        
        self.objects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        obj_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Metadata tab
        metadata_frame = ttk.Frame(map_notebook)
        map_notebook.add(metadata_frame, text="Metadata")
        
        meta_form = ttk.Frame(metadata_frame)
        meta_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        row = 0
        # Description
        ttk.Label(meta_form, text="Description:").grid(row=row, column=0, 
                                                     sticky=tk.W, pady=2)
        self.map_desc_var = tk.StringVar()
        ttk.Entry(meta_form, textvariable=self.map_desc_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Danger level
        ttk.Label(meta_form, text="Danger Level:").grid(row=row, column=0, 
                                                      sticky=tk.W, pady=2)
        self.map_danger_var = tk.StringVar()
        ttk.Combobox(meta_form, textvariable=self.map_danger_var,
                    values=["none", "low", "medium", "high", "extreme"]).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Resource richness
        ttk.Label(meta_form, text="Resource Richness:").grid(row=row, column=0, 
                                                           sticky=tk.W, pady=2)
        self.map_resource_var = tk.StringVar()
        ttk.Combobox(meta_form, textvariable=self.map_resource_var,
                    values=["none", "very_low", "low", "medium", "high", "very_high"]).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Discovery date
        ttk.Label(meta_form, text="Discovery Date:").grid(row=row, column=0, 
                                                        sticky=tk.W, pady=2)
        self.map_date_var = tk.StringVar()
        ttk.Entry(meta_form, textvariable=self.map_date_var).grid(
            row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Save button
        ttk.Button(editor_frame, text="Save Map", 
                  command=self.save_map).pack(pady=10)
        
        # Add constants for world size
        self.WORLD_WIDTH = 3200
        self.WORLD_HEIGHT = 2400
        
        # Set up tab change event to load data
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # Initialize modules
        self.load_modules()
        
        # Initialize items
        self.load_items()
        
        # Initialize maps
        self.load_maps()

    # Module functions
    def new_module(self):
        """Create a new module"""
        self.current_module = {
            "name": "New Module",
            "type": "ENGINE",
            "description": "A new module",
            "value": 100,
            "stats": {}
        }
        self.load_module_to_form()
        self.status_var.set("New module created")

    def load_modules(self):
        """Load modules from components/module.py"""
        # In a real implementation, parse the Python file
        # For this example, load some sample modules
        modules = [
            {
                "name": "Basic Engine",
                "type": "ENGINE",
                "description": "Standard engine with moderate speed and acceleration.",
                "value": 200,
                "stats": {"max_speed": 5.0, "acceleration": 0.2, "turn_rate": 3.0, "energy_usage": 1}
            },
            {
                "name": "Speedy Engine",
                "type": "ENGINE",
                "description": "Faster engine with higher energy consumption.",
                "value": 500,
                "stats": {"max_speed": 7.0, "acceleration": 0.25, "turn_rate": 2.5, "energy_usage": 2}
            },
            {
                "name": "Basic Shield",
                "type": "SHIELD",
                "description": "Standard shield providing moderate protection.",
                "value": 250,
                "stats": {"capacity": 50, "regen_rate": 0.5}
            }
        ]
        
        # Clear and update listbox
        self.module_listbox.delete(0, tk.END)
        for module in modules:
            self.module_listbox.insert(tk.END, f"{module['name']} ({module['type']})")
        
        self.status_var.set(f"Loaded {len(modules)} modules")

    def select_module(self, event):
        """Handle selection of a module from the list"""
        selection = self.module_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        # In real implementation, get the actual module data
        # This is a placeholder
        module_name = self.module_listbox.get(index).split(" (")[0]
        
        # Find the module in our data
        # Here we just use a sample
        if module_name == "Basic Engine":
            self.current_module = {
                "name": "Basic Engine",
                "type": "ENGINE",
                "description": "Standard engine with moderate speed and acceleration.",
                "value": 200,
                "stats": {"max_speed": 5.0, "acceleration": 0.2, "turn_rate": 3.0, "energy_usage": 1}
            }
        elif module_name == "Speedy Engine":
            self.current_module = {
                "name": "Speedy Engine",
                "type": "ENGINE",
                "description": "Faster engine with higher energy consumption.",
                "value": 500,
                "stats": {"max_speed": 7.0, "acceleration": 0.25, "turn_rate": 2.5, "energy_usage": 2}
            }
        elif module_name == "Basic Shield":
            self.current_module = {
                "name": "Basic Shield",
                "type": "SHIELD",
                "description": "Standard shield providing moderate protection.",
                "value": 250,
                "stats": {"capacity": 50, "regen_rate": 0.5}
            }
        
        self.load_module_to_form()
        self.status_var.set(f"Selected module: {module_name}")

    def load_module_to_form(self):
        """Load module data to the form"""
        if not self.current_module:
            return
        
        # Set form values
        self.module_name_var.set(self.current_module["name"])
        self.module_type_var.set(self.current_module["type"])
        self.module_desc_var.set(self.current_module["description"])
        self.module_value_var.set(self.current_module["value"])
        
        # Clear and populate stats
        self.stats_tree.delete(*self.stats_tree.get_children())
        for stat_name, stat_value in self.current_module["stats"].items():
            self.stats_tree.insert("", "end", values=(stat_name, stat_value))

    def save_module(self):
        """Save the current module"""
        if not self.current_module:
            return
        
        # Get form values
        self.current_module["name"] = self.module_name_var.get()
        self.current_module["type"] = self.module_type_var.get()
        self.current_module["description"] = self.module_desc_var.get()
        
        try:
            self.current_module["value"] = int(self.module_value_var.get())
        except ValueError:
            messagebox.showerror("Error", "Value must be a number")
            return
        
        # Get stats
        stats = {}
        for item_id in self.stats_tree.get_children():
            name, value = self.stats_tree.item(item_id)["values"]
            try:
                # Try to convert to appropriate type
                if "." in str(value):
                    stats[name] = float(value)
                else:
                    stats[name] = int(value)
            except ValueError:
                # Keep as string if conversion fails
                stats[name] = value
        
        self.current_module["stats"] = stats
        
        # In real implementation, save to module.py file
        messagebox.showinfo("Success", f"Module {self.current_module['name']} saved")
        self.status_var.set(f"Saved module: {self.current_module['name']}")

    def delete_module(self):
        """Delete the selected module"""
        selection = self.module_listbox.curselection()
        if not selection:
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this module?"):
            return
            
        # Delete from listbox and data
        self.module_listbox.delete(selection)
        self.current_module = None
        
        # Clear form
        self.module_name_var.set("")
        self.module_type_var.set("")
        self.module_desc_var.set("")
        self.module_value_var.set(0)
        self.stats_tree.delete(*self.stats_tree.get_children())
        
        self.status_var.set("Module deleted")

    def filter_modules(self, event=None):
        """Filter modules by type"""
        # In real implementation, filter the module list
        self.status_var.set(f"Filtering modules: {self.module_filter_var.get()}")

    def add_module_stat(self):
        """Add a new stat to the module"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Stat")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Stat Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        stat_name = ttk.Entry(dialog)
        stat_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Stat Value:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        stat_value = ttk.Entry(dialog)
        stat_value.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        def add_stat():
            name = stat_name.get().strip()
            value = stat_value.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Stat name is required")
                return
                
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string if not a number
                pass
                
            self.stats_tree.insert("", "end", values=(name, value))
            dialog.destroy()
            
        ttk.Button(dialog, text="Add", command=add_stat).grid(row=2, column=0, columnspan=2, pady=10)

    def remove_module_stat(self):
        """Remove the selected stat"""
        selection = self.stats_tree.selection()
        if selection:
            self.stats_tree.delete(selection)

    # Item functions
    def new_item(self):
        """Create a new item"""
        self.current_item = {
            "name": "New Item",
            "type": "REGULAR",
            "description": "A new item",
            "value": 10,
            "max_stack": 20,
            "color": (100, 100, 100)
        }
        self.load_item_to_form()
        self.status_var.set("New item created")

    def load_items(self):
        """Load items from components/items.py"""
        # This is a simplified version that loads the main items
        # In a real implementation, we'd parse the Python file
        items = [
            # Ore items
            {
                "name": "Low-grade Ore",
                "type": "ORE",
                "description": "Common ore with minimal value. Found in most asteroids.",
                "value": 1,
                "max_stack": 50,
                "color": (139, 69, 19)
            },
            {
                "name": "High-grade Ore",
                "type": "ORE",
                "description": "Better quality ore with higher mineral content.",
                "value": 3,
                "max_stack": 30,
                "color": (255, 255, 0)
            },
            {
                "name": "Rare Ore",
                "type": "ORE",
                "description": "Exotic minerals with unusual properties. Valuable for research.",
                "value": 8,
                "max_stack": 20,
                "color": (128, 0, 128)
            },
            {
                "name": "Raw Silver",
                "type": "ORE",
                "description": "Unrefined silver ore. Can be processed into currency.",
                "value": 5,
                "max_stack": 20,
                "color": (192, 192, 192)
            },
            
            # Equipment items
            {
                "name": "Basic Scanner",
                "type": "REGULAR",
                "description": "Simple scanner that helps detect asteroid composition.",
                "value": 50,
                "max_stack": 1
            },
            {
                "name": "Mining Laser Upgrade",
                "type": "REGULAR",
                "description": "Increases mining laser efficiency by 15%.",
                "value": 100,
                "max_stack": 1
            },
            {
                "name": "Shield Booster",
                "type": "REGULAR",
                "description": "Enhances shield capacity by 20 points.",
                "value": 75,
                "max_stack": 1
            },
            {
                "name": "Cargo Expander",
                "type": "REGULAR",
                "description": "Increases cargo capacity by 10 slots.",
                "value": 120,
                "max_stack": 1
            }
        ]
        
        # Clear and update listbox
        self.item_listbox.delete(0, tk.END)
        for item in items:
            self.item_listbox.insert(tk.END, f"{item['name']} ({item['type']})")
        
        self.status_var.set(f"Loaded {len(items)} items")

    def select_item(self, event):
        """Handle selection of an item from the list"""
        selection = self.item_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        # In real implementation, get the actual item data
        # This is a placeholder
        item_name = self.item_listbox.get(index).split(" (")[0]
        
        # Find the item in our data
        # Here we just use a sample
        if item_name == "Low-grade Ore":
            self.current_item = {
                "name": "Low-grade Ore",
                "type": "ORE",
                "description": "Common ore with minimal value. Found in most asteroids.",
                "value": 1,
                "max_stack": 50,
                "color": (139, 69, 19)
            }
        elif item_name == "High-grade Ore":
            self.current_item = {
                "name": "High-grade Ore",
                "type": "ORE",
                "description": "Better quality ore with higher mineral content.",
                "value": 3,
                "max_stack": 30,
                "color": (255, 255, 0)
            }
        elif item_name == "Basic Scanner":
            self.current_item = {
                "name": "Basic Scanner",
                "type": "REGULAR",
                "description": "Simple scanner that helps detect asteroid composition.",
                "value": 50,
                "max_stack": 1
            }
        
        self.load_item_to_form()
        self.status_var.set(f"Selected item: {item_name}")

    def load_item_to_form(self):
        """Load item data to the form"""
        if not self.current_item:
            return
        
        # Set form values
        self.item_name_var.set(self.current_item["name"])
        self.item_type_var.set(self.current_item["type"])
        self.item_desc_var.set(self.current_item["description"])
        self.item_value_var.set(self.current_item["value"])
        self.item_stack_var.set(self.current_item["max_stack"])
        
        # Set ore color if applicable
        if self.current_item["type"] == "ORE" and "color" in self.current_item:
            color = self.current_item["color"]
            self.ore_r_var.set(color[0])
            self.ore_g_var.set(color[1])
            self.ore_b_var.set(color[2])
            
        # Show/hide ore frame
        self.toggle_ore_frame()

    def toggle_ore_frame(self, *args):
        """Show or hide ore frame based on item type"""
        if self.item_type_var.get() == "ORE":
            self.ore_frame.grid()
        else:
            self.ore_frame.grid_remove()

    def update_color_preview(self):
        """Update the color preview canvas"""
        r = self.ore_r_var.get()
        g = self.ore_g_var.get()
        b = self.ore_b_var.get()
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.color_preview.delete("all")
        self.color_preview.create_rectangle(0, 0, 30, 20, fill=color, outline="")

    def save_item(self):
        """Save the current item"""
        if not self.current_item:
            return
        
        # Get form values
        self.current_item["name"] = self.item_name_var.get()
        self.current_item["type"] = self.item_type_var.get()
        self.current_item["description"] = self.item_desc_var.get()
        
        try:
            self.current_item["value"] = int(self.item_value_var.get())
            self.current_item["max_stack"] = int(self.item_stack_var.get())
        except ValueError:
            messagebox.showerror("Error", "Value and Max Stack must be numbers")
            return
        
        # Get ore color if applicable
        if self.current_item["type"] == "ORE":
            self.current_item["color"] = (
                self.ore_r_var.get(),
                self.ore_g_var.get(),
                self.ore_b_var.get()
            )
        
        # In real implementation, save to items.py file
        messagebox.showinfo("Success", f"Item {self.current_item['name']} saved")
        self.status_var.set(f"Saved item: {self.current_item['name']}")

    def delete_item(self):
        """Delete the selected item"""
        selection = self.item_listbox.curselection()
        if not selection:
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            return
            
        # Delete from listbox and data
        self.item_listbox.delete(selection)
        self.current_item = None
        
        # Clear form
        self.item_name_var.set("")
        self.item_type_var.set("")
        self.item_desc_var.set("")
        self.item_value_var.set(0)
        self.item_stack_var.set(20)
        
        self.status_var.set("Item deleted")

    def filter_items(self, event=None):
        """Filter items by type"""
        # In real implementation, filter the item list
        self.status_var.set(f"Filtering items: {self.item_filter_var.get()}")

    # Map functions
    def new_map(self):
        """Create a new map"""
        self.current_map = {
            "id": "new-map",
            "name": "New Map",
            "type": "empty",
            "connections": {
                "north": None,
                "east": None,
                "south": None,
                "west": None
            },
            "background": "starfield_sparse",
            "objects": [],
            "metadata": {
                "description": "A new map area.",
                "danger_level": "low",
                "resource_richness": "low",
                "discovery_date": "2200"
            }
        }
        self.load_map_to_form()
        self.status_var.set("New map created")

    def load_maps(self):
        """Load maps from maps directory"""
        try:
            # Create maps directory if it doesn't exist
            if not os.path.exists(self.maps_dir):
                os.makedirs(self.maps_dir)
                self.status_var.set("Created maps directory, no maps found")
                return
                
            map_files = [f for f in os.listdir(self.maps_dir) if f.endswith(".json")]
            
            if not map_files:
                self.status_var.set("No map files found")
                return
                
            # Clear listbox
            self.map_listbox.delete(0, tk.END)
            
            # Load each map file
            for map_file in map_files:
                try:
                    with open(os.path.join(self.maps_dir, map_file), "r") as f:
                        map_data = json.load(f)
                        self.map_listbox.insert(tk.END, f"{map_data['name']} ({map_data['id']})")
                except Exception as e:
                    print(f"Error loading {map_file}: {str(e)}")
            
            self.status_var.set(f"Loaded {len(map_files)} maps")
        except Exception as e:
            print(f"Error in load_maps: {str(e)}")
            self.status_var.set("Error loading maps")

    def select_map(self, event):
        """Handle selection of a map from the list"""
        selection = self.map_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        map_id = self.map_listbox.get(index).split(" (")[1][:-1]  # Extract ID from "Name (ID)"
        
        # Load the map from file
        try:
            with open(os.path.join(self.maps_dir, f"{map_id}.json"), "r") as f:
                self.current_map = json.load(f)
                self.load_map_to_form()
                self.status_var.set(f"Selected map: {self.current_map['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map: {str(e)}")

    def load_map_to_form(self):
        """Load map data to the form"""
        if not self.current_map:
            return
        
        # Basic info
        self.map_id_var.set(self.current_map["id"])
        self.map_name_var.set(self.current_map["name"])
        self.map_type_var.set(self.current_map["type"])
        self.map_bg_var.set(self.current_map["background"])
        
        # Connections
        connections = self.current_map["connections"]
        self.map_north_var.set(connections["north"] if connections["north"] else "")
        self.map_east_var.set(connections["east"] if connections["east"] else "")
        self.map_south_var.set(connections["south"] if connections["south"] else "")
        self.map_west_var.set(connections["west"] if connections["west"] else "")
        
        # Objects
        self.objects_tree.delete(*self.objects_tree.get_children())
        for obj in self.current_map["objects"]:
            obj_type = obj["type"]
            x = obj["x"]
            y = obj["y"]
            
            # Get other properties
            props = {}
            for key, value in obj.items():
                if key not in ["type", "x", "y"]:
                    props[key] = value
            
            # Format properties as string
            props_str = ", ".join(f"{k}={v}" for k, v in props.items())
            
            self.objects_tree.insert("", "end", values=(obj_type, x, y, props_str))
        
        # Metadata
        metadata = self.current_map.get("metadata", {})
        self.map_desc_var.set(metadata.get("description", ""))
        self.map_danger_var.set(metadata.get("danger_level", "low"))
        self.map_resource_var.set(metadata.get("resource_richness", "low"))
        self.map_date_var.set(metadata.get("discovery_date", ""))

    def save_map(self):
        """Save the current map"""
        if not self.current_map:
            return
        
        # Get basic info
        map_id = self.map_id_var.get().strip()
        if not map_id:
            messagebox.showerror("Error", "Map ID is required")
            return
            
        self.current_map["id"] = map_id
        self.current_map["name"] = self.map_name_var.get()
        self.current_map["type"] = self.map_type_var.get()
        self.current_map["background"] = self.map_bg_var.get()
        
        # Get connections
        self.current_map["connections"] = {
            "north": self.map_north_var.get() or None,
            "east": self.map_east_var.get() or None,
            "south": self.map_south_var.get() or None,
            "west": self.map_west_var.get() or None
        }
        
        # Get objects
        objects = []
        for item_id in self.objects_tree.get_children():
            obj_type, x, y, props_str = self.objects_tree.item(item_id)["values"]
            
            obj = {
                "type": obj_type,
                "x": int(x),
                "y": int(y)
            }
            
            # Parse properties
            if props_str:
                for prop in props_str.split(", "):
                    if "=" in prop:
                        key, value = prop.split("=", 1)
                        # Try to convert to appropriate type
                        try:
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            elif value.replace(".", "", 1).isdigit():
                                value = float(value)
                        except:
                            pass
                        obj[key] = value
            
            objects.append(obj)
            
        self.current_map["objects"] = objects
        
        # Get metadata
        self.current_map["metadata"] = {
            "description": self.map_desc_var.get(),
            "danger_level": self.map_danger_var.get(),
            "resource_richness": self.map_resource_var.get(),
            "discovery_date": self.map_date_var.get()
        }
        
        # Add random asteroids for empty systems based on resource richness
        if self.current_map["type"] == "empty" and not objects:
            resource_richness = self.current_map["metadata"]["resource_richness"]
            if resource_richness != "none":
                # Generate random asteroids based on richness
                num_asteroids = 0
                if resource_richness == "very_low":
                    num_asteroids = random.randint(1, 5)
                elif resource_richness == "low":
                    num_asteroids = random.randint(3, 8)
                elif resource_richness == "medium":
                    num_asteroids = random.randint(5, 12)
                elif resource_richness == "high":
                    num_asteroids = random.randint(10, 20)
                elif resource_richness == "very_high":
                    num_asteroids = random.randint(15, 30)
                
                # Add asteroids to the map
                for _ in range(num_asteroids):
                    # Random position
                    x = random.randint(100, 3100)
                    y = random.randint(100, 2300)
                    
                    # Determine asteroid type based on richness
                    ast_type_roll = random.random()
                    if resource_richness in ["high", "very_high"] and ast_type_roll > 0.6:
                        ast_type = "rich"
                    elif resource_richness in ["very_low", "low"] and ast_type_roll > 0.7:
                        ast_type = "dry"
                    else:
                        ast_type = "regular"
                    
                    # Random size between 20-50
                    size = random.randint(20, 50)
                    
                    # Add to objects
                    self.current_map["objects"].append({
                        "type": "asteroid",
                        "x": x,
                        "y": y,
                        "size": size,
                        "asteroid_type": ast_type
                    })
                
                # Update the objects list in the UI
                self.objects_tree.delete(*self.objects_tree.get_children())
                for obj in self.current_map["objects"]:
                    props_str = ", ".join(f"{k}={v}" for k, v in obj.items() 
                                        if k not in ["type", "x", "y"])
                    self.objects_tree.insert("", "end", values=(obj["type"], obj["x"], obj["y"], props_str))
        
        # Save to file
        try:
            with open(os.path.join(self.maps_dir, f"{map_id}.json"), "w") as f:
                json.dump(self.current_map, f, indent=2)
                
            messagebox.showinfo("Success", f"Map {self.current_map['name']} saved")
            self.status_var.set(f"Saved map: {self.current_map['name']}")
            
            # Refresh map list
            self.load_maps()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save map: {str(e)}")

    def delete_map(self):
        """Delete the selected map"""
        selection = self.map_listbox.curselection()
        if not selection:
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this map?"):
            return
            
        map_id = self.map_listbox.get(selection[0]).split(" (")[1][:-1]
        
        # Delete the file
        try:
            os.remove(os.path.join(self.maps_dir, f"{map_id}.json"))
            self.map_listbox.delete(selection)
            self.current_map = None
            self.status_var.set("Map deleted")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete map: {str(e)}")

    def add_map_object(self, obj_type):
        """Add a new object to the map"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add {obj_type.title()}")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Position
        ttk.Label(dialog, text="X Position:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        x_pos = ttk.Entry(dialog)
        x_pos.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        # Set default position to center
        x_pos.insert(0, str(WORLD_WIDTH // 2))
        
        ttk.Label(dialog, text="Y Position:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        y_pos = ttk.Entry(dialog)
        y_pos.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        y_pos.insert(0, str(WORLD_HEIGHT // 2))
        
        # Specific properties for each type
        props_frame = ttk.LabelFrame(dialog, text="Properties")
        props_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
        
        properties = {}
        
        if obj_type == "asteroid":
            ttk.Label(props_frame, text="Size:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            size = ttk.Entry(props_frame)
            size.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
            size.insert(0, "30")
            properties["size"] = size
            
            ttk.Label(props_frame, text="Asteroid Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            ast_type = ttk.Combobox(props_frame, values=["regular", "rich", "dry"])
            ast_type.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
            ast_type.current(0)
            properties["asteroid_type"] = ast_type
            
        elif obj_type == "station":
            ttk.Label(props_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            name = ttk.Entry(props_frame)
            name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
            name.insert(0, "Space Station")
            properties["name"] = name
            
            ttk.Label(props_frame, text="Dialog:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            dialog_text = tk.Text(props_frame, width=30, height=5)
            dialog_text.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
            dialog_text.insert("1.0", "Welcome to the station, traveler.")
            properties["dialog"] = dialog_text
            
            ttk.Label(props_frame, text="Size:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            size = ttk.Entry(props_frame)
            size.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
            size.insert(0, "120")
            properties["size"] = size
        
        def add_object():
            try:
                x = int(x_pos.get())
                y = int(y_pos.get())
                
                # Get property values
                props = {}
                for key, widget in properties.items():
                    if key == "dialog" and obj_type == "station":
                        # Special handling for Text widget
                        value = widget.get("1.0", tk.END).strip()
                    else:
                        value = widget.get()
                    
                    # Try to convert numbers
                    try:
                        if isinstance(value, str):
                            if value.isdigit():
                                value = int(value)
                            elif value.replace(".", "", 1).isdigit():
                                value = float(value)
                    except:
                        pass
                    props[key] = value
                
                # Format props string
                props_str = ", ".join(f"{k}={v}" for k, v in props.items())
                
                # Add to treeview
                self.objects_tree.insert("", "end", values=(obj_type, x, y, props_str))
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Position values must be numbers")
            
        ttk.Button(dialog, text="Add", command=add_object).grid(row=3, column=0, columnspan=2, pady=10)

    def remove_map_object(self):
        """Remove the selected object"""
        selection = self.objects_tree.selection()
        if selection:
            self.objects_tree.delete(selection)
            
    def on_tab_change(self, event):
        """Load data when tab is changed"""
        tab_id = self.notebook.index(self.notebook.select())
        
        # 0 = Modules, 1 = Items, 2 = Maps
        if tab_id == 0:
            self.load_modules()
        elif tab_id == 1:
            self.load_items()
        elif tab_id == 2:
            self.load_maps()

if __name__ == "__main__":
    root = tk.Tk()
    editor = GameEditor(root)
    root.mainloop()