import os
import shutil
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from openpyxl import load_workbook
import hashlib
import shutil
from collections import defaultdict

class FileDatabase:
    def __init__(self, filename, key_fields):
        self.filename = filename
        self.key_fields = key_fields
        self.fields = []
        self.hash_table = {}  # Хранение записей в хеш-таблице
        self.load_or_create_db()

    def load_or_create_db(self):
        """Загрузка базы данных из файла или создание новой."""
        if os.path.exists(self.filename):
            try:
                df = pd.read_excel(self.filename, engine='openpyxl')
                self.fields = df.columns.tolist()
                if not set(self.key_fields).issubset(self.fields):
                    raise ValueError("Ключевые поля отсутствуют в заголовках базы данных.")
                # Загрузка данных в хеш-таблицу
                for _, row in df.iterrows():
                    key = self._generate_key(row)
                    self.hash_table[key] = row.to_dict()
            except Exception as e:
                raise ValueError(f"Не удалось загрузить базу данных: {e}")
        else:
            self.fields = self.key_fields.copy()
            self.hash_table = {}

    def save(self):
        """Сохранение базы данных в файл."""
        df = self.to_dataframe()
        try:
            df.to_excel(self.filename, index=False, engine='openpyxl')
        except PermissionError:
            raise PermissionError(f"Ошибка доступа: невозможно сохранить файл {self.filename}.")
        except Exception as e:
            raise Exception(f"Ошибка при сохранении файла: {e}")

    def to_dataframe(self):
        """Преобразует данные из хеш-таблицы в pandas DataFrame."""
        if not self.hash_table:
            return pd.DataFrame(columns=self.fields)
        return pd.DataFrame(self.hash_table.values())


    def _generate_key(self, record):
        """Генерирует уникальный ключ на основе ключевых полей."""
        return tuple(record[field] for field in self.key_fields)

    def add_record(self, record):
        """Добавление новой записи."""
        key = self._generate_key(record)
        if key in self.hash_table:
            raise ValueError("Запись с таким ключом уже существует.")
        self.hash_table[key] = record

    def search_records(self, key_values):
        """Поиск записи по ключу."""
        key = tuple(key_values)
        if key in self.hash_table:
            return self.hash_table[key]
        raise ValueError("Запись с таким ключом не найдена.")

    def delete_records(self, field=None, value=None, key_values=None):
        """Удаление записи по ключу или по полю и значению."""
        if key_values:
            # Удаление по ключу
            key = tuple(key_values)
            if key in self.hash_table:
                del self.hash_table[key]
            else:
                raise ValueError("Запись с таким ключом не найдена.")
        elif field and value:
            # Удаление по полю и значению
            to_delete = [key for key, record in self.hash_table.items() if record.get(field) == value]
            if not to_delete:
                raise ValueError(f"Нет записей для удаления по значению '{value}' в поле '{field}'.")
            for key in to_delete:
                del self.hash_table[key]
        else:
            raise ValueError("Недостаточно аргументов для удаления.")


    def edit_record(self, key_values, new_record):
        """Редактирование существующей записи."""
        key = tuple(key_values)
        if key not in self.hash_table:
            raise ValueError("Запись для редактирования не найдена.")
        # Удаляем старую запись, если ключ изменяется
        old_record = self.hash_table[key]
        new_key = self._generate_key(new_record)
        if new_key != key and new_key in self.hash_table:
            raise ValueError("Запись с новым ключом уже существует.")
        del self.hash_table[key]
        self.hash_table[new_key] = new_record
    
    def clear_database(self):
        """Очистка базы данных."""
        self.hash_table.clear()
        self.save()
    
    def backup(self, backup_filename):
        """Создание backup-файла БД."""
        try:
            shutil.copyfile(self.filename, backup_filename)
        except Exception as e:
            raise Exception(f"Не удалось создать backup: {e}")

    def restore(self, backup_filename):
        """Восстановление БД из backup-файла."""
        if not os.path.exists(backup_filename):
            raise FileNotFoundError(f"Файл backup не найден: {backup_filename}")
        try:
            shutil.copyfile(backup_filename, self.filename)
            self.load_or_create_db()
        except Exception as e:
            raise Exception(f"Не удалось восстановить базу данных из backup: {e}")
    
    def import_from_xlsx(self, import_filename):
        """Импорт данных из файла XLSX в базу данных."""
        if not os.path.exists(import_filename):
            raise FileNotFoundError(f"Файл для импорта не найден: {import_filename}")
        try:
            df_import = pd.read_excel(import_filename, engine='openpyxl')
            for _, row in df_import.iterrows():
                record = row.to_dict()
                try:
                    self.add_record(record)
                except ValueError:
                    # Если запись с таким ключом уже существует, можно обновить или пропустить
                    pass  # Здесь пропускаем дубликаты
            self.save()
        except Exception as e:
            raise Exception(f"Не удалось импортировать данные из XLSX: {e}")

    def export_to_xlsx(self, export_filename):
        """Экспорт данных базы данных в файл XLSX."""
        try:
            df = self.to_dataframe()
            df.to_excel(export_filename, index=False, engine='openpyxl')
        except Exception as e:
            raise Exception(f"Не удалось экспортировать данные в XLSX: {e}")

class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Файловая База Данных")
        self.db = None
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Создать БД", command=self.create_db)
        filemenu.add_command(label="Открыть БД", command=self.open_db)
        filemenu.add_command(label="Удалить БД", command=self.delete_db)
        filemenu.add_command(label="Очистить БД", command=self.clear_db)
        filemenu.add_command(label="Сохранить БД", command=self.save_db)
        filemenu.add_command(label="Импорт из XLSX", command=self.import_from_xlsx)
        filemenu.add_command(label="Экспорт в XLSX", command=self.export_to_xlsx)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=filemenu)

        backupmenu = tk.Menu(menubar, tearoff=0)
        backupmenu.add_command(label="Создать Backup", command=self.create_backup)
        backupmenu.add_command(label="Восстановить из Backup", command=self.restore_backup)
        menubar.add_cascade(label="Backup", menu=backupmenu)

        self.root.config(menu=menubar)

        operation_frame = tk.Frame(self.root)
        operation_frame.pack(pady=10)

        tk.Button(operation_frame, text="Добавить", command=self.add_record).grid(row=0, column=0, padx=5)
        tk.Button(operation_frame, text="Удалить", command=self.delete_record).grid(row=0, column=1, padx=5)
        tk.Button(operation_frame, text="Поиск", command=self.search_records).grid(row=0, column=2, padx=5)
        tk.Button(operation_frame, text="Редактировать", command=self.edit_record).grid(row=0, column=3, padx=5)

        self.tree = ttk.Treeview(self.root, show='headings', selectmode='browse')
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tree.bind("<Control-c>", self.copy_selected)
        self.tree.bind("<Control-C>", self.copy_selected)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_selected)

    def show_context_menu(self, event):
        selected = self.tree.identify_row(event.y)
        if selected:
            self.tree.selection_set(selected)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected(self, event=None):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            text = '\t'.join(str(v) for v in values)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Копирование", "Запись скопирована в буфер обмена.")
        else:
            messagebox.showwarning("Копирование", "Нет выделенной записи для копирования.")

    def create_db(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx")],
                                                title="Создать новую базу данных")
        if filename:
            fields = self.get_fields_dialog()
            if not fields:
                messagebox.showerror("Ошибка", "Не заданы заголовки полей.")
                return
            key_fields = self.get_key_fields_dialog(fields)
            if not key_fields:
                messagebox.showerror("Ошибка", "Не заданы ключевые поля.")
                return
            try:
                self.db = FileDatabase(filename, key_fields)
                self.db.fields = fields
                self.db.save()
                self.refresh_table()
                messagebox.showinfo("Создание БД", "База данных успешно создана.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать базу данных: {e}")

    def open_db(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")],
                                              title="Открыть базу данных")
        if filename:
            try:
                self.db = FileDatabase(filename, [])
                with pd.ExcelFile(filename, engine='openpyxl') as xls:
                    df = pd.read_excel(xls, sheet_name=0)
                    fields = df.columns.tolist()
                key_fields = self.get_key_fields_dialog(fields)
                if not key_fields:
                    messagebox.showerror("Ошибка", "Не заданы ключевые поля.")
                    return
                if not set(key_fields).issubset(fields):
                    messagebox.showerror("Ошибка", "Ключевые поля отсутствуют в заголовках файла.")
                    return
                self.db = FileDatabase(filename, key_fields)
                self.refresh_table()
                messagebox.showinfo("Открытие БД", "База данных успешно открыта.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть базу данных: {e}")

    def delete_db(self):
        if self.db:
            if messagebox.askyesno("Удаление БД", f"Удалить базу данных {os.path.basename(self.db.filename)}?"):
                try:
                    os.remove(self.db.filename)
                    self.db = None
                    self.refresh_table()
                    messagebox.showinfo("Удаление БД", "База данных успешно удалена.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить базу данных: {e}")
        else:
            messagebox.showwarning("Удаление БД", "Нет открытой базы данных.")

    def clear_db(self):
        if self.db:
            if messagebox.askyesno("Очистка БД", "Очистить базу данных?"):
                try:
                    self.db.clear_database()
                    self.refresh_table()
                    messagebox.showinfo("Очистка БД", "База данных очищена.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось очистить базу данных: {e}")
        else:
            messagebox.showwarning("Очистка БД", "Нет открытой базы данных.")

    def save_db(self):
        if self.db:
            try:
                self.db.save()
                messagebox.showinfo("Сохранение БД", "База данных успешно сохранена.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить базу данных: {e}")
        else:
            messagebox.showwarning("Сохранение БД", "Нет открытой базы данных.")

    def create_backup(self):
        if self.db:
            backup_filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                           filetypes=[("Excel files", "*.xlsx")],
                                                           title="Создать Backup")
            if backup_filename:
                try:
                    self.db.backup(backup_filename)
                    messagebox.showinfo("Backup", "Backup успешно создан.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось создать backup: {e}")
        else:
            messagebox.showwarning("Backup", "Нет открытой базы данных.")

    def restore_backup(self):
        if self.db:
            backup_filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")],
                                                         title="Восстановить из Backup")
            if backup_filename:
                try:
                    self.db.restore(backup_filename)
                    self.refresh_table()
                    messagebox.showinfo("Restore", "База данных успешно восстановлена из backup.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось восстановить из backup: {e}")
        else:
            messagebox.showwarning("Restore", "Нет открытой базы данных.")

    def import_from_xlsx(self):
        if not self.db:
            messagebox.showwarning("Импорт из XLSX", "Нет открытой базы данных.")
            return
        import_filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")],
                                                     title="Импорт из XLSX")
        if import_filename:
            try:
                self.db.import_from_xlsx(import_filename)
                self.refresh_table()
                messagebox.showinfo("Импорт из XLSX", "Импорт успешно выполнен.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {e}")

    def export_to_xlsx(self):
        if not self.db:
            messagebox.showwarning("Экспорт в XLSX", "Нет открытой базы данных.")
            return
        export_filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                       filetypes=[("Excel files", "*.xlsx")],
                                                       title="Экспорт в XLSX")
        if export_filename:
            try:
                self.db.export_to_xlsx(export_filename)
                messagebox.showinfo("Экспорт в XLSX", "Экспорт успешно выполнен.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")

    def add_record(self):
        if not self.db:
            messagebox.showwarning("Добавление", "Нет открытой базы данных.")
            return
        AddEditWindow(self, "Добавить Запись")

    def delete_record(self):
        if not self.db:
            messagebox.showwarning("Удаление", "Нет открытой базы данных.")
            return
        DeleteWindow(self)

    def search_records(self):
        if not self.db:
            messagebox.showwarning("Поиск", "Нет открытой базы данных.")
            return
        SearchWindow(self)

    def edit_record(self):
        if not self.db:
            messagebox.showwarning("Редактирование", "Нет открытой базы данных.")
            return
        EditWindow(self)

    def refresh_table(self, df=None):
        """Обновляет данные в таблице GUI."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.db:
            try:
                self.tree["columns"] = self.db.fields
                for col in self.db.fields:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, width=100, anchor='center')
                display_df = df if df is not None else self.db.to_dataframe()
                for _, row in display_df.iterrows():
                    values = [row.get(field, "") for field in self.db.fields]
                    self.tree.insert('', 'end', values=values)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить таблицу: {e}")

    def get_fields_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ввод Заголовков Полей")
        tk.Label(dialog, text="Введите заголовки полей через запятую:").pack(pady=5)
        entry = tk.Entry(dialog, width=50)
        entry.pack(pady=5)

        fields = []

        def submit():
            nonlocal fields
            input_text = entry.get().strip()
            if not input_text:
                messagebox.showerror("Ошибка", "Заголовки не могут быть пустыми.")
                return
            fields = [field.strip() for field in input_text.split(',') if field.strip()]
            if not fields:
                messagebox.showerror("Ошибка", "Необходимо указать хотя бы одно поле.")
                return
            dialog.destroy()

        tk.Button(dialog, text="OK", command=submit).pack(pady=5)
        self.root.wait_window(dialog)
        return fields

    def get_key_fields_dialog(self, available_fields):
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор Ключевых Полей")
        tk.Label(dialog, text="Выберите ключевые поля:").pack(pady=5)
        listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE, width=50)
        for field in available_fields:
            listbox.insert(tk.END, field)
        listbox.pack(pady=5)

        key_fields = []

        def submit():
            nonlocal key_fields
            selected_indices = listbox.curselection()
            key_fields = [available_fields[i] for i in selected_indices]
            if not key_fields:
                messagebox.showerror("Ошибка", "Необходимо выбрать хотя бы одно ключевое поле.")
                return
            dialog.destroy()

        tk.Button(dialog, text="OK", command=submit).pack(pady=5)
        self.root.wait_window(dialog)
        return key_fields

class AddEditWindow:
    def __init__(self, parent, title, record=None):
        self.parent = parent
        self.record = record
        self.window = tk.Toplevel()
        self.window.title(title)

        if self.record:
            tk.Label(self.window, text="Редактирование записи. Все поля доступны для изменения.").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            start_row = 1
        else:
            tk.Label(self.window, text="Добавление новой записи. Заполните все поля.").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            start_row = 1

        self.fields = parent.db.fields
        self.entries = {}

        # Функция для вставки из буфера
        def on_paste(event):
            try:
                clipboard = self.parent.root.clipboard_get()
                event.widget.insert(tk.INSERT, clipboard)
            except tk.TclError:
                pass
            return "break"

        for idx, field in enumerate(self.fields):
            tk.Label(self.window, text=field).grid(row=idx+start_row, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(self.window)
            entry.grid(row=idx+start_row, column=1, padx=5, pady=5, sticky='w')

            # Привязка Ctrl+V к вставке
            entry.bind("<Control-v>", on_paste)
            entry.bind("<Control-V>", on_paste)

            if record:
                entry.insert(0, record.get(field, ""))

            self.entries[field] = entry

        tk.Button(self.window, text="Сохранить", command=self.save).grid(row=len(self.fields)+start_row, column=0, pady=10, padx=5)
        tk.Button(self.window, text="Отмена", command=self.window.destroy).grid(row=len(self.fields)+start_row, column=1, pady=10, padx=5)

    def save(self):
        record = {}
        for field, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Ошибка", f"{field} не может быть пустым.")
                return
            record[field] = value
        try:
            if self.record:
                key = tuple(self.record[f] for f in self.parent.db.key_fields)
                self.parent.db.edit_record(key, record)
            else:
                self.parent.db.add_record(record)
            self.parent.refresh_table()
            self.window.destroy()
            messagebox.showinfo("Сохранение", "Запись успешно сохранена.")
        except ValueError as ve:
            messagebox.showerror("Ошибка", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {e}")

class DeleteWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.title("Удаление Записи")
        tk.Label(self.window, text="Поле").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.field_var = tk.StringVar(value=parent.db.fields[0])
        field_menu = tk.OptionMenu(self.window, self.field_var, *parent.db.fields)
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Label(self.window, text="Значение").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.value_entry = tk.Entry(self.window)
        self.value_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Button(self.window, text="Удалить", command=self.delete).grid(row=2, column=0, columnspan=2, pady=10)

    def delete(self):
        field = self.field_var.get()
        value = self.value_entry.get().strip()
        if not value:
            messagebox.showerror("Ошибка", "Значение не может быть пустым.")
            return
        try:
            self.parent.db.delete_records(field=field, value=value)  # Передаём field и value
            self.parent.refresh_table()
            self.window.destroy()
            messagebox.showinfo("Удаление", "Запись(и) успешно удалены.")
        except ValueError as ve:
            messagebox.showerror("Ошибка", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись(и): {e}")

class SearchWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.title("Поиск Записей")

        tk.Label(self.window, text="Поле").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.field_var = tk.StringVar(value=parent.db.fields[0])
        field_menu = tk.OptionMenu(self.window, self.field_var, *parent.db.fields)
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Label(self.window, text="Значение").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.value_entry = tk.Entry(self.window)
        self.value_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Button(self.window, text="Поиск", command=self.search).grid(row=2, column=0, columnspan=2, pady=10)

    def search(self):
        field = self.field_var.get()
        value = self.value_entry.get().strip()
        if not value:
            messagebox.showerror("Ошибка", "Значение не может быть пустым.")
            return

        try:
            df = self.parent.db.to_dataframe()
            mask = (df[field] == value)
            results = df[mask]

            if results.empty:
                messagebox.showinfo("Поиск", "Записи не найдены.")
                return

            result_window = tk.Toplevel(self.parent.root)
            result_window.title("Результаты Поиска")

            tree = ttk.Treeview(result_window, show='headings', selectmode='browse')
            tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            cols = results.columns.tolist()
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor='center')

            for _, row in results.iterrows():
                values = [row[col] for col in cols]
                tree.insert('', 'end', values=values)

            messagebox.showinfo("Поиск", f"Найдено записей: {len(results)}")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")

class EditWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.title("Редактирование Записи")

        # Предполагаем, что используем первый ключевой столбец
        key_field = self.parent.db.key_fields[0]

        tk.Label(self.window, text=f"Введите значение ключевого поля ({key_field}):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.key_entry = tk.Entry(self.window, width=50)
        self.key_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Button(self.window, text="Загрузить", command=self.load_record).grid(row=1, column=0, columnspan=2, pady=10)

    def load_record(self):
        key_input = self.key_entry.get().strip()
        if not key_input:
            messagebox.showerror("Ошибка", "Ключ не может быть пустым.")
            return

        try:
            key_field = self.parent.db.key_fields[0]
            df = self.parent.db.to_dataframe()  # Создаём DataFrame для фильтрации
            mask = (df[key_field] == key_input)
            results = df[mask]

            if results.empty:
                messagebox.showerror("Ошибка", "Запись не найдена.")
                return

            record_dict = results.iloc[0].to_dict()
            self.window.destroy()
            AddEditWindow(self.parent, "Редактировать Запись", record_dict)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить запись: {e}")


def main():
    root = tk.Tk()
    app = DatabaseGUI(root)
    root.geometry("800x600")
    root.mainloop()

if __name__ == "__main__":
    main()
