import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import subprocess
import random
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        
        # Предопределённые задачи с категориями
        self.predefined_tasks = [
            {"task": "Прочитать статью", "category": "Учёба"},
            {"task": "Сделать зарядку", "category": "Спорт"},
            {"task": "Написать отчёт", "category": "Работа"},
            {"task": "Изучить новую тему", "category": "Учёба"},
            {"task": "Пробежать 3 км", "category": "Спорт"},
            {"task": "Проверить почту", "category": "Работа"}
        ]
        
        self.history = []
        self.current_tasks = self.predefined_tasks.copy()
        
        # Инициализация Git-репозитория
        self.init_git_repo()
        self.load_data()
        
        self.create_widgets()
        self.update_category_filter()
    
    def init_git_repo(self):
        """Инициализация Git‑репозитория, если его нет"""
        if not os.path.exists(".git"):
            try:
                subprocess.run(["git", "init"], check=True, capture_output=True)
                # Создаём .gitignore
                with open(".gitignore", "w") as f:
                    f.write("*.tmp\n*.log\n__pycache__/\n")
                subprocess.run(["git", "add", ".gitignore"], check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", "Initial commit: setup .gitignore"],
                             check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                messagebox.showwarning("Git не найден",
                                      "Git не установлен или не добавлен в PATH. Сохранение без версионирования.")
    
    def commit_to_git(self):
        """Коммит изменений в Git"""
        try:
            subprocess.run(["git", "add", "tasks_data.json"], check=True, capture_output=True)
            commit_msg = f"Update task history: {len(self.history)} entries"
            subprocess.run(["git", "commit", "-m", commit_msg],
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Игнорируем ошибки Git
    
    
    def create_widgets(self):
        # Фрейм для генерации задач
        generate_frame = ttk.LabelFrame(self.root, text="Генерация задач")
        generate_frame.pack(padx=10, pady=10, fill="x")
        
        self.generate_btn = ttk.Button(generate_frame, text="Сгенерировать задачу",
                                   command=self.generate_random_task)
        self.generate_btn.pack(pady=10)
        
        # Фрейм для добавления новых задач
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую задачу")
        add_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(add_frame, text="Задача:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.new_task_entry = ttk.Entry(add_frame, width=30)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar(value="Учёба")
        categories = ["Учёба", "Спорт", "Работа"]
        self.category_combo = ttk.Combobox(add_frame, textvariable=self.category_var,
                                           values=categories, state="readonly")
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)
        
        self.add_task_btn = ttk.Button(add_frame, text="Добавить задачу",
                               command=self.add_new_task)
        self.add_task_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_category = ttk.Combobox(filter_frame, state="readonly")
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)
        
        self.apply_filter_btn = ttk.Button(filter_frame, text="Применить фильтр",
                                 command=self.apply_filter)
        self.apply_filter_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр",
                                 command=self.clear_filter)
        self.clear_filter_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Фрейм для отображения истории
        history_frame = ttk.LabelFrame(self.root, text="История сгенерированных задач")
        history_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        columns = ("Время", "Задача", "Категория")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def validate_task_input(self, task_text):
        """Проверка корректности ввода задачи"""
        if not task_text.strip():
            messagebox.showerror("Ошибка", "Задача не может быть пустой")
            return False
        return True
    
    def add_new_task(self):
        """Добавление новой задачи в список"""
        task_text = self.new_task_entry.get().strip()
        category = self.category_var.get()
        if self.validate_task_input(task_text):
            new_task = {"task": task_text, "category": category}
            self.current_tasks.append(new_task)
            self.save_data()
            self.update_category_filter()
            self.new_task_entry.delete(0, tk.END)
            messagebox.showinfo("Успех", "Задача успешно добавлена")
    
    def generate_random_task(self):
        """Генерация случайной задачи и добавление в историю"""
        if not self.current_tasks:
            messagebox.showwarning("Предупреждение", "Нет задач для генерации")
            return
        random_task = random.choice(self.current_tasks)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "timestamp": timestamp,
            "task": random_task["task"],
            "category": random_task["category"]
        }
        self.history.append(history_entry)
        self.save_data()
        self.update_history_table()
        # Показываем сгенерированную задачу
        messagebox.showinfo("Сгенерированная задача",
                          f"Задача: {random_task['task']}\nКатегория: {random_task['category']}")
    def update_history_table(self, filtered_history=None):
        """Обновление таблицы истории"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        history_to_show = filtered_history if filtered_history is not None else self.history
        for entry in history_to_show:
            self.tree.insert("", "end", values=(
                entry["timestamp"],
                entry["task"],
                entry["category"]
            ))

    def apply_filter(self):
        """Применение фильтра по категории"""
        selected_category = self.filter_category.get()
        if selected_category == "Все категории" or not selected_category:
            self.update_history_table()
            return
        filtered = [entry for entry in self.history if entry["category"] == selected_category]
        self.update_history_table(filtered)

    def clear_filter(self):
        """Сброс фильтра"""
        self.filter_category.set("")
        self.update_history_table()

    def update_category_filter(self):
        """Обновление списка категорий в фильтре"""
        categories = sorted(set(task["category"] for task in self.current_tasks))
        self.filter_category["values"] = ["Все категории"] + categories
        if categories:
            self.filter_category.set("Все категории")

    def save_data(self):
        """Сохранение данных в JSON-файл с коммитом в Git"""
        data = {
            "tasks": self.current_tasks,
            "history": self.history
        }
        try:
            with open("tasks_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # Автокоммит в Git
            self.commit_to_git()
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузка данных из JSON-файла"""
        if os.path.exists("tasks_data.json"):
            try:
                with open("tasks_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.current_tasks = data.get("tasks", self.predefined_tasks)
                self.history = data.get("history", [])
                self.update_category_filter()
                self.update_history_table()
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                # Используем предопределённые задачи при ошибке загрузки
                self.current_tasks = self.predefined_tasks.copy()
                self.history = []

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x500")
    app = RandomTaskGenerator(root)
    root.mainloop()
