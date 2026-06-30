import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import threading
from app.assistant import Assistant


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AssistantUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.assistant = Assistant()
        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        self.title(f"AI Assistant — {self.assistant.get_model_name()}")
        self.geometry("900x650")
        self.minsize(600, 400)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Chat display
        self.chat_frame = ctk.CTkScrollableFrame(self)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Input area
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(8, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Type a message...")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)

        self.send_btn = ctk.CTkButton(input_frame, text="Send", width=80, command=self._send)
        self.send_btn.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 2))

        # Top menu
        menu_frame = ctk.CTkFrame(self, height=36)
        menu_frame.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))
        menu_frame.grid_propagate(False)

        ctk.CTkButton(menu_frame, text="Clear", width=60, command=self._clear).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="Settings", width=80, command=self._open_settings).pack(side="left", padx=2)

    def _bind_events(self):
        self.entry.bind("<Return>", lambda e: self._send())

    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.entry.configure(state="disabled")
        self.send_btn.configure(state="disabled", text="...")
        self._add_bubble("You", text, "user")
        self._add_bubble("Assistant", "▌", "assistant")
        self._scroll_to_bottom()

        def run():
            last_bubble = None
            def on_update(phase, data):
                self.after(0, lambda: self._handle_update(phase, data))
            self.assistant.process_message(text, on_update=on_update)
            self.after(0, self._done)

        threading.Thread(target=run, daemon=True).start()

    def _handle_update(self, phase, data):
        if phase == "tool_start":
            self._add_bubble("Tool", data, "tool")
        elif phase == "tool_result":
            self._append_to_last_bubble(data)
        elif phase == "assistant_complete":
            self._update_last_assistant(data)
        self._scroll_to_bottom()

    def _add_bubble(self, sender, text, kind):
        color = {
            "user": ("#2b5278", "#ffffff"),
            "assistant": ("#2e2e2e", "#d4d4d4"),
            "tool": ("#1e3a2e", "#8bc34a"),
        }.get(kind, ("#2e2e2e", "#d4d4d4"))

        frame = ctk.CTkFrame(self.chat_frame, fg_color=color[0], corner_radius=8)
        frame.pack(fill="x", padx=8, pady=3, anchor="w" if kind != "user" else "e")
        frame.pack_propagate(False)

        lbl = ctk.CTkLabel(
            frame, text=f"{sender}: {text}", wraplength=600,
            justify="left", anchor="w", text_color=color[1], font=("Segoe UI", 12),
        )
        lbl.pack(fill="x", padx=10, pady=6)

        if kind == "tool":
            self._last_tool_frame = frame
            self._last_tool_label = lbl
        elif kind == "assistant" and text == "▌":
            self._last_assistant_frame = frame
            self._last_assistant_label = lbl

    def _append_to_last_bubble(self, text):
        if hasattr(self, "_last_tool_label"):
            current = self._last_tool_label.cget("text")
            self._last_tool_label.configure(text=current + "\n" + text)

    def _update_last_assistant(self, text):
        if hasattr(self, "_last_assistant_label"):
            self._last_assistant_label.configure(text=f"Assistant: {text}")
            self._last_assistant_frame.configure(fg_color="#2e2e2e")

    def _scroll_to_bottom(self):
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _done(self):
        self.entry.configure(state="normal")
        self.send_btn.configure(state="normal", text="Send")
        self.entry.focus()

    def _clear(self):
        self.assistant.clear_history()
        for w in self.chat_frame.winfo_children():
            w.destroy()

    def _open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("420x320")
        win.transient(self)
        win.grab_set()

        row = 0
        ctk.CTkLabel(win, text="LLM Backend:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        backend_var = tk.StringVar(value=self.assistant.llm.name())
        backend_menu = ctk.CTkOptionMenu(
            win, values=["openai", "anthropic", "ollama"],
            command=lambda v: setattr(self.assistant, "_pending_backend", v),
        )
        backend_menu.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        def apply():
            if hasattr(self.assistant, "_pending_backend"):
                self.assistant.switch_backend(self.assistant._pending_backend)
                self.title(f"AI Assistant — {self.assistant.get_model_name()}")
            win.destroy()

        ctk.CTkButton(win, text="Apply", command=apply).grid(row=row, column=0, columnspan=2, pady=20)
