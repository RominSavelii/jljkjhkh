import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
from datetime import datetime

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.movies = []
        self.filtered_movies = []
        
        # Инициализация Git-репозитория при первом запуске
        self.init_git_repo()
        self.load_movies()
        
        self.create_widgets()
        self.update_table()
        self.update_genre_filter()
    
    def init_git_repo(self):
        """Инициализация Git‑репозитория, если его нет"""
        if not os.path.exists(".git"):
            try:
                subprocess.run(["git", "init"], check=True, capture_output=True)
                # Создаём .gitignore для исключения временных файлов
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
            subprocess.run(["git", "add", "movies.json"], check=True, capture_output=True)
            commit_msg = f"Update movie library: {len(self.movies)} movies"
            subprocess.run(["git", "commit", "-m", commit_msg],
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Игнорируем ошибки Git — приложение продолжит работу
    
    def create_widgets(self):
        # Фрейм для формы добавления
        form_frame = ttk.LabelFrame(self.root, text="Добавить фильм")
        form_frame.pack(padx=10, pady=10, fill="x")
        
        # Поля формы
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Жанр:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.genre_entry = ttk.Entry(form_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Год выпуска:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.year_entry = ttk.Entry(form_frame, width=30)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Рейтинг (0–10):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.rating_entry = ttk.Entry(form_frame, width=30)
        self.rating_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(form_frame, text="Добавить фильм", command=self.add_movie)
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.genre_filter = ttk.Combobox(filter_frame, state="readonly")
        self.genre_filter.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Год:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.year_filter = ttk.Entry(filter_frame, width=10)
        self.year_filter.grid(row=0, column=3, padx=5, pady=5)
        
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=5, pady=5)
        
        self.clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        self.clear_filter_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Таблица
        table_frame = ttk.Frame(self.root)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def validate_input(self, title, genre, year_str, rating_str):
        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр обязательны для заполнения")
            return False
        try:
            year = int(year_str)
            if year < 1888 or year > datetime.now().year:  # Первый фильм — 1888 г.
                messagebox.showerror("Ошибка", "Год должен быть от 1888 до текущего года")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом")
            return False
        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом")
            return False
        return True
    
    def add_movie(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()
        if self.validate_input(title, genre, year_str, rating_str):
            movie = {
                "title": title,
                "genre": genre,
                "year": int(year_str),
                "rating": float(rating_str)
            }
            self.movies.append(movie)
            self.save_movies()
            self.update_table()
            self.update_genre_filter()
            # Очистка полей ввода
            self.title_entry.delete(0, tk.END)
            self.genre_entry.delete(0, tk.END)
            self.year_entry.delete(self.year_entry.delete(0, tk.END)
            self.rating_entry.delete(0, tk.END)
    
    def update_genre_filter(self):
        """Обновление списка жанров в фильтре"""
        genres = sorted(set(movie["genre"] for movie in self.movies))
        self.genre_filter["values"] = ["Все жанры"] + genres
        if genres:
            self.genre_filter.set("Все жанры")
    
    def apply_filter(self):
        """Применение фильтров к таблице"""
        selected_genre = self.genre_filter.get()
        year_filter = self.year_filter.get().strip()
        filtered = self.movies.copy()
        # Фильтрация по жанру
        if selected_genre and selected_genre != "Все жанры":
            filtered = [movie for movie in filtered if movie["genre"] == selected_genre]
        # Фильтрация по году
        if year_filter:
            try:
                year = int(year_filter)
                filtered = [movie for movie in filtered if movie["year"] == year]
            except ValueError:
                messagebox.showerror("Ошибка", "Год для фильтрации должен быть числом")
                return
        self.update_table(filtered)
    
    def clear_filter(self):
        """Сброс фильтров"""
        self.genre_filter.set("")
        self.year_filter.delete(0, tk.END)
        self.update_table()
    
    def load_movies(self):
        """Загрузка фильмов из JSON-файла"""
        if os.path.exists("movies.json"):
            try:
                with open("movies.json", "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
                self.update_genre_filter()
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.movies = []
    
    def save_movies(self):
        """Сохранение фильмов в JSON-файл с коммитом в Git"""
        try:
            with open("movies.json", "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
            # Автокоммит в Git
            self.commit_to_git()
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()
