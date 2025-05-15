import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import time
import json
from typing import Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum, auto
import webbrowser
import random

# ==================== Constants and Enums ====================
class OperationType(Enum):
    INSERT_HEAD = auto()
    INSERT_TAIL = auto()
    INSERT_POS = auto()
    DELETE = auto()
    SEARCH = auto()
    CLEAR = auto()
    LOAD = auto()
    IMPORT = auto()
    EXPORT = auto()

class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    GREEN = "green"

@dataclass
class AnimationSettings:
    speed: float = 0.2
    highlight_color: str = "#FFF9C4"
    node_scale: float = 1.0
    enable_physics: bool = False

# ==================== Data Structures ====================
class Node:
    def __init__(self, value: str):
        self.value: str = str(value)
        self.next: Optional['Node'] = None
        self.prev: Optional['Node'] = None
        self.id: int = hash(f"{value}_{time.time()}")

class DoublyLinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.length: int = 0
        self.operation_history: List[Dict] = []

    def insert_at_head(self, value: str) -> None:
        new_node = Node(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.length += 1
        self._record_operation(OperationType.INSERT_HEAD, value, 0)

    def insert_at_tail(self, value: str) -> None:
        new_node = Node(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        self._record_operation(OperationType.INSERT_TAIL, value, self.length-1)

    def insert_at_position(self, index: int, value: str) -> None:
        if index < 0 or index > self.length:
            raise IndexError("Index out of range")
        if index == 0:
            self.insert_at_head(value)
        elif index == self.length:
            self.insert_at_tail(value)
        else:
            new_node = Node(value)
            current = self._get_node(index)
            new_node.prev = current.prev
            new_node.next = current
            if current.prev:
                current.prev.next = new_node
            current.prev = new_node
            self.length += 1
            self._record_operation(OperationType.INSERT_POS, value, index)

    def delete_at_position(self, index: int) -> str:
        if index < 0 or index >= self.length:
            raise IndexError("Index out of range")
        if self.length == 1:
            value = self.head.value
            self.head = self.tail = None
        elif index == 0:
            value = self.head.value
            self.head = self.head.next
            if self.head:
                self.head.prev = None
        elif index == self.length - 1:
            value = self.tail.value
            self.tail = self.tail.prev
            if self.tail:
                self.tail.next = None
        else:
            current = self._get_node(index)
            value = current.value
            current.prev.next = current.next
            current.next.prev = current.prev
        self.length -= 1
        self._record_operation(OperationType.DELETE, value, index)
        return value

    def clear(self) -> None:
        self.head = self.tail = None
        self.length = 0
        self._record_operation(OperationType.CLEAR, None, None)

    def search(self, value: str) -> int:
        current = self.head
        index = 0
        while current:
            if current.value == value:
                return index
            current = current.next
            index += 1
        return -1

    def _get_node(self, index: int) -> Node:
        if index < 0 or index >= self.length:
            raise IndexError("Index out of range")
        if index <= self.length // 2:
            current = self.head
            for _ in range(index):
                current = current.next
        else:
            current = self.tail
            for _ in range(self.length - 1 - index):
                current = current.prev
        return current

    def to_list(self) -> List[str]:
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

    def _record_operation(self, op_type: OperationType, value: Optional[str], index: Optional[int]) -> None:
        self.operation_history.append({
            "type": op_type,
            "value": value,
            "index": index,
            "timestamp": time.time(),
            "state": self.to_list()
        })

    def undo_last_operation(self) -> bool:
        if len(self.operation_history) <= 1:
            return False
        self.operation_history.pop()
        if len(self.operation_history) > 0:
            prev_state = self.operation_history[-1]["state"]
            self._load_from_list(prev_state)
            return True
        return False

    def _load_from_list(self, values: List[str]) -> None:
        self.head = self.tail = None
        self.length = 0
        for value in values:
            self.insert_at_tail(value)

# ==================== Visualization ====================
class LinkedListVisualizer:
    def __init__(self, canvas: tk.Canvas, linked_list: DoublyLinkedList):
        self.canvas = canvas
        self.linked_list = linked_list
        self.theme = Theme.LIGHT
        self.animation_settings = AnimationSettings()
        self._setup_theme()
        self.node_width = 120
        self.node_height = 80
        self.spacing = 150

    def _setup_theme(self) -> None:
        if self.theme == Theme.LIGHT:
            self.colors = {
                "normal": "#E1F5FE",
                "highlight": "#FFF9C4",
                "head": "#C8E6C9",
                "tail": "#FFCDD2",
                "arrow": "#757575",
                "prev_arrow": "#9E9E9E",
                "text": "#212121",
                "pointer_text": "#616161",
                "border": "#BDBDBD",
                "pointer_area": "#E0E0E0",
                "canvas_bg": "white"
            }
        elif self.theme == Theme.DARK:
            self.colors = {
                "normal": "#424242",
                "highlight": "#FFA000",
                "head": "#2E7D32",
                "tail": "#C62828",
                "arrow": "#9E9E9E",
                "prev_arrow": "#757575",
                "text": "#FAFAFA",
                "pointer_text": "#BDBDBD",
                "border": "#212121",
                "pointer_area": "#616161",
                "canvas_bg": "#303030"
            }
        elif self.theme == Theme.BLUE:
            self.colors = {
                "normal": "#E3F2FD",
                "highlight": "#B3E5FC",
                "head": "#BBDEFB",
                "tail": "#90CAF9",
                "arrow": "#42A5F5",
                "prev_arrow": "#1E88E5",
                "text": "#0D47A1",
                "pointer_text": "#1565C0",
                "border": "#1976D2",
                "pointer_area": "#BBDEFB",
                "canvas_bg": "#E3F2FD"
            }
        else:  # GREEN
            self.colors = {
                "normal": "#E8F5E9",
                "highlight": "#C8E6C9",
                "head": "#A5D6A7",
                "tail": "#81C784",
                "arrow": "#4CAF50",
                "prev_arrow": "#2E7D32",
                "text": "#1B5E20",
                "pointer_text": "#2E7D32",
                "border": "#43A047",
                "pointer_area": "#C8E6C9",
                "canvas_bg": "#E8F5E9"
            }
        self.canvas.config(bg=self.colors["canvas_bg"])

    def set_theme(self, theme: Theme) -> None:
        self.theme = theme
        self._setup_theme()
        self.draw()

    def set_animation_settings(self, settings: AnimationSettings) -> None:
        self.animation_settings = settings

    def draw(self, highlight_index: Union[int, List[int]] = -1) -> None:
        self.canvas.delete("all")
        current = self.linked_list.head
        x, y = 50, 150
        index = 0
        if isinstance(highlight_index, int):
            highlight_index = [highlight_index] if highlight_index != -1 else []
        while current:
            # Determine node color
            if index in highlight_index:
                color = self.colors["highlight"]
            elif index == 0:
                color = self.colors["head"]
            elif index == self.linked_list.length-1:
                color = self.colors["tail"]
            else:
                color = self.colors["normal"]
            # Draw the node
            self._draw_node(x, y, current, color, index in highlight_index)
            # Draw index label
            self._draw_index_label(x, y, index)
            # Draw connecting arrows
            if current.next:
                self._draw_arrow(
                    x + self.node_width,
                    y + self.node_height//2,
                    x + self.node_width + self.spacing//3,
                    y + self.node_height//2,
                    "next"
                )
            if current.prev:
                self._draw_arrow(
                    x - self.spacing//3,
                    y + self.node_height//2,
                    x,
                    y + self.node_height//2,
                    "prev"
                )
            x += self.node_width + self.spacing
            current = current.next
            index += 1
        # Draw list info
        self._draw_list_info()

    def _draw_node(self, x: int, y: int, node: Node, color: str, highlighted: bool) -> None:
        scale = 1.1 if highlighted else 1.0
        scaled_width = self.node_width * scale
        scaled_height = self.node_height * scale
        offset_x = (scaled_width - self.node_width) / 2
        offset_y = (scaled_height - self.node_height) / 2
        self.canvas.create_rectangle(
            x - offset_x, y - offset_y,
            x + scaled_width - offset_x, y + scaled_height - offset_y,
            fill=color, outline=self.colors["border"], width=2,
            tags=f"node_{node.id}"
        )
        self.canvas.create_text(
            x + self.node_width//2,
            y + 20,
            text=f"Data: {node.value}",
            font=("Arial", 10, "bold"),
            fill=self.colors["text"],
            tags=f"node_text_{node.id}"
        )
        self._draw_pointer_area(x, y, "next", node.next is not None, node.id)
        if node.prev is not None or self.linked_list.length > 1:
            self._draw_pointer_area(x, y, "prev", node.prev is not None, node.id)

    def _draw_pointer_area(self, x: int, y: int, pointer_type: str, has_connection: bool, node_id: int) -> None:
        if pointer_type == "next":
            y_pos = y + self.node_height - 25
            text = "Next: " + ("→" if has_connection else "NULL")
            tag = f"next_ptr_{node_id}"
        else:  # prev
            y_pos = y + self.node_height - 45
            text = "Prev: " + ("←" if has_connection else "NULL")
            tag = f"prev_ptr_{node_id}"
        self.canvas.create_rectangle(
            x, y_pos,
            x + self.node_width, y_pos + 20,
            fill=self.colors["pointer_area"], outline=self.colors["border"],
            tags=tag
        )
        self.canvas.create_text(
            x + self.node_width//2,
            y_pos + 10,
            text=text,
            font=("Consolas", 9),
            fill=self.colors["pointer_text"],
            tags=f"{tag}_text"
        )

    def _draw_index_label(self, x: int, y: int, index: int) -> None:
        self.canvas.create_text(
            x + self.node_width//2,
            y - 20,
            text=f"Index: {index}",
            fill=self.colors["pointer_text"],
            font=("Arial", 9),
            tags=f"index_label_{index}"
        )

    def _draw_arrow(self, x1: int, y1: int, x2: int, y2: int, arrow_type: str) -> None:
        arrow_shape = (9, 12, 6) if arrow_type == "next" else (6, 12, 9)
        arrow_pos = tk.LAST if arrow_type == "next" else tk.FIRST
        color = self.colors["arrow"] if arrow_type == "next" else self.colors["prev_arrow"]
        self.canvas.create_line(
            x1, y1, x2, y2,
            arrow=arrow_pos,
            width=3,
            fill=color,
            arrowshape=arrow_shape
        )

    def _draw_list_info(self) -> None:
        info_text = f"Length: {self.linked_list.length} | Head: {self.linked_list.head.value if self.linked_list.head else 'None'} | Tail: {self.linked_list.tail.value if self.linked_list.tail else 'None'}"
        self.canvas.create_text(
            10, 10,
            text=info_text,
            anchor=tk.NW,
            fill=self.colors["text"],
            font=("Arial", 10, "bold")
        )

    def animate_operation(self, highlight_indices: List[int], callback=None) -> None:
        for i in highlight_indices:
            self.draw([i])
            self.canvas.update()
            time.sleep(self.animation_settings.speed)
        self.draw()
        if callback:
            callback()

# ==================== Main Application ====================
class LinkedListApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ultimate Doubly Linked List Visualizer")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.linked_list = DoublyLinkedList()
        self.animation_settings = AnimationSettings()
        self.current_theme = Theme.LIGHT
        self._configure_styles()
        self._create_widgets()
        self._setup_layout()
        self._setup_bindings()
        self._setup_menu()
        self.update_display()
        self._add_sample_data()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", font=("Arial", 10))
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TButton", padding=6)
        style.configure("TEntry", padding=5)
        style.configure("Error.TEntry", foreground="red")
        style.map("Insert.TButton",
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', '#388E3C'), ('!disabled', '#4CAF50')]
        )
        style.map("Delete.TButton",
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', '#D32F2F'), ('!disabled', '#F44336')]
        )
        style.map("Search.TButton",
            foreground=[('active', 'white'), ('!disabled', 'black')],
            background=[('active', '#FFE082'), ('!disabled', '#FFC107')]
        )
        style.map("Clear.TButton",
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', '#616161'), ('!disabled', '#757575')]
        )
        style.map("Theme.TButton",
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', '#673AB7'), ('!disabled', '#7E57C2')]
        )

    def _create_widgets(self) -> None:
        self.main_frame = ttk.Frame(self.root)
        self.control_frame = ttk.Frame(self.main_frame)
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.sidebar_frame = ttk.Frame(self.main_frame)
        self.status_bar = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W)
        self.value_var = tk.StringVar()
        self.index_var = tk.StringVar()
        self.entry_frame = ttk.Frame(self.control_frame)
        self.value_label = ttk.Label(self.entry_frame, text="Value:")
        self.value_entry = ttk.Entry(self.entry_frame, textvariable=self.value_var, width=25)
        self.index_label = ttk.Label(self.entry_frame, text="Index:")
        self.index_entry = ttk.Entry(self.entry_frame, textvariable=self.index_var, width=8)
        self.btn_frame = ttk.Frame(self.control_frame)
        self.insert_head_btn = ttk.Button(
            self.btn_frame,
            text="Insert at Head",
            style="Insert.TButton",
            command=lambda: self._insert("head")
        )
        self.insert_tail_btn = ttk.Button(
            self.btn_frame,
            text="Insert at Tail",
            style="Insert.TButton",
            command=lambda: self._insert("tail")
        )
        self.insert_pos_btn = ttk.Button(
            self.btn_frame,
            text="Insert at Position",
            style="Insert.TButton",
            command=lambda: self._insert("position")
        )
        self.delete_btn = ttk.Button(
            self.btn_frame,
            text="Delete Position",
            style="Delete.TButton",
            command=self._delete
        )
        self.search_btn = ttk.Button(
            self.btn_frame,
            text="Search Value",
            style="Search.TButton",
            command=self._search
        )
        self.clear_btn = ttk.Button(
            self.btn_frame,
            text="Clear List",
            style="Clear.TButton",
            command=self._clear_list
        )
        self.undo_btn = ttk.Button(
            self.btn_frame,
            text="Undo",
            command=self._undo
        )
        self.ops_frame = ttk.Frame(self.control_frame)
        self.to_list_btn = ttk.Button(
            self.ops_frame,
            text="Show as Python List",
            command=self._show_as_list
        )
        self.from_list_btn = ttk.Button(
            self.ops_frame,
            text="Load from Python List",
            command=self._load_from_list
        )
        self.export_btn = ttk.Button(
            self.ops_frame,
            text="Export to JSON",
            command=self._export_to_json
        )
        self.import_btn = ttk.Button(
            self.ops_frame,
            text="Import from JSON",
            command=self._import_from_json
        )
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.visualizer = LinkedListVisualizer(self.canvas, self.linked_list)
        self.settings_frame = ttk.LabelFrame(self.sidebar_frame, text="Visual Settings")
        self.theme_var = tk.StringVar(value="light")
        self.theme_light_btn = ttk.Radiobutton(
            self.settings_frame, text="Light", variable=self.theme_var,
            value="light", command=lambda: self._change_theme(Theme.LIGHT)
        )
        self.theme_dark_btn = ttk.Radiobutton(
            self.settings_frame, text="Dark", variable=self.theme_var,
            value="dark", command=lambda: self._change_theme(Theme.DARK)
        )
        self.theme_blue_btn = ttk.Radiobutton(
            self.settings_frame, text="Blue", variable=self.theme_var,
            value="blue", command=lambda: self._change_theme(Theme.BLUE)
        )
        self.theme_green_btn = ttk.Radiobutton(
            self.settings_frame, text="Green", variable=self.theme_var,
            value="green", command=lambda: self._change_theme(Theme.GREEN)
        )
        self.animation_frame = ttk.LabelFrame(self.sidebar_frame, text="Animation Settings")
        self.anim_speed_scale = ttk.Scale(
            self.animation_frame, from_=0.1, to=1.0, value=0.2,
            command=lambda v: setattr(self.animation_settings, 'speed', float(v))
        )
        self.anim_speed_label = ttk.Label(self.animation_frame, text="Speed: 0.2")
        self.anim_physics_var = tk.BooleanVar(value=False)
        self.anim_physics_check = ttk.Checkbutton(
            self.animation_frame, text="Physics Effects",
            variable=self.anim_physics_var,
            command=lambda: setattr(self.animation_settings, 'enable_physics', self.anim_physics_var.get())
        )
        self.help_frame = ttk.LabelFrame(self.sidebar_frame, text="Help")
        self.help_text = tk.Text(
            self.help_frame, wrap=tk.WORD, height=10, width=30,
            bg="#f0f0f0", relief=tk.FLAT
        )
        self.help_text.insert(tk.END,
            "How to use:\n"
            "1. Enter value and click operation\n"
            "2. For position ops, specify index\n"
            "3. Use Undo to revert changes\n\n"
            "Shortcuts:\n"
            "Ctrl+Z: Undo\n"
            "Enter: Insert at position"
        )
        self.help_text.config(state=tk.DISABLED)
        self.docs_btn = ttk.Button(
            self.help_frame, text="Open Documentation",
            command=lambda: webbrowser.open("https://github.com/Vladislav-Karat/List-program.git")
        )

    def _setup_layout(self) -> None:
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.entry_frame.pack(fill=tk.X, pady=5)
        self.value_label.grid(row=0, column=0, padx=5, sticky="e")
        self.value_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.index_label.grid(row=0, column=2, padx=5, sticky="e")
        self.index_entry.grid(row=0, column=3, padx=5)
        self.entry_frame.grid_columnconfigure(1, weight=1)
        self.btn_frame.pack(fill=tk.X, pady=5)
        buttons = [
            self.insert_head_btn, self.insert_tail_btn,
            self.insert_pos_btn, self.delete_btn,
            self.search_btn, self.clear_btn, self.undo_btn
        ]
        for i, btn in enumerate(buttons):
            btn.grid(row=0, column=i, padx=3, sticky="ew")
        self.btn_frame.grid_columnconfigure(tuple(range(len(buttons))), weight=1)
        self.ops_frame.pack(fill=tk.X, pady=5)
        ops_buttons = [self.to_list_btn, self.from_list_btn, self.export_btn, self.import_btn]
        for i, btn in enumerate(ops_buttons):
            btn.grid(row=0, column=i, padx=3, sticky="ew")
        self.ops_frame.grid_columnconfigure(tuple(range(len(ops_buttons))), weight=1)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.settings_frame.pack(fill=tk.X, pady=5)
        self.theme_light_btn.pack(anchor=tk.W, pady=2)
        self.theme_dark_btn.pack(anchor=tk.W, pady=2)
        self.theme_blue_btn.pack(anchor=tk.W, pady=2)
        self.theme_green_btn.pack(anchor=tk.W, pady=2)
        self.animation_frame.pack(fill=tk.X, pady=5)
        self.anim_speed_label.pack(anchor=tk.W)
        self.anim_speed_scale.pack(fill=tk.X, pady=5)
        self.anim_physics_check.pack(anchor=tk.W)
        self.help_frame.pack(fill=tk.X, pady=5)
        self.help_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.docs_btn.pack(fill=tk.X, pady=(0, 5))

    def _setup_bindings(self) -> None:
        self.index_entry.configure(validate="key",
            validatecommand=(self.root.register(self._validate_index), "%P"))
        self.canvas.bind("<Configure>", self._update_scroll_region)
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.value_entry.bind("<Return>", lambda e: self._insert("position"))
        self.index_entry.bind("<Return>", lambda e: self._insert("position"))
        self.anim_speed_scale.bind("<Motion>", self._update_anim_speed_label)

    def _setup_menu(self) -> None:
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self._clear_list)
        file_menu.add_command(label="Open JSON...", command=self._import_from_json)
        file_menu.add_command(label="Save as JSON...", command=self._export_to_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Generate Sample Data", command=self._add_sample_data)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_radiobutton(label="Light Theme", variable=self.theme_var,
                                value="light", command=lambda: self._change_theme(Theme.LIGHT))
        view_menu.add_radiobutton(label="Dark Theme", variable=self.theme_var,
                                value="dark", command=lambda: self._change_theme(Theme.DARK))
        view_menu.add_radiobutton(label="Blue Theme", variable=self.theme_var,
                                value="blue", command=lambda: self._change_theme(Theme.BLUE))
        view_menu.add_radiobutton(label="Green Theme", variable=self.theme_var,
                                value="green", command=lambda: self._change_theme(Theme.GREEN))
        menubar.add_cascade(label="View", menu=view_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation",
                            command=lambda: webbrowser.open("https://github.com/Vladislav-Karat/List-program.git"))
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

    def _update_anim_speed_label(self, event=None) -> None:
        speed = round(self.anim_speed_scale.get(), 1)
        self.anim_speed_label.config(text=f"Speed: {speed}")
        self.animation_settings.speed = speed

    def _change_theme(self, theme: Theme) -> None:
        self.current_theme = theme
        self.visualizer.set_theme(theme)
        self.update_display()

    def _validate_index(self, text: str) -> bool:
        return text.isdigit() or text == ""

    def _update_scroll_region(self, event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _insert(self, position: str) -> None:
        value = self.value_var.get()
        index_str = self.index_var.get()
        try:
            if not value:
                raise ValueError("Please enter a value")
            if position == "head":
                self.linked_list.insert_at_head(value)
                highlight = [0]
            elif position == "tail":
                self.linked_list.insert_at_tail(value)
                highlight = [self.linked_list.length-1]
            elif position == "position":
                if not index_str:
                    raise ValueError("Index required for position insertion")
                index = int(index_str)
                self.linked_list.insert_at_position(index, value)
                highlight = [index]
            self.visualizer.animate_operation(highlight)
            self._update_status(f"Inserted '{value}' at {position} (index {highlight[0]})", "success")
            self.update_display()
        except Exception as e:
            self._update_status(str(e), "error")
            self._highlight_error_fields(position)

    def _delete(self) -> None:
        index_str = self.index_var.get()
        try:
            if not index_str:
                raise ValueError("Please enter an index to delete")
            index = int(index_str)
            value = self.linked_list.delete_at_position(index)
            highlight = []
            if index > 0:
                highlight.append(index-1)
            if index < self.linked_list.length:
                highlight.append(index)
            self.visualizer.animate_operation(highlight)
            self._update_status(f"Deleted value '{value}' at index {index}", "success")
            self.update_display()
        except Exception as e:
            self._update_status(str(e), "error")

    def _search(self) -> None:
        value = self.value_var.get()
        try:
            if not value:
                raise ValueError("Please enter a value to search")
            index = self.linked_list.search(value)
            if index == -1:
                self._update_status(f"Value '{value}' not found", "warning")
            else:
                self.visualizer.animate_operation([index])
                self._update_status(f"Found '{value}' at index {index}", "success")
            self.update_display()
        except Exception as e:
            self._update_status(str(e), "error")

    def _clear_list(self) -> None:
        if self.linked_list.length == 0:
            self._update_status("List is already empty", "info")
            return
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the list?"):
            self.linked_list.clear()
            self.update_display()
            self._update_status("List cleared successfully", "success")

    def _undo(self) -> None:
        if self.linked_list.undo_last_operation():
            self.update_display()
            self._update_status("Undo successful", "success")
        else:
            self._update_status("Nothing to undo", "info")

    def _show_as_list(self) -> None:
        py_list = self.linked_list.to_list()
        messagebox.showinfo("Python List", f"Current List:\n{py_list}")

    def _load_from_list(self) -> None:
        input_str = simpledialog.askstring("Load from List", "Enter a Python list (e.g. [1,2,3]):")
        if input_str:
            try:
                values = json.loads(input_str.replace("'", '"'))
                if not isinstance(values, list):
                    raise ValueError("Input is not a list")
                self.linked_list.clear()
                for v in values:
                    self.linked_list.insert_at_tail(str(v))
                self.update_display()
                self._update_status("Loaded from list successfully", "success")
            except Exception as e:
                self._update_status(f"Error loading list: {e}", "error")

    def _export_to_json(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                data = self.linked_list.to_list()
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self._update_status(f"Exported to {file_path}", "success")
            except Exception as e:
                self._update_status(f"Export failed: {e}", "error")

    def _import_from_json(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("JSON does not contain a list")
                self.linked_list.clear()
                for v in data:
                    self.linked_list.insert_at_tail(str(v))
                self.update_display()
                self._update_status(f"Imported from {file_path}", "success")
            except Exception as e:
                self._update_status(f"Import failed: {e}", "error")

    def _highlight_error_fields(self, position: str) -> None:
        if position in ("position", "head", "tail"):
            self.value_entry.configure(style="Error.TEntry")
        if position == "position":
            self.index_entry.configure(style="Error.TEntry")
        self.root.after(1000, self._reset_entry_styles)

    def _reset_entry_styles(self) -> None:
        self.value_entry.configure(style="TEntry")
        self.index_entry.configure(style="TEntry")

    def _update_status(self, message: str, status: str = "info") -> None:
        color = {
            "success": "#388E3C",
            "error": "#D32F2F",
            "warning": "#FFA000",
            "info": "#1976D2"
        }.get(status, "#1976D2")
        self.status_bar.config(text=message, foreground=color)

    def update_display(self) -> None:
        self.visualizer.set_animation_settings(self.animation_settings)
        self.visualizer.draw()
        self._update_scroll_region()

    def _add_sample_data(self) -> None:
        self.linked_list.clear()
        for v in ["A", "B", "C", "D"]:
            self.linked_list.insert_at_tail(v)
        self.update_display()
        self._update_status("Sample data loaded", "success")

    def _show_about(self) -> None:
        messagebox.showinfo(
            "HSE",
            "List Visualizer\n"
            "Author: Alexander Kalinin\n"
            "GitHub: https://github.com/Vladislav-Karat/List-program.git\n"
            "2025"
        )

# ==================== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ И РАСШИРЕНИЯ ====================

# --- Расширенная справка ---
extended_help = """
Ultimate Doubly Linked List Visualizer

Возможности:
- Вставка, удаление, поиск, очистка, undo, импорт/экспорт, история, темы, справка.
- Визуализация структуры и связей.
- Поддержка горячих клавиш.
- Генерация случайных данных.
- Сохранение и загрузка истории операций.

Горячие клавиши:
- Ctrl+Z — Undo
- Enter — Вставка по индексу

Рекомендации:
- Для вставки по индексу укажите значение и индекс.
- Для генерации случайных данных используйте соответствующую кнопку.
- Историю операций можно сохранить и загрузить через меню.
"""

def show_extended_help():
    """Показать расширенную справку."""
    messagebox.showinfo("Расширенная справка", extended_help)

# --- Дополнительные темы оформления ---
EXTRA_THEMES = {
    "PINK": {
        "normal": "#F8BBD0", "highlight": "#F06292", "head": "#F48FB1", "tail": "#EC407A",
        "arrow": "#AD1457", "prev_arrow": "#D81B60", "text": "#880E4F", "pointer_text": "#AD1457",
        "border": "#C2185B", "pointer_area": "#F8BBD0", "canvas_bg": "#FCE4EC"
    },
    "ORANGE": {
        "normal": "#FFE0B2", "highlight": "#FFB74D", "head": "#FFCC80", "tail": "#FF9800",
        "arrow": "#E65100", "prev_arrow": "#F57C00", "text": "#E65100", "pointer_text": "#F57C00",
        "border": "#FF9800", "pointer_area": "#FFE0B2", "canvas_bg": "#FFF3E0"
    },
    "GRAY": {
        "normal": "#CFD8DC", "highlight": "#B0BEC5", "head": "#90A4AE", "tail": "#78909C",
        "arrow": "#37474F", "prev_arrow": "#607D8B", "text": "#263238", "pointer_text": "#37474F",
        "border": "#78909C", "pointer_area": "#CFD8DC", "canvas_bg": "#ECEFF1"
    }
}

def add_extra_themes(visualizer):
    """Добавляет дополнительные темы оформления."""
    if not hasattr(visualizer, "extra_themes"):
        visualizer.extra_themes = {}
    visualizer.extra_themes.update(EXTRA_THEMES)

# --- Генерация случайных данных ---
def generate_random_data(linked_list, app):
    """Генерирует случайный список."""
    linked_list.clear()
    count = random.randint(5, 15)
    for _ in range(count):
        value = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        linked_list.insert_at_tail(value)
    app.update_display()
    app._update_status("Случайные данные сгенерированы", "success")

# --- Работа с историей операций ---
def clear_history(linked_list, app):
    """Очищает историю операций."""
    linked_list.operation_history.clear()
    app._update_status("История операций очищена", "info")

def save_history(linked_list, app):
    """Сохраняет историю операций в файл."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(linked_list.operation_history, f, ensure_ascii=False, indent=2)
        app._update_status(f"История сохранена в {file_path}", "success")

def load_history(linked_list, app):
    """Загружает историю операций из файла."""
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            linked_list.operation_history = json.load(f)
        if linked_list.operation_history:
            last_state = linked_list.operation_history[-1]["state"]
            linked_list._load_from_list(last_state)
        app.update_display()
        app._update_status(f"История загружена из {file_path}", "success")

# --- Добавление новых кнопок в интерфейс ---
def add_extra_buttons(app):
    """Добавляет дополнительные кнопки в сайдбар."""
    extra_frame = ttk.LabelFrame(app.sidebar_frame, text="Дополнительно")
    extra_frame.pack(fill=tk.X, pady=5)
    ttk.Button(extra_frame, text="Случайные данные", command=lambda: generate_random_data(app.linked_list, app)).pack(fill=tk.X, pady=2)
    ttk.Button(extra_frame, text="Очистить историю", command=lambda: clear_history(app.linked_list, app)).pack(fill=tk.X, pady=2)
    ttk.Button(extra_frame, text="Сохранить историю", command=lambda: save_history(app.linked_list, app)).pack(fill=tk.X, pady=2)
    ttk.Button(extra_frame, text="Загрузить историю", command=lambda: load_history(app.linked_list, app)).pack(fill=tk.X, pady=2)
    ttk.Button(extra_frame, text="Расширенная справка", command=show_extended_help).pack(fill=tk.X, pady=2)

    # Кнопки для новых тем
    theme_extra_frame = ttk.LabelFrame(app.sidebar_frame, text="Экстра темы")
    theme_extra_frame.pack(fill=tk.X, pady=5)
    ttk.Button(theme_extra_frame, text="Pink", command=lambda: app._change_theme(Theme("PINK"))).pack(fill=tk.X, pady=1)
    ttk.Button(theme_extra_frame, text="Orange", command=lambda: app._change_theme(Theme("ORANGE"))).pack(fill=tk.X, pady=1)
    ttk.Button(theme_extra_frame, text="Gray", command=lambda: app._change_theme(Theme("GRAY"))).pack(fill=tk.X, pady=1)

# --- Демонстрационные функции и заглушки для будущих фич ---
def future_feature_1():
    """Заглушка для будущей функции 1."""
    pass

def future_feature_2():
    """Заглушка для будущей функции 2."""
    pass

def future_feature_3():
    """Заглушка для будущей функции 3."""
    pass

# --- Пример использования классов и функций ---
def demo_usage():
    """Демонстрация использования DoublyLinkedList."""
    dll = DoublyLinkedList()
    dll.insert_at_head("A")
    dll.insert_at_tail("B")
    dll.insert_at_position(1, "C")
    print("Demo list:", dll.to_list())
    dll.delete_at_position(1)
    print("After delete:", dll.to_list())
    dll.clear()
    print("After clear:", dll.to_list())

# --- Псевдо-тесты (заглушки) ---
def test_insert():
    """Тест вставки."""
    pass

def test_delete():
    """Тест удаления."""
    pass

def test_search():
    """Тест поиска."""
    pass

def test_export_import():
    """Тест экспорта/импорта."""
    pass

"""
Этот файл содержит расширенную версию визуализатора двусвязного списка.
Добавлены дополнительные темы, справка, кнопки, заглушки для будущих функций,
и демонстрационные вызовы. Вы можете использовать этот шаблон для расширения
своих учебных или демонстрационных проектов.
"""

def main():
    root = tk.Tk()
    app = LinkedListApp(root)
    add_extra_themes(app.visualizer)
    add_extra_buttons(app)
    demo_usage()
    root.mainloop()

if __name__ == "__main__":
    main()