import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # Added simpledialog import
import time
from typing import Optional

class Node:
    def __init__(self, value):
        self.value = value
        self.next: Optional[Node] = None
        self.prev: Optional[Node] = None

class DoublyLinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.length = 0

    def insert_at_head(self, value) -> None:
        new_node = Node(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.length += 1

    def insert_at_tail(self, value) -> None:
        new_node = Node(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1

    def insert_at_position(self, index: int, value) -> None:
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

    def delete_at_position(self, index: int) -> None:
        if index < 0 or index >= self.length:
            raise IndexError("Index out of range")
        
        if self.length == 1:
            self.head = self.tail = None
        elif index == 0:
            self.head = self.head.next
            self.head.prev = None
        elif index == self.length - 1:
            self.tail = self.tail.prev
            self.tail.next = None
        else:
            current = self._get_node(index)
            current.prev.next = current.next
            current.next.prev = current.prev
            
        self.length -= 1

    def clear(self) -> None:
        self.head = self.tail = None
        self.length = 0

    def search(self, value) -> int:
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

    def to_list(self) -> list:
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

class LinkedListVisualizer:
    def __init__(self, canvas, linked_list):
        self.canvas = canvas
        self.linked_list = linked_list
        self.node_width = 120
        self.node_height = 80
        self.spacing = 150
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
            "pointer_area": "#E0E0E0"
        }
        self.current_highlight = None
        self.animation_speed = 0.2

    def draw(self, highlight_index=-1) -> None:
        self.canvas.delete("all")
        current = self.linked_list.head
        x, y = 50, 150
        index = 0
        
        while current:
            # Determine node color
            if index == highlight_index:
                color = self.colors["highlight"]
            elif index == 0:
                color = self.colors["head"]
            elif index == self.linked_list.length-1:
                color = self.colors["tail"]
            else:
                color = self.colors["normal"]
            
            # Draw the node
            self._draw_node(x, y, current, color)
            
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

    def _draw_node(self, x: int, y: int, node: Node, color: str) -> None:
        # Main node container
        self.canvas.create_rectangle(
            x, y, 
            x + self.node_width, y + self.node_height,
            fill=color, outline=self.colors["border"], width=2
        )
        
        # Value display
        self.canvas.create_text(
            x + self.node_width//2, 
            y + 20,
            text=f"Data: {node.value}",
            font=("Arial", 10, "bold"),
            fill=self.colors["text"]
        )
        
        # Next pointer area
        self._draw_pointer_area(x, y, "next", node.next is not None)
        
        # Prev pointer area (only if exists)
        if node.prev is not None or self.linked_list.length > 1:
            self._draw_pointer_area(x, y, "prev", node.prev is not None)

    def _draw_pointer_area(self, x: int, y: int, pointer_type: str, has_connection: bool) -> None:
        if pointer_type == "next":
            y_pos = y + self.node_height - 25
            text = "Next: " + ("→" if has_connection else "NULL")
        else:  # prev
            y_pos = y + self.node_height - 45
            text = "Prev: " + ("←" if has_connection else "NULL")
        
        self.canvas.create_rectangle(
            x, y_pos,
            x + self.node_width, y_pos + 20,
            fill=self.colors["pointer_area"], outline=self.colors["border"]
        )
        
        self.canvas.create_text(
            x + self.node_width//2,
            y_pos + 10,
            text=text,
            font=("Consolas", 9),
            fill=self.colors["pointer_text"]
        )

    def _draw_index_label(self, x: int, y: int, index: int) -> None:
        self.canvas.create_text(
            x + self.node_width//2,
            y - 20,
            text=f"Index: {index}",
            fill=self.colors["pointer_text"],
            font=("Arial", 9)
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

    def animate_operation(self, highlight_indices: list, callback=None) -> None:
        for i in highlight_indices:
            self.draw(i)
            self.canvas.update()
            time.sleep(self.animation_speed)
        
        self.draw()
        if callback:
            callback()

class LinkedListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doubly Linked List Visualizer")
        self.root.geometry("1300x800")
        self._configure_styles()
        
        self.linked_list = DoublyLinkedList()
        self._create_widgets()
        self._setup_layout()
        self._setup_bindings()
        
        self.update_display()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure main styles
        style.configure("TButton", padding=6, font=("Arial", 10))
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        
        # Colorful button styles
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
        
        # Entry styles
        style.configure("TEntry", padding=5)
        style.configure("Error.TEntry", foreground="red")

    def _create_widgets(self) -> None:
        # Main containers
        self.control_frame = ttk.Frame(self.root)
        self.canvas_frame = ttk.Frame(self.root)
        self.status_bar = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W)
        
        # Control widgets
        self.value_var = tk.StringVar()
        self.index_var = tk.StringVar()
        
        self.entry_frame = ttk.Frame(self.control_frame)
        self.value_label = ttk.Label(self.entry_frame, text="Value:")
        self.value_entry = ttk.Entry(self.entry_frame, textvariable=self.value_var, width=25)
        self.index_label = ttk.Label(self.entry_frame, text="Index:")
        self.index_entry = ttk.Entry(self.entry_frame, textvariable=self.index_var, width=8)
        
        # Buttons with styled categories
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
        
        # List operations frame
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
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        
        self.visualizer = LinkedListVisualizer(self.canvas, self.linked_list)

    def _setup_layout(self) -> None:
        # Control frame layout
        self.control_frame.pack(pady=10, fill=tk.X, padx=10)
        
        # Entry frame
        self.entry_frame.pack(pady=5, fill=tk.X)
        self.value_label.grid(row=0, column=0, padx=5, sticky="e")
        self.value_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.index_label.grid(row=0, column=2, padx=5, sticky="e")
        self.index_entry.grid(row=0, column=3, padx=5)
        self.entry_frame.grid_columnconfigure(1, weight=1)
        
        # Button frame
        self.btn_frame.pack(pady=5, fill=tk.X)
        buttons = [
            self.insert_head_btn, self.insert_tail_btn, 
            self.insert_pos_btn, self.delete_btn,
            self.search_btn, self.clear_btn
        ]
        for i, btn in enumerate(buttons):
            btn.grid(row=0, column=i, padx=3, sticky="ew")
        self.btn_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        
        # Operations frame
        self.ops_frame.pack(pady=5, fill=tk.X)
        self.to_list_btn.grid(row=0, column=0, padx=3, sticky="ew")
        self.from_list_btn.grid(row=0, column=1, padx=3, sticky="ew")
        self.ops_frame.grid_columnconfigure((0,1), weight=1)
        
        # Canvas frame layout
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        
        # Status bar
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_bindings(self) -> None:
        self.index_entry.configure(validate="key", 
            validatecommand=(self.root.register(self._validate_index), "%P"))
        self.canvas.bind("<Configure>", self._update_scroll_region)
        
        # Bind Enter key to insert at position
        self.value_entry.bind("<Return>", lambda e: self._insert("position"))
        self.index_entry.bind("<Return>", lambda e: self._insert("position"))

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
            value = self.linked_list._get_node(index).value
            self.linked_list.delete_at_position(index)
            
            # Animate deletion by highlighting surrounding nodes
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

    def _show_as_list(self) -> None:
        py_list = self.linked_list.to_list()
        messagebox.showinfo("List Contents", f"Current list as Python list:\n\n{py_list}")

    def _load_from_list(self) -> None:
        input_str = simpledialog.askstring("Load from List", "Enter Python list (e.g., [1, 2, 3]):")
        if input_str:
            try:
                # Simple evaluation (in real app, use ast.literal_eval or proper parsing)
                if not (input_str.startswith('[') and input_str.endswith(']')):
                    raise ValueError("Invalid list format - must be enclosed in []")
                
                elements = [e.strip() for e in input_str[1:-1].split(',') if e.strip()]
                
                self.linked_list.clear()
                for element in elements:
                    self.linked_list.insert_at_tail(element)
                
                self.update_display()
                self._update_status(f"Loaded {len(elements)} elements from list", "success")
            except Exception as e:
                self._update_status(f"Error loading list: {str(e)}", "error")

    def _highlight_error_fields(self, position: str) -> None:
        fields = []
        if not self.value_var.get():
            fields.append(self.value_entry)
        if position == "position" and not self.index_var.get():
            fields.append(self.index_entry)
        
        for field in fields:
            field.configure(style="Error.TEntry")
            self.root.after(2000, lambda: field.configure(style="TEntry"))

    def _update_status(self, message: str, status_type: str) -> None:
        colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "warning": "#FFC107",
            "info": "#2196F3"
        }
        self.status_bar.config(
            text=message, 
            foreground="white",
            background=colors.get(status_type, "black"),
            font=("Arial", 10)
        )

    def update_display(self) -> None:
        self.visualizer.draw()
        self._update_scroll_region()
        self.value_var.set("")
        self.index_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedListApp(root)
    root.mainloop()