import os, socket, threading
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox



def encrypt_message(msg: str) -> bytes:
    aesgcm = AESGCM(SHARED_KEY)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, msg.encode(), None)


def decrypt_message(data: bytes) -> str:
    aesgcm = AESGCM(SHARED_KEY)
    nonce, ciphertext = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()


# ------------------------------------------------------------------
# Modern Secure Messenger
# ------------------------------------------------------------------
class ModernSecureApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- basic window ---
        self.title("Secure Messenger")
        self.geometry("800x500")
        self.resizable(True,True)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")   # nice teal/blue palette

        # --- background image ---
        bg = ctk.CTkImage(light_image=Image.open("background.jpg"),
                          dark_image=Image.open("background.jpg"),
                          size=(800, 500))
        bg_label = ctk.CTkLabel(self, text="", image=bg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # --- centre card (glass effect) ---
        self.card = ctk.CTkFrame(self, corner_radius=20, fg_color=("gray10", "gray10"))
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self.card,
                                        text="Secure Messenger",
                                        font=("Segoe UI Semibold", 24))
        self.title_label.pack(pady=(20, 15))

        # --- main buttons ---
        self.recv_btn = ctk.CTkButton(self.card, text="Receiver Mode",
                                      corner_radius=15, width=200,
                                      command=self.start_receiver)
        self.recv_btn.pack(pady=10)

        self.send_btn = ctk.CTkButton(self.card, text="Sender Mode",
                                      corner_radius=15, width=200,
                                      command=self.start_sender)
        self.send_btn.pack(pady=10)

    # ---------------- Receiver UI ----------------
    def start_receiver(self):
        self.clear_card()
        ctk.CTkLabel(self.card, text="Receiver Mode",
                     font=("Segoe UI Semibold", 20)).pack(pady=10)

        self.output = ctk.CTkTextbox(self.card, width=600, height=300,
                                     corner_radius=10, font=("Consolas", 12))
        self.output.pack(padx=10, pady=10)
        self.output.insert("end", "Listening on port 5000...\n")
        self.output.configure(state="disabled")

        threading.Thread(target=self.receiver_thread, daemon=True).start()

    def receiver_thread(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', PORT))
            s.listen(1)
            while True:
                conn, addr = s.accept()
                with conn:
                    encrypted = conn.recv(4096)
                    try:
                        msg = decrypt_message(encrypted)
                        self.output.configure(state="normal")
                        self.output.insert("end", f"\nFrom {addr[0]}: {msg}")
                        self.output.see("end")
                        self.output.configure(state="disabled")
                    except Exception as e:
                        self.output.configure(state="normal")
                        self.output.insert("end", f"\n[Error decrypting message] {e}")
                        self.output.see("end")
                        self.output.configure(state="disabled")

    # ---------------- Sender UI ----------------
    def start_sender(self):
        self.clear_card()
        ctk.CTkLabel(self.card, text="Sender Mode",
                     font=("Segoe UI Semibold", 20)).pack(pady=10)

        ctk.CTkLabel(self.card, text="Receiver IP:", font=("Segoe UI", 14)).pack()
        self.ip_entry = ctk.CTkEntry(self.card, width=250, font=("Segoe UI", 13))
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(pady=5)

        ctk.CTkLabel(self.card, text="Message:", font=("Segoe UI", 14)).pack()
        self.msg_entry = ctk.CTkEntry(self.card, width=400, font=("Segoe UI", 13))
        self.msg_entry.pack(pady=5)

        ctk.CTkButton(self.card, text="Send Securely",
                      corner_radius=15, width=200,
                      command=self.send_message).pack(pady=15)

    def send_message(self):
        ip = self.ip_entry.get().strip()
        msg = self.msg_entry.get().strip()
        if not msg:
            messagebox.showwarning("Warning", "Message cannot be empty")
            return
        data = encrypt_message(msg)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, PORT))
                s.sendall(data)
            messagebox.showinfo("Success", "Encrypted message sent!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send: {e}")

    # ---------------- helper ----------------
    def clear_card(self):
        for w in self.card.winfo_children():
            w.destroy()


if __name__ == "__main__":
    app = ModernSecureApp()
    app.mainloop()
