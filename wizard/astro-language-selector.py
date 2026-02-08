import tkinter as tk
from tkinter import messagebox
import os, sys
import i18n

BG_COLOR = "#0f172a"
ACCENT_COLOR = "#38bdf8"
SECONDARY_BG = "#1e293b"

class LanguageSelector:
    def __init__(self, root):
        self.root = root
        self.root.title(i18n.t("select_language"))
        self.root.geometry("400x450")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.lang_var = tk.StringVar(value=i18n.get_lang())
        
        self.draw_main()
        self.center_window()

    def draw_main(self):
        for w in self.root.winfo_children(): w.destroy()
        
        tk.Label(self.root, text="🌍", font=("Sans", 48), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(30, 10))
        tk.Label(self.root, text=i18n.t("select_language"), font=("Sans", 18, "bold"), bg=BG_COLOR, fg="white").pack(pady=10)
        
        frm = tk.Frame(self.root, bg=BG_COLOR)
        frm.pack(pady=20)
        
        opts = [("Español", "es"), ("English", "en")]
        for text, val in opts:
            rb = tk.Radiobutton(frm, text=text, variable=self.lang_var, value=val,
                                bg=BG_COLOR, fg="white", selectcolor=SECONDARY_BG,
                                font=("Sans", 12), activebackground=BG_COLOR, cursor="hand2")
            rb.pack(pady=10, anchor="w")

        tk.Button(self.root, text=i18n.t("save"), command=self.save_lang,
                  bg=ACCENT_COLOR, fg="#0f172a", font=("Sans", 12, "bold"),
                  relief="flat", padx=40, pady=10, cursor="hand2").pack(pady=30)

    def save_lang(self):
        lang = self.lang_var.get()
        try:
            import subprocess
            # Create directory with sudo
            dir_path = os.path.dirname(i18n.LANG_FILE)
            subprocess.run(f"sudo mkdir -p {dir_path}", shell=True, check=True)
            
            # Write language file with sudo
            subprocess.run(f"echo '{lang}' | sudo tee {i18n.LANG_FILE} > /dev/null", shell=True, check=True)
            
            # Set proper permissions
            subprocess.run(f"sudo chmod 644 {i18n.LANG_FILE}", shell=True, check=True)
            
            messagebox.showinfo(i18n.t("select_language"), i18n.t("restart_msg"))
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageSelector(root)
    root.mainloop()
