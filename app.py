"""Desktop GUI for Trim Images PNG."""

import threading
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from trim_png_alpha import trim_image


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TrimApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trim Images PNG")
        self.geometry("820x660")
        self.minsize(640, 500)

        self._files: list[Path] = []
        self._output_dir: Optional[Path] = None
        self._processing = False
        self._rows: list[tuple] = []  # (BooleanVar, CTkFrame, Path)

        self._setup()

    def _setup(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # file list expands

        # Title
        ctk.CTkLabel(
            self, text="Trim Images PNG",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        # File list toolbar
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(bar, text="Imagens selecionadas", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w"
        )
        btn_box = ctk.CTkFrame(bar, fg_color="transparent")
        btn_box.grid(row=0, column=1)
        ctk.CTkButton(btn_box, text="+ Adicionar", width=110, command=self._add_files).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_box, text="Remover marcadas", width=148,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"),
            command=self._remove_checked,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_box, text="Limpar tudo", width=100,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"),
            command=self._clear_all,
        ).pack(side="left", padx=2)

        # Thin divider
        ctk.CTkFrame(self, height=1).grid(row=2, column=0, sticky="ew", padx=16)

        # Scrollable file list
        self._file_list = ctk.CTkScrollableFrame(self)
        self._file_list.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 4))
        self._file_list.grid_columnconfigure(0, weight=1)

        self._empty_lbl = ctk.CTkLabel(
            self._file_list,
            text="Nenhuma imagem adicionada.\nClique em  + Adicionar  para selecionar arquivos PNG.",
            text_color="gray", justify="center",
        )
        self._empty_lbl.grid(row=0, column=0, pady=36)

        # Settings row (padding slider)
        cfg = ctk.CTkFrame(self)
        cfg.grid(row=4, column=0, sticky="ew", padx=16, pady=4)

        ctk.CTkLabel(cfg, text="Padding:  ").pack(side="left", padx=(12, 0), pady=10)
        self._pad_var = tk.IntVar(value=0)
        self._pad_lbl = ctk.CTkLabel(cfg, text="  0 px", width=55)
        ctk.CTkSlider(
            cfg, from_=0, to=100, number_of_steps=100, width=220,
            variable=self._pad_var, command=self._on_slider,
        ).pack(side="left", padx=4, pady=10)
        self._pad_lbl.pack(side="left", pady=10)

        # Output folder row
        out = ctk.CTkFrame(self)
        out.grid(row=5, column=0, sticky="ew", padx=16, pady=4)
        out.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(out, text="Pasta de saída:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(12, 4), pady=8,
        )
        self._out_lbl = ctk.CTkLabel(out, text="Não selecionada", text_color="gray", anchor="w")
        self._out_lbl.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        ctk.CTkButton(out, text="Selecionar pasta", width=148, command=self._pick_output).grid(
            row=0, column=2, padx=(4, 12), pady=8,
        )

        # Progress bar + process button
        act = ctk.CTkFrame(self, fg_color="transparent")
        act.grid(row=6, column=0, sticky="ew", padx=16, pady=(4, 0))
        act.grid_columnconfigure(0, weight=1)

        self._prog = ctk.CTkProgressBar(act)
        self._prog.set(0)
        self._prog.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self._go_btn = ctk.CTkButton(act, text="Processar imagens", width=168, command=self._start)
        self._go_btn.grid(row=0, column=1)

        # Log
        ctk.CTkLabel(self, text="Log", font=ctk.CTkFont(weight="bold")).grid(
            row=7, column=0, sticky="w", padx=16, pady=(8, 0),
        )
        self._log = ctk.CTkTextbox(self, height=130, state="disabled")
        self._log.grid(row=8, column=0, sticky="ew", padx=16, pady=(2, 16))

    # ── Event handlers ────────────────────────────────────────────

    def _on_slider(self, v):
        self._pad_lbl.configure(text=f"  {int(v)} px")

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar imagens PNG",
            filetypes=[("Imagens PNG", "*.png *.PNG"), ("Todos os arquivos", "*.*")],
        )
        added = 0
        for p_str in paths:
            p = Path(p_str)
            if p not in self._files:
                self._files.append(p)
                self._append_row(p)
                added += 1
        if added:
            self._empty_lbl.grid_remove()

    def _append_row(self, path: Path):
        idx = len(self._rows)
        frame = ctk.CTkFrame(self._file_list, fg_color=("gray88", "gray22"), corner_radius=6)
        frame.grid(row=idx + 1, column=0, sticky="ew", pady=2, padx=4)
        frame.grid_columnconfigure(2, weight=1)

        var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(frame, text="", variable=var, width=28).grid(
            row=0, column=0, padx=(8, 2), pady=6
        )
        ctk.CTkLabel(frame, text=path.name, font=ctk.CTkFont(weight="bold"), anchor="w").grid(
            row=0, column=1, sticky="ew", padx=(2, 6)
        )
        ctk.CTkLabel(
            frame, text=str(path.parent), text_color="gray",
            anchor="w", font=ctk.CTkFont(size=11),
        ).grid(row=0, column=2, sticky="ew", padx=(0, 8))

        self._rows.append((var, frame, path))

    def _remove_checked(self):
        kept_rows = []
        kept_files = []
        for var, frame, path in self._rows:
            if var.get():
                frame.destroy()
            else:
                kept_rows.append((var, frame, path))
                kept_files.append(path)
        self._rows = kept_rows
        self._files = kept_files
        for i, (_, frame, _) in enumerate(self._rows):
            frame.grid(row=i + 1, column=0)
        if not self._files:
            self._empty_lbl.grid()

    def _clear_all(self):
        for _, frame, _ in self._rows:
            frame.destroy()
        self._rows.clear()
        self._files.clear()
        self._empty_lbl.grid()

    def _pick_output(self):
        folder = filedialog.askdirectory(title="Selecionar pasta de saída")
        if folder:
            self._output_dir = Path(folder)
            self._out_lbl.configure(text=str(self._output_dir), text_color=("gray10", "gray90"))

    def _write_log(self, msg: str):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _start(self):
        if self._processing:
            return
        if not self._files:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma imagem.")
            return
        if not self._output_dir:
            messagebox.showwarning("Aviso", "Selecione a pasta de saída.")
            return

        self._processing = True
        self._go_btn.configure(state="disabled", text="Processando…")
        self._prog.set(0)
        self._write_log(f"Iniciando processamento de {len(self._files)} imagem(ns)...\n")

        threading.Thread(
            target=self._work,
            args=(list(self._files), self._output_dir, int(self._pad_var.get())),
            daemon=True,
        ).start()

    def _work(self, files: list, out_dir: Path, padding: int):
        total = len(files)
        ok_count = 0
        for i, src in enumerate(files):
            out_path = out_dir / src.name
            ok, msg = trim_image(src, out_path, alpha_threshold=0, padding=padding, overwrite=True)
            ok_count += int(ok)
            self.after(0, self._write_log, f"{'[ OK ]' if ok else '[FAIL]'} {msg}")
            self.after(0, self._prog.set, (i + 1) / total)

        self.after(0, self._write_log, f"\nConcluido: {ok_count}/{total} imagens processadas.")
        self.after(0, self._finish, ok_count, total)

    def _finish(self, ok: int, total: int):
        self._processing = False
        self._go_btn.configure(state="normal", text="Processar imagens")
        messagebox.showinfo(
            "Processamento concluido",
            f"{ok} de {total} imagens processadas com sucesso.\n\nSalvas em:\n{self._output_dir}",
        )


if __name__ == "__main__":
    app = TrimApp()
    app.mainloop()
