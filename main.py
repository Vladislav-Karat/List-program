import tkinter as tk
from tkinter import ttk, messagebox
import time

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insert_at_head(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1

    def insert_at_tail(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1

    def insert_at_position(self, index, value):
        if index < 0 or index > self.length:
            raise IndexError("Index out of range")
        
        if index == 0:
            self.insert_at_head(value)
        elif index == self.length:
            self.insert_at_tail(value)
        else:
            new_node = Node(value)
            current = self.head
            for _ in range(index-1):
                current = current.next
            new_node.next = current.next
            current.next = new_node
            self.length += 1

    def delete_at_position(self, index):
        if index < 0 or index >= self.length:
            raise IndexError("Index out of range")
        
        if index == 0:
            self.head = self.head.next
            if not self.head:
                self.tail = None
        else:
            current = self.head
            for _ in range(index-1):
                current = current.next
            current.next = current.next.next
            if index == self.length-1:
                self.tail = current
        self.length -= 1

    def clear(self):
        self.head = self.tail = None
        self.length = 0

    def search(self, value):
        current = self.head
        index = 0
        while current:
            if current.value == value:
                return index
            current = current.next
            index += 1
        return -1

    def get_node(self, index):
        if index < 0 or index >= self.length:
            return None
        current = self.head
        for _ in range(index):
            current = current.next
        return current

class LinkedListVisualizer:
    def __init__(self, canvas, linked_list):
        self.canvas = canvas
        self.linked_list = linked_list
        self.node_width = 100
        self.node_height = 60
        self.spacing = 120
        self.colors = {
            "normal": "#E1F5FE",
            "highlight": "#FFF9C4",
            "head": "#C8E6C9",
            "tail": "#FFCDD2",
            "arrow": "#757575"
        }
        self.current_highlight = None

    def draw(self, highlight_index=-1):
        self.canvas.delete("all")
        current = self.linked_list.head
        x, y = 50, 100
        index = 0
        
        while current:
            # Определить цвет узла
            if index == highlight_index:
                color = self.colors["highlight"]
            elif index == 0:
                color = self.colors["head"]
            elif index == self.linked_list.length-1:
                color = self.colors["tail"]
            else:
                color = self.colors["normal"]
            
            # Нарисуйте узлы и указатели
            self._draw_node(x, y, current.value, color)
            self._draw_pointers(x, y, current.next is not None)
            
            # Нарисуйте индексную метку
            self.canvas.create_text(
                x + self.node_width//2,
                y - 20,
                text=f"Index: {index}",
                fill="#616161",
                font=("Arial", 9))
            
            # Нарисуйте соединяющие стрелки
            if current.next:
                self._draw_arrow(
                    x + self.node_width, 
                    y + self.node_height//2, 
                    x + self.node_width + self.spacing//2, 
                    y + self.node_height//2
                )
            
            x += self.node_width + self.spacing
            current = current.next
            index += 1

    def _draw_node(self, x, y, value, color):
        # Контейнер узла
        self.canvas.create_rectangle(
            x, y, 
            x + self.node_width, y + self.node_height,
            fill=color, outline="#BDBDBD", width=2
        )
        
        # Отображение значения
        self.canvas.create_text(
            x + self.node_width//2, 
            y + 20,
            text="Data: " + str(value),
            font=("Arial", 10, "bold"),
            fill="#212121"
        )
        
    def _draw_pointers(self, x, y, has_next):
       # Следующая область указателя
        self.canvas.create_rectangle(
            x, y + self.node_height - 20,
            x + self.node_width, y + self.node_height,
            fill="#E0E0E0", outline="#BDBDBD"
        )
        
        # Следующая метка указателя
        self.canvas.create_text(
            x + self.node_width//2,
            y + self.node_height - 10,
            text="Next: " + ("→" if has_next else "NULL"),
            font=("Consolas", 9),
            fill="#616161"
        )

    def _draw_arrow(self, x1, y1, x2, y2):
        self.canvas.create_line(
            x1, y1, x2, y2,
            arrow=tk.LAST, 
            width=3,
            fill=self.colors["arrow"],
            arrowshape=(9, 12, 6)
        )

class LinkedListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Linked List Visualizer")
        self.root.geometry("1200x800")
        self._configure_styles()
        
        self.linked_list = SinglyLinkedList()
        self._create_widgets()
        self._setup_layout()
        self._setup_bindings()
        
        self.update_display()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, font=("Arial", 10))
        style.map("TButton",
            foreground=[('active', '!disabled', 'white')],
            background=[('active', '#616161')]
        )

    def _create_widgets(self):
        # Основные контейнеры
        self.control_frame = ttk.Frame(self.root)
        self.canvas_frame = ttk.Frame(self.root)
        self.status_bar = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W)
        
        # Управление виджетами
        self.value_var = tk.StringVar()
        self.index_var = tk.StringVar()
        
        self.entry_frame = ttk.Frame(self.control_frame)
        self.value_label = ttk.Label(self.entry_frame, text="Value:")
        self.value_entry = ttk.Entry(self.entry_frame, textvariable=self.value_var, width=20)
        self.index_label = ttk.Label(self.entry_frame, text="Index:")
        self.index_entry = ttk.Entry(self.entry_frame, textvariable=self.index_var, width=8)
        
        # Кнопки
        self.btn_frame = ttk.Frame(self.control_frame)
        self.insert_head_btn = ttk.Button(
            self.btn_frame, 
            text="Insert at Head", 
            command=lambda: self._insert("head")
        )
        self.insert_tail_btn = ttk.Button(
            self.btn_frame, 
            text="Insert at Tail", 
            command=lambda: self._insert("tail")
        )
        self.insert_pos_btn = ttk.Button(
            self.btn_frame, 
            text="Insert at Position", 
            command=lambda: self._insert("position")
        )
        self.delete_btn = ttk.Button(
            self.btn_frame,
            text="Delete Position",
            command=self._delete
        )
        self.search_btn = ttk.Button(
            self.btn_frame,
            text="Search Value",
            command=self._search
        )
        self.clear_btn = ttk.Button(
            self.btn_frame,
            text="Clear List",
            command=self._clear_list
        )

        # Холст с полосой прокрутки
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        
        self.visualizer = LinkedListVisualizer(self.canvas, self.linked_list)

    def _setup_layout(self):
        # Расположение управляющего фрейма
        self.control_frame.pack(pady=10, fill=tk.X)
        self.entry_frame.pack(pady=5, fill=tk.X)
        self.value_label.grid(row=0, column=0, padx=5)
        self.value_entry.grid(row=0, column=1, padx=5)
        self.index_label.grid(row=0, column=2, padx=5)
        self.index_entry.grid(row=0, column=3, padx=5)
        
        self.btn_frame.pack(pady=5)
        buttons = [
            self.insert_head_btn, self.insert_tail_btn, 
            self.insert_pos_btn, self.delete_btn,
            self.search_btn, self.clear_btn
        ]
        for i, btn in enumerate(buttons):
            btn.grid(row=0, column=i, padx=3)

        # Макет рамки для холста
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        
        # Строка состояния
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_bindings(self):
        self.index_entry.configure(validate="key", 
            validatecommand=(self.root.register(self._validate_index), "%P"))
        self.canvas.bind("<Configure>", self._update_scroll_region)

    def _validate_index(self, text):
        return text.isdigit() or text == ""

    def _update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _insert(self, position):
        value = self.value_var.get()
        index_str = self.index_var.get()
        
        try:
            if position == "head":
                self.linked_list.insert_at_head(value)
            elif position == "tail":
                self.linked_list.insert_at_tail(value)
            elif position == "position":
                if not index_str:
                    raise ValueError("Index required for position insertion")
                self.linked_list.insert_at_position(int(index_str), value)
            
            self._animate_insertion(position)
            self._update_status(f"Inserted '{value}' successfully", "success")
            self.update_display()
        except Exception as e:
            self._update_status(str(e), "error")
            self._highlight_error_fields(position)

    def _animate_insertion(self, position):
        for i in range(3):
            self.visualizer.draw(self._get_highlight_index(position))
            self.canvas.update()
            time.sleep(0.1)
            self.visualizer.draw()
            self.canvas.update()
            time.sleep(0.1)

    def _get_highlight_index(self, position):
        return {
            "head": 0,
            "tail": self.linked_list.length-1,
            "position": int(self.index_var.get()) if self.index_var.get() else 0
        }.get(position, -1)

    def _delete(self):
        index_str = self.index_var.get()
        try:
            if not index_str:
                raise ValueError("Please enter an index to delete")
            
            index = int(index_str)
            value = self.linked_list.get_node(index).value
            self.linked_list.delete_at_position(index)
            self._animate_deletion(index)
            self._update_status(f"Deleted value '{value}' at index {index}", "success")
            self.update_display()
        except Exception as e:
            self._update_status(str(e), "error")

    def _animate_deletion(self, index):
        for i in range(3):
            self.visualizer.draw(index)
            self.canvas.update()
            time.sleep(0.1)
            self.visualizer.draw()
            self.canvas.update()
            time.sleep(0.1)

    def _search(self):
        value = self.value_var.get()
        try:
            if not value:
                raise ValueError("Please enter a value to search")
            
            index = self.linked_list.search(value)
            if index == -1:
                self._update_status(f"Value '{value}' not found", "warning")
            else:
                self._animate_search(index)
                self._update_status(f"Found '{value}' at index {index}", "success")
            self.update_display()
        except Exception as e:
            self._update_status(str(e), "error")

    def _animate_search(self, index):
        for _ in range(3):
            self.visualizer.draw(index)
            self.canvas.update()
            time.sleep(0.2)
            self.visualizer.draw()
            self.canvas.update()
            time.sleep(0.2)

    def _clear_list(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the list?"):
            self.linked_list.clear()
            self.update_display()
            self._update_status("List cleared successfully", "success")

    def _highlight_error_fields(self, position):
        fields = []
        if not self.value_var.get():
            fields.append(self.value_entry)
        if position == "position" and not self.index_var.get():
            fields.append(self.index_entry)
        
        for field in fields:
            field.configure(style="Error.TEntry")
            self.root.after(2000, lambda: field.configure(style="TEntry"))

    def _update_status(self, message, status_type):
        colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "warning": "#FFC107",
            "info": "#2196F3"
        }
        self.status_bar.config(text=message, foreground=colors.get(status_type, "black"))

    def update_display(self):
        self.visualizer.draw()
        self._update_scroll_region()
        self.value_var.set("")
        self.index_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedListApp(root)
    root.mainloop()