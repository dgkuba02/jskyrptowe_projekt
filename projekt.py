import tkinter as tk
from tkinter import messagebox, simpledialog, Checkbutton, IntVar, Toplevel, Entry, Label, Button
from PIL import Image, ImageTk
import requests
import random
from io import BytesIO
from datetime import datetime
import json
import os

API_KEY = "63684e0d57ae1644fe89071c159ef905"
DEFAULT_CITY = "Sopot"
SETTINGS_FILE = "settings.json"

definitions = [
    {
        "word": "Kapibara",
        "options": ["ptak", "największy gryzoń świata", "ssak morski"],
        "correct": 1
    },
    {
        "word": "Koralowiec",
        "options": ["kamień", "roślina", "zwierzę"],
        "correct": 2
    },
    {
        "word": "Fotosynteza",
        "options": ["proces oddychania", "tworzenie energii ze światła", "przemiana materii"],
        "correct": 1
    },
    {
        "word": "Tundra",
        "options": ["las tropikalny", "obszar pustynny", "zimny, bezdrzewny obszar"],
        "correct": 2
    },
    {
        "word": "Atom",
        "options": ["najmniejsza jednostka materii", "cząstka światła", "rodzaj komórki"],
        "correct": 0
    },
    {
        "word": "Mitologia",
        "options": ["zbiór wierzeń i legend", "rodzaj matematyki", "sztuka gotowania"],
        "correct": 0
    },
    {
        "word": "Delfin",
        "options": ["ryba", "ssak morski", "gad"],
        "correct": 1
    },
    {
        "word": "Kontynent",
        "options": ["część planety pokryta wodą", "wielki obszar lądu", "rodzaj wyspy"],
        "correct": 1
    },
    {
        "word": "Grawitacja",
        "options": ["energia cieplna", "siła przyciągająca do ziemi", "pole magnetyczne"],
        "correct": 1
    },
    {
        "word": "Encyklopedia",
        "options": ["książka kucharska", "zbiór bajek", "zbiór wiedzy na różne tematy"],
        "correct": 2
    }
]

true_false_questions = [
    {"text": "Słoń potrafi skakać.", "answer": False},
    {"text": "Ziemia obraca się wokół Słońca.", "answer": True},
    {"text": "Lód jest cieplejszy od wrzątku.", "answer": False},
    {"text": "Nietoperze są ślepe.", "answer": False},
    {"text": "Woda wrze w temperaturze 100°C \n przy ciśnieniu atmosferycznym.", "answer": True},
    {"text": "Pająki to owady.", "answer": False},
    {"text": "Ludzie mają 5 zmysłów.", "answer": True},
    {"text": "Księżyc świeci własnym światłem.", "answer": False},
    {"text": "Rekiny to ryby.", "answer": True},
    {"text": "Banan rośnie na drzewie.", "answer": False}
]

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except:
            pass
    return {
        "city": DEFAULT_CITY,
        "screens": {
            "weather": True,
            "clock": True,
            "quiz0": True,
            "quote": True,
            "dog": True,
            "quiz": True,
            "note": True
        }
    }

def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać ustawień:\n{e}")

settings = load_settings()

def get_weather_text(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=pl"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("cod") != 200:
            return f"Błąd pogody: {data.get('message','Nieznany błąd')}"
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()
        return f"{city} 🌤 Pogoda:\n{temp}°C, {desc}"
    except Exception as e:
        return f"Nie udało się pobrać pogody.\n{e}"

def get_time_text():
    now = datetime.now()
    return now.strftime("🕒 %H:%M\n📅 %A, %d %B")

def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=5)
        data = r.json()[0]
        return f"“{data['q']}”\n– {data['a']}"
    except:
        return "Brak cytatu 😞"

def get_dog_image():
    try:
        r = requests.get("https://random.dog/woof.json", timeout=5)
        url = r.json()["url"]
        if not url.lower().endswith(('.jpg', '.png', '.jpeg')):
            return None
        image_data = requests.get(url, timeout=5).content
        return Image.open(BytesIO(image_data))
    except:
        return None

class WidgetApp:
    def __init__(self, root):
        self.root = root
        root.title("Super Mega Hiper Widget Pro Max")
        root.geometry("400x400")
        root.resizable(False, False)
        
        BG_COLOR = "#282c34"

        root.config(bg=BG_COLOR)

        menubar = tk.Menu(root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Ustawienia", command=self.open_settings)
        menubar.add_cascade(label="Menu", menu=settings_menu)
        root.config(menu=menubar)

        self.container = tk.Frame(root, bg=BG_COLOR)
        self.container.pack(expand=True, fill='both')

        self.label = Label(
            self.container,
            text="",
            font=("Helvetica", 16),
            justify="center",
            anchor="center",
            wraplength=380,
            bg=BG_COLOR,
            fg="white"
        )
        self.label.place(relx=0.5, rely=0.5, anchor='center')

        self.img_label = Label(self.container, bg=BG_COLOR)
        self.img_label.place_forget()

        self.frame = tk.Frame(self.container, bg=BG_COLOR)
        self.frame.place_forget()

        self.current_screen = 0
        self.screens = []
        self.prepare_screens()

        self.screen_job = None
        self.start_screen_loop()
           
    def start_screen_loop(self):
        if self.screen_job:
            self.root.after_cancel(self.screen_job)
        self.next_screen()

    def prepare_screens(self):
        self.screens = []
        s = settings["screens"]
        if s.get("note", False):
            self.screens.append(self.screen_note)
        if s.get("weather", False):
            self.screens.append(self.screen_weather)
        if s.get("clock", False):
            self.screens.append(self.screen_clock)
        if s.get("quiz0", False):
            self.screens.append(self.screen_definition_quiz)
        if s.get("quote", False):
            self.screens.append(self.screen_quote)
        if s.get("dog", False):
            self.screens.append(self.screen_dog)
        if s.get("quiz", False):
            self.screens.append(self.screen_true_false_quiz)

        if not self.screens:
            self.screens.append(self.screen_no_screens)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.label.config(text="")
        self.img_label.config(image="", text="")

    def next_screen(self):
        self.clear_frame()
        screen_func = self.screens[self.current_screen]
        self.current_screen = (self.current_screen + 1) % len(self.screens)
        screen_func()

        self.screen_job = self.root.after(3000, self.next_screen)
        
    def open_notepad_window(self):
        NotepadWindow(self.root)

    def screen_note(self):
        self.label.place_forget()
        self.img_label.place_forget()
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.clear_frame()

        Label(self.frame, text="📝 Notatki", font=("Helvetica", 16)).pack(pady=10)
        Button(self.frame, text="Otwórz notatnik", command=self.open_notepad_window).pack(pady=5)

    def screen_weather(self):
        self.img_label.place_forget()
        self.frame.place_forget()
        text = get_weather_text(settings["city"])
        self.label.config(text=text, anchor="center", justify="center", font=("Helvetica", 16))
        self.label.place(relx=0.5, rely=0.5, anchor='center')

    def screen_clock(self):
        self.img_label.place_forget()
        self.frame.place_forget()
        self.label.place(relx=0.5, rely=0.5, anchor='center')

        self.update_clock_text()
    
    def update_clock_text(self):
        now = datetime.now()
        time_text = now.strftime("%H:%M:%S")
        date_text = now.strftime("%A, %d %B")

        self.label.config(
            text=f"🕒 {time_text}\n{date_text}",
            font=("Helvetica", 40),
            justify="center",
            anchor="center"
        )
        if self.screens[self.current_screen - 1] == self.screen_clock:
            self.root.after(1000, self.update_clock_text)

    def screen_quote(self):
        self.img_label.place_forget()
        self.frame.place_forget()
        text = get_quote()
        self.label.config(text=text, anchor="center", justify="center", font=("Helvetica", 16))
        self.label.place(relx=0.5, rely=0.5, anchor='center')

    def screen_dog(self):
        self.label.place_forget()
        self.frame.place_forget()
        img = get_dog_image()
        if img:
            img.thumbnail((380, 220))
            tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=tk_img)
            self.img_label.image = tk_img
            self.img_label.place(relx=0.5, rely=0.5, anchor='center')
        else:
            self.img_label.place_forget()
            self.label.config(text="Nie udało się wczytać obrazka 🐶", anchor="center", justify="center", font=("Helvetica", 16))
            self.label.place(relx=0.5, rely=0.5, anchor='center')

    def screen_no_screens(self):
        self.img_label.place_forget()
        self.frame.place_forget()
        self.label.config(text="Nie wybrano żadnego ekranu!\nPrzejdź do ustawień i wybierz przynajmniej jeden.", anchor="center", justify="center", font=("Helvetica", 16))
        self.label.place(relx=0.5, rely=0.5, anchor='center')

    def screen_definition_quiz(self):
        self.label.place_forget()
        self.img_label.place_forget()
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.clear_frame()

        question = random.choice(definitions)
        word = question["word"]
        options = question["options"]
        correct_index = question["correct"]

        Label(self.frame, text=f"Co to jest: {word}?", font=("Arial", 16)).pack(pady=10)

        result_label = Label(self.frame, text="", font=("Arial", 14))
        result_label.pack(pady=5)

        def check(i):
            if i == correct_index:
                result_label.config(text="✅ Dobrze!", fg="green")
            else:
                result_label.config(text=f"❌ Niepoprawnie! Poprawna odpowiedź: {options[correct_index]}", fg="red")

        for i, opt in enumerate(options):
            Button(self.frame, text=opt, command=lambda i=i: check(i)).pack(fill='x', padx=50, pady=5)

    def screen_true_false_quiz(self):
        self.label.place_forget()
        self.img_label.place_forget()
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.clear_frame()

        question = random.choice(true_false_questions)

        Label(self.frame, text=question["text"], font=("Arial", 16)).pack(pady=10)

        result_label = Label(self.frame, text="", font=("Arial", 14))
        result_label.pack(pady=5)

        def answer(choice):
            correct = question["answer"]
            if choice == correct:
                result_label.config(text="✅ Dobrze!", fg="green")
            else:
                result_label.config(text=f"❌ Niepoprawnie. To jest {'prawda' if correct else 'fałsz'}.", fg="red")

        Button(self.frame, text="Prawda", command=lambda: answer(True)).pack(pady=5)
        Button(self.frame, text="Fałsz", command=lambda: answer(False)).pack(pady=5)

    def open_settings(self):
        SettingsWindow(self)

class SettingsWindow:
    def __init__(self, app):
        self.app = app
        self.win = Toplevel(app.root)
        self.win.title("Ustawienia")
        self.win.geometry("400x400")
        self.win.resizable(False, False)

        Label(self.win, text="Miasto do pogody:", font=("Helvetica", 12)).pack(pady=5)
        self.city_entry = Entry(self.win)
        self.city_entry.pack(pady=5)
        self.city_entry.insert(0, settings["city"])

        Label(self.win, text="Wybierz ekrany do wyświetlania:", font=("Helvetica", 12)).pack(pady=10)

        self.vars = {}
        screens = ["weather", "clock", "quiz0", "quote", "dog", "quiz", "note"]
        screen_names = {
            "weather": "Pogoda",
            "clock": "Zegar",
            "quiz0": "Quiz wiedza",
            "quote": "Cytat dnia",
            "dog": "Zdjęcie zwierzaka",
            "quiz": "Quiz prawda/fałsz",
            "note": "Notatnik"
        }
        for s in screens:
            var = IntVar(value=1 if settings["screens"].get(s, False) else 0)
            cb = Checkbutton(self.win, text=screen_names[s], variable=var, font=("Helvetica", 11))
            cb.pack(anchor="w")
            self.vars[s] = var

        Button(self.win, text="Zapisz", command=self.save_settings).pack(pady=15)

    def save_settings(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Błąd", "Podaj nazwę miasta.")
            return
        settings["city"] = city
        for s, var in self.vars.items():
            settings["screens"][s] = bool(var.get())
        save_settings(settings)
        self.app.prepare_screens()
        self.app.current_screen = 0
        self.app.start_screen_loop()
        self.win.destroy()

class NotepadWindow:
    def __init__(self, parent):
        self.win = Toplevel(parent)
        self.win.title("Notatnik")
        self.win.geometry("400x400")
        self.notes_dir = "notes"
        os.makedirs(self.notes_dir, exist_ok=True)

        Label(self.win, text="Twoje notatki:", font=("Helvetica", 14)).pack(pady=5)

        self.listbox = tk.Listbox(self.win, font=("Arial", 12))
        self.listbox.pack(fill='both', expand=True, padx=10, pady=5)

        self.refresh_notes()

        Button(self.win, text="➕ Dodaj notatkę", command=self.add_note).pack(fill='x', padx=10, pady=2)
        Button(self.win, text="✏️ Edytuj wybraną", command=self.edit_note).pack(fill='x', padx=10, pady=2)
        Button(self.win, text="🗑 Usuń wybraną", command=self.delete_note).pack(fill='x', padx=10, pady=2)
        Button(self.win, text="❌ Wyjdź", command=self.win.destroy).pack(fill='x', padx=10, pady=5)

    def get_selected_note_path(self):
        selection = self.listbox.curselection()
        if not selection:
            return None
        name = self.listbox.get(selection[0])
        return os.path.join(self.notes_dir, name + ".txt")

    def refresh_notes(self):
        self.listbox.delete(0, tk.END)
        for filename in os.listdir(self.notes_dir):
            if filename.endswith(".txt"):
                self.listbox.insert(tk.END, filename[:-4])

    def add_note(self):
        name = simpledialog.askstring("Nowa notatka", "Podaj nazwę notatki:")
        if name:
            path = os.path.join(self.notes_dir, name + ".txt")
            if os.path.exists(path):
                messagebox.showwarning("Błąd", "Notatka o tej nazwie już istnieje.")
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            self.refresh_notes()

    def edit_note(self):
        path = self.get_selected_note_path()
        if not path:
            messagebox.showwarning("Błąd", "Wybierz notatkę.")
            return

        edit_win = Toplevel(self.win)
        edit_win.title("Edytuj notatkę")
        edit_win.geometry("400x400")
        edit_win.resizable(False, False)

        text = tk.Text(edit_win, font=("Arial", 12))
        text.pack(expand=True, fill='both', padx=10, pady=(10, 0))

        with open(path, "r", encoding="utf-8") as f:
            text.insert("1.0", f.read())

        btn_frame = tk.Frame(edit_win)
        btn_frame.pack(fill='x', pady=5)

        def save():
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.get("1.0", "end").strip())
            messagebox.showinfo("Zapisano", "Notatka została zapisana.")
            edit_win.destroy()

        save_button = Button(btn_frame, text="💾 Zapisz", command=save)
        save_button.pack(pady=5)

    def delete_note(self):
        path = self.get_selected_note_path()
        if not path:
            messagebox.showwarning("Błąd", "Wybierz notatkę.")
            return
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno usunąć notatkę?"):
            os.remove(path)
            self.refresh_notes()

if __name__ == "__main__":
    root = tk.Tk()
    app = WidgetApp(root)
    root.mainloop()