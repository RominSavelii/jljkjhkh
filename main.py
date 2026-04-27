import tkinter as tk
from tkinter import messagebox
import json
import os

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.tasks = []
        self.load_tasks()
        self.create_widgets()

    def create_widgets(self):
        # Поле ввода
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=10)

        # Кнопка добавления
        self.add_btn = tk.Button(root, text="Добавить", command=self.add_task)
        self.add_btn.pack()

        # Список задач (Listbox + Scrollbar)
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=15)
        self.scrollbar = tk.Scrollbar(root)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления
        self.frame_buttons = tk.Frame(root)
        self.complete_btn = tk.Button(self.frame_buttons, text="Отметить как выполненное", command=self.mark_completed)
        self.delete_btn = tk.Button(self.frame_buttons, text="Удалить", command=self.delete_task)
        self.save_btn = tk.Button(self.frame_buttons, text="Сохранить", command=self.save_tasks)

        self.complete_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.frame_buttons.pack(pady=10)

        self.update_listbox()

    def add_task(self):
        task_text = self.entry.get().strip()
        if task_text:
            new_task = {"id": len(self.tasks) + 1, "text": task_text, "completed": False}
            self.tasks.append(new_task)
            self.entry.delete(0, tk.END)
            self.update_listbox()
            self.save_tasks()

    def mark_completed(self):
        selected_indices = self.listbox.curselection()
        for index in reversed(selected_indices):
            self.tasks[index]["completed"] = True
        self.update_listbox()
        self.save_tasks()

    def delete_task(self):
        selected_indices = self.listbox.curselection()
        for index in reversed(selected_indices):
            del self.tasks[index]
        self.update_listbox()
        self.save_tasks()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            display_text = task["text"]
            if task["completed"]:
                display_text = f"[ВЫПОЛНЕНО] {display_text}"
            self.listbox.insert(tk.END, display_text)

    def save_tasks(self):
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить задачи. Используется пустой список.")
                self.tasks = []

# Запуск приложения
root = tk.Tk()
app = TaskManager(root)
root.mainloop()
