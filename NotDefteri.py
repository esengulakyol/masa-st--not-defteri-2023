import tkinter as tk
from tkinter import Text, PhotoImage, messagebox
import sqlite3
import os

class NotDefteri:
    def __init__(self, root):
        self.root = root
        self.root.title("Not Defteri")

        # 🔹 Görsel dosyaları için dinamik yol
        base_path = os.path.dirname(os.path.dirname(__file__))
        images_path = os.path.join(base_path, "images")

        # Veritabanı bağlantısı
        self.conn = sqlite3.connect("notes.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS notes (title TEXT, content TEXT)")
        self.conn.commit()

        # Ana çerçeve
        self.main_frame = tk.Frame(self.root, bg="gray")
        self.main_frame.pack(fill="both", expand=True)

        # Sol panel (kayıtlı notlar)
        self.left_panel = tk.Frame(self.main_frame, bg="lightgray", width=350)
        self.left_panel.pack(side="left", fill="y")

        # Kayıtlı notlar arama çubuğu ve butonu
        search_frame = tk.Frame(self.left_panel, bg="lightgray")
        search_frame.pack(pady=10, padx=10, fill="x")

        self.search_bar = tk.Entry(search_frame, font=("Arial", 12))
        self.search_bar.pack(side="left", fill="x", expand=True)

        # 🔹 Görsel yolları düzenlendi
        self.search_icon = PhotoImage(file=os.path.join(images_path, "searchbutton.png"))
        self.search_button = tk.Button(search_frame, image=self.search_icon, bg="orange", command=self.search_note)
        self.search_button.pack(side="left", padx=(5, 0))

        # Not listesi
        self.notes_list_frame = tk.Frame(self.left_panel, bg="gray")
        self.notes_list_frame.pack(fill="both", expand=True)

        # Sağ panel (not içeriği)
        self.right_panel = tk.Frame(self.main_frame, bg="gray", relief="solid", bd=1)
        self.right_panel.pack(side="right", fill="both", expand=True)

        # Not başlığı
        self.note_title = tk.Entry(self.right_panel, font=("Arial", 14), bg="white", fg="gray")
        self.note_title.pack(padx=10, pady=10, fill="x")

        # Placeholder özelliği
        self.note_title.insert(0, "NOT BAŞLIĞI")
        self.note_title.bind("<FocusIn>", self.clear_placeholder)

        # Not içeriği
        self.text_area = Text(self.right_panel, wrap="word", font=("Arial", 12), bg="lightgray")
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)

        # 🔹 Kaydet butonu görseli
        self.save_icon = PhotoImage(file=os.path.join(images_path, "save.png"))
        self.save_button = tk.Button(self.right_panel, image=self.save_icon, bg="yellow", command=self.save_note)
        self.save_button.pack(side="right", padx=10, pady=10)

        # 🔹 Sil butonu görseli
        self.delete_icon = PhotoImage(file=os.path.join(images_path, "deletebutton.png"))
        self.delete_button = tk.Button(self.right_panel, image=self.delete_icon, bg="red", command=self.delete_note)
        self.delete_button.pack(side="right", padx=10, pady=10)

        # Kayıtlı notlar listesi
        self.notes = []
        self.load_notes_from_db()

    def clear_placeholder(self, event):
        if self.note_title.get() == "NOT BAŞLIĞI":
            self.note_title.delete(0, tk.END)
            self.note_title.config(fg="black")

    def save_note(self):
        # Not başlığı ve içeriği al
        title = self.note_title.get()
        content = self.text_area.get("1.0", tk.END).strip()

        if title and content:
            # Veritabanına kaydet
            self.cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            self.conn.commit()

            # Yeni bir not ekle
            self.add_note_to_list(title, content)

            # Not başlığı ve içeriği temizle
            self.note_title.delete(0, tk.END)
            self.text_area.delete("1.0", tk.END)

    def add_note_to_list(self, title, content):
        note_frame = tk.Frame(self.notes_list_frame, bg="lightgray", height=80)
        note_frame.pack(padx=10, pady=5, fill="x")

        note_title = tk.Label(note_frame, text=title, bg="green", fg="white", anchor="w")
        note_title.pack(side="top", fill="x")

        # Kısa içerik
        short_content = content[:50] + ("..." if len(content) > 50 else "")
        note_preview = tk.Label(note_frame, text=short_content, bg="lightgray", fg="black", anchor="w")
        note_preview.pack(side="top", fill="x")

        # Sil butonu
        delete_btn = tk.Button(note_frame, text="Sil", bg="red", fg="white", command=lambda nf=note_frame, t=title: self.confirm_delete(nf, t))
        delete_btn.pack(side="right", padx=5)

        # Notun tıklanma özelliği
        note_title.bind("<Button-1>", lambda e, t=title, c=content: self.load_note(t, c))
        note_preview.bind("<Button-1>", lambda e, t=title, c=content: self.load_note(t, c))

        # Notu listeye ekle
        self.notes.append((title, content))

    def load_note(self, title, content):
        # Sağ panele notu yükle
        self.note_title.delete(0, tk.END)
        self.note_title.insert(0, title)

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)

    def confirm_delete(self, note_frame, title):
        # Silme onayı penceresi
        confirm = messagebox.askyesno("Onay", f"'{title}' adlı notu silmek istediğinize emin misiniz?")
        if confirm:
            self.delete_note_from_list(note_frame, title)

    def delete_note_from_list(self, note_frame, title):
        # Frame'i kaldır
        note_frame.destroy()

        # Notu veritabanından ve listeden sil
        self.cursor.execute("DELETE FROM notes WHERE title = ?", (title,))
        self.conn.commit()
        self.notes = [(t, c) for t, c in self.notes if t != title]

        # Sağ panelde gösterilen not bu ise temizle
        if self.note_title.get() == title:
            self.delete_note()

    def delete_note(self):
        # Not başlığı ve içeriği temizle
        self.note_title.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)

    def search_note(self):
        search_title = self.search_bar.get().strip()
        for title, content in self.notes:
            if title == search_title:
                self.load_note(title, content)
                return
        # Aranan not bulunamadığında
        messagebox.showinfo("Uyarı", "Not bulunamadı")

    def load_notes_from_db(self):
        # Veritabanından notları yükle
        self.cursor.execute("SELECT title, content FROM notes")
        for title, content in self.cursor.fetchall():
            self.add_note_to_list(title, content)


# Uygulamayı başlat
root = tk.Tk()
app = NotDefteri(root)
root.mainloop()
