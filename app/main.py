import tkinter as tk
import threading
import time
import os
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.importers.csv_importer import read_csv
from app.importers.excel_importer import read_xlsx
from app.importers.pdf_importer import read_pdf
from app.whatsapp_sender import WhatsAppSender


class WhatsAppSenderApp(tk.Tk):
    """Main window for the first UI milestone."""

    DEFAULT_APPOINTMENT_MESSAGE = (
        "Olá, [nome]! 😊\n"
        "Somos da equipe da unidade de saúde.\n\n"
        "Estamos passando para lembrar que você tem uma consulta com Clínico Geral "
        "agendada para:\n\n"
        "📅 *[data]*\n"
        "🕐 *[horario]*\n\n"
        "Se tiver alguma dúvida sobre o seu agendamento, pode falar com a gente por "
        "aqui. Pedimos apenas que envie sua mensagem por *escrito*, pois *não "
        "conseguimos ouvir áudios nem atender ligações* por este número.\n\n"
        "Caso não consiga comparecer, é só responder CANCELAR para nos avisar.\n\n"
        "Agradecemos pela atenção e esperamos você! 💙"
    )

    def __init__(self) -> None:
        super().__init__()
        self.file_batches: list[dict] = []  # List of {path, name, contacts, status}
        self.is_paused = False
        self.is_stopped = False
        self.use_edited_general_message = False
        self.sender: WhatsAppSender | None = None
        self._configure_window()
        self._build_styles()
        self._build_layout()

    def _configure_window(self) -> None:
        self.title("WhatsApp Message Sender")
        self.geometry("900x650")
        self.minsize(760, 560)
        self.configure(bg="#f4f6f8")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f6f8")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure(
            "Title.TLabel",
            background="#f4f6f8",
            foreground="#17212b",
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#f4f6f8",
            foreground="#65727e",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel",
            background="#ffffff",
            foreground="#17212b",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "MetricValue.TLabel",
            background="#ffffff",
            foreground="#17212b",
            font=("Segoe UI", 19, "bold"),
        )
        style.configure(
            "MetricLabel.TLabel",
            background="#ffffff",
            foreground="#65727e",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton",
            background="#1f7a5a",
            foreground="#ffffff",
            borderwidth=0,
            padding=(18, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Primary.TButton", background=[("active", "#176044")])
        style.configure(
            "Secondary.TButton",
            background="#e9eef1",
            foreground="#17212b",
            borderwidth=0,
            padding=(14, 9),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Secondary.TButton", background=[("active", "#dce4e8")])
        style.configure(
            "TEntry",
            fieldbackground="#f8fafb",
            bordercolor="#d7e0e5",
            padding=8,
        )
        style.configure("Status.TLabel", background="#edf7f2", foreground="#176044", padding=10)

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=(34, 28))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        ttk.Label(root, text="WhatsApp Message Sender", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            root,
            text="Envio individual com controle, pausa e histórico local.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 22))

        message_card = ttk.Frame(root, style="Card.TFrame", padding=20)
        message_card.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        message_card.columnconfigure(0, weight=1)
        ttk.Label(message_card, text="Mensagem geral", style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            message_card,
            text="Use [nome] para inserir automaticamente o nome de cada paciente.",
            background="#ffffff",
            foreground="#65727e",
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))

        self.message_preview = ttk.Label(
            message_card,
            text="Modo atual: mensagem padrão de agendamento.",
            background="#ffffff",
            foreground="#17212b",
            font=("Segoe UI", 10),
        )
        self.message_preview.grid(row=2, column=0, sticky="w", pady=(0, 10))

        ttk.Button(
            message_card,
            text="Editar mensagem geral",
            style="Secondary.TButton",
            command=self._open_general_message_editor,
        ).grid(row=3, column=0, sticky="w")
        ttk.Button(
            message_card,
            text="Usar mensagem padrão",
            style="Secondary.TButton",
            command=self._restore_default_general_message,
        ).grid(row=3, column=0, sticky="w", padx=(180, 0))

        # Hidden storage used by the sending flow and the per-contact editor.
        self.message_text = tk.Text(
            message_card,
            height=5,
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            bg="#f8fafb",
            fg="#17212b",
            insertbackground="#1f7a5a",
            font=("Segoe UI", 11),
        )
        self.message_text.insert("1.0", self.DEFAULT_APPOINTMENT_MESSAGE)

        controls = ttk.Frame(root)
        controls.grid(row=3, column=0, sticky="nsew")
        controls.columnconfigure(0, weight=1)
        controls.rowconfigure(1, weight=1)

        import_card = ttk.Frame(controls, style="Card.TFrame", padding=20)
        import_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        import_card.columnconfigure(1, weight=1)
        ttk.Button(
            import_card,
            text="+ Adicionar arquivo",
            style="Secondary.TButton",
            command=self._import_contacts,
        ).grid(row=0, column=0, padx=(0, 14))
        ttk.Label(
            import_card,
            text="Modo Lote: Adicione múltiplos PDF/Excel/CSV",
            background="#ffffff",
            foreground="#65727e",
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, sticky="w")

        # File batch list
        self.batch_listbox = tk.Listbox(
            import_card,
            height=4,
            bg="#f8fafb",
            fg="#17212b",
            font=("Segoe UI", 9),
            relief="flat",
            borderwidth=1,
        )
        self.batch_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        import_card.rowconfigure(1, weight=1)

        # Buttons for batch management
        batch_buttons = ttk.Frame(import_card)
        batch_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(
            batch_buttons,
            text="Remover selecionado",
            style="Secondary.TButton",
            command=self._remove_batch,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            batch_buttons,
            text="Limpar tudo",
            style="Secondary.TButton",
            command=self._clear_batches,
        ).pack(side="left")

        summary_card = ttk.Frame(controls, style="Card.TFrame", padding=20)
        summary_card.grid(row=1, column=0, sticky="nsew", pady=(0, 14))
        summary_card.columnconfigure((0, 1, 2, 3), weight=1)
        self.metric_values: dict[str, ttk.Label] = {}
        metrics = [("total", "0", "Contatos"), ("sent", "0", "Enviados"), ("pending", "0", "Pendentes"), ("errors", "0", "Erros")]
        for column, (key, value, label) in enumerate(metrics):
            metric = ttk.Frame(summary_card, style="Card.TFrame")
            metric.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
            value_label = ttk.Label(metric, text=value, style="MetricValue.TLabel")
            value_label.pack(anchor="w")
            self.metric_values[key] = value_label
            ttk.Label(metric, text=label, style="MetricLabel.TLabel").pack(anchor="w", pady=(2, 0))

        self.contact_table = ttk.Treeview(summary_card, columns=("name", "phone", "status"), show="headings", height=8)
        self.contact_table.heading("name", text="Nome")
        self.contact_table.heading("phone", text="Telefone")
        self.contact_table.heading("status", text="Status")
        self.contact_table.column("name", width=220, anchor="w")
        self.contact_table.column("phone", width=180, anchor="w")
        self.contact_table.column("status", width=120, anchor="w")
        self.contact_table.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(18, 0))
        self.contact_table.bind("<<TreeviewSelect>>", self._on_contact_selected)
        summary_card.rowconfigure(1, weight=1)

        # Message editor for selected contact
        editor_card = ttk.Frame(controls, style="Card.TFrame", padding=20)
        editor_card.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        editor_card.columnconfigure(0, weight=1)
        ttk.Label(editor_card, text="Editar Mensagem de Contato", style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            editor_card,
            text="Selecione um contato acima para editar sua mensagem individualmente",
            background="#ffffff",
            foreground="#65727e",
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))
        
        self.selected_contact_label = ttk.Label(
            editor_card,
            text="Nenhum contato selecionado",
            background="#ffffff",
            foreground="#17212b",
            font=("Segoe UI", 9, "bold"),
        )
        self.selected_contact_label.grid(row=2, column=0, sticky="w")
        
        self.message_editor = tk.Text(
            editor_card,
            height=4,
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            bg="#f8fafb",
            fg="#17212b",
            insertbackground="#1f7a5a",
            font=("Segoe UI", 10),
            state="disabled",
        )
        self.message_editor.grid(row=3, column=0, sticky="ew", pady=(10, 10))
        editor_card.rowconfigure(3, weight=1)
        
        editor_buttons = ttk.Frame(editor_card)
        editor_buttons.grid(row=4, column=0, sticky="ew")
        ttk.Button(
            editor_buttons,
            text="Salvar Mensagem",
            style="Secondary.TButton",
            command=self._save_contact_message,
            state="disabled",
        ).pack(side="left", padx=(0, 8))
        self.reset_button = ttk.Button(
            editor_buttons,
            text="Restaurar Padrão",
            style="Secondary.TButton",
            command=self._reset_contact_message,
            state="disabled",
        )
        self.reset_button.pack(side="left")
        
        # Store references to buttons for state control
        self.save_message_button = editor_buttons.winfo_children()[0]
        self.current_contact_idx = None

        footer = ttk.Frame(root)
        footer.grid(row=4, column=0, sticky="ew")
        footer.columnconfigure(3, weight=1)
        self.start_button = ttk.Button(footer, text="Iniciar", style="Primary.TButton", command=self._start)
        self.start_button.grid(row=0, column=0, padx=(0, 8))
        self.pause_button = ttk.Button(footer, text="Pausar", style="Secondary.TButton", command=self._pause, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=4)
        self.stop_button = ttk.Button(footer, text="Parar", style="Secondary.TButton", command=self._stop, state="disabled")
        self.stop_button.grid(row=0, column=2, padx=4)
        self.status_label = ttk.Label(footer, text="Aguardando configuracao", style="Status.TLabel")
        self.status_label.grid(row=0, column=4, sticky="e", padx=(16, 0))

    def _open_general_message_editor(self) -> None:
        """Open a modal editor for the message sent to every contact."""
        editor_window = tk.Toplevel(self)
        editor_window.title("Editar mensagem geral")
        editor_window.geometry("650x380")
        editor_window.minsize(520, 300)
        editor_window.transient(self)
        editor_window.grab_set()
        editor_window.configure(bg="#f4f6f8")

        container = ttk.Frame(editor_window, padding=24)
        container.pack(fill="both", expand=True)
        ttk.Label(
            container,
            text="Editar mensagem geral",
            style="Section.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            container,
            text="Use [nome] para personalizar a mensagem para cada paciente.",
            background="#f4f6f8",
            foreground="#65727e",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 12))

        editor = tk.Text(
            container,
            height=10,
            wrap="word",
            relief="flat",
            borderwidth=1,
            padx=12,
            pady=12,
            bg="#ffffff",
            fg="#17212b",
            insertbackground="#1f7a5a",
            font=("Segoe UI", 11),
        )
        editor.pack(fill="both", expand=True)
        editor.insert("1.0", self.message_text.get("1.0", "end").strip())
        editor.focus_set()

        buttons = ttk.Frame(container)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(
            buttons,
            text="Cancelar",
            style="Secondary.TButton",
            command=editor_window.destroy,
        ).pack(side="right")
        ttk.Button(
            buttons,
            text="Salvar mensagem geral",
            style="Primary.TButton",
            command=lambda: self._save_general_message(editor, editor_window),
        ).pack(side="right", padx=(0, 8))

    def _save_general_message(self, editor: tk.Text, editor_window: tk.Toplevel) -> None:
        message = editor.get("1.0", "end").strip()
        if not message:
            messagebox.showwarning("Mensagem vazia", "Digite uma mensagem antes de salvar.")
            return

        confirmed = messagebox.askyesno(
            "Confirmar mensagem editada",
            "Ao confirmar, a mensagem editada substituirá a mensagem padrão e "
            "será enviada para todos os pacientes. Deseja continuar?",
            parent=editor_window,
        )
        if not confirmed:
            return

        self.message_text.delete("1.0", "end")
        self.message_text.insert("1.0", message)
        self.use_edited_general_message = True
        self.message_preview.configure(
            text="Modo atual: mensagem geral EDITADA será enviada para todos."
        )
        editor_window.destroy()
        messagebox.showinfo(
            "Mensagem editada ativada",
            "Confirmado: a mensagem a ser enviada será a editada, e não a padrão.",
            parent=self,
        )

    def _restore_default_general_message(self) -> None:
        self.message_text.delete("1.0", "end")
        self.message_text.insert("1.0", self.DEFAULT_APPOINTMENT_MESSAGE)
        self.use_edited_general_message = False
        self.message_preview.configure(
            text="Modo atual: mensagem padrão de agendamento."
        )
        messagebox.showinfo(
            "Mensagem padrão ativada",
            "A mensagem padrão voltará a ser enviada aos pacientes.",
            parent=self,
        )

    @staticmethod
    def _personalize_message(message: str, contact: dict) -> str:
        """Replace supported patient placeholders."""
        return (
            message.replace("[nome]", contact["name"])
            .replace("{nome}", contact["name"])
            .replace("[data]", str(contact.get("data", "")))
            .replace("[horario]", str(contact.get("horario", "")))
        )

    def _import_contacts(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Selecionar lista de contatos (múltiplos arquivos)",
            filetypes=[("Arquivos suportados", "*.pdf *.csv *.xlsx"), ("PDF", "*.pdf"), ("CSV", "*.csv"), ("Excel", "*.xlsx")],
        )
        if selected:
            for file_path in selected:
                path = Path(file_path)
                try:
                    suffix = path.suffix.lower()
                    if suffix == ".csv":
                        contacts = read_csv(path)
                    elif suffix == ".xlsx":
                        contacts = read_xlsx(path)
                    else:
                        contacts = read_pdf(path)
                except (OSError, RuntimeError, ValueError) as error:
                    messagebox.showerror("Falha na importacao", f"{path.name}: {str(error)}")
                    continue
                
                # Add to batch list
                batch = {
                    "path": path,
                    "name": path.name,
                    "contacts": contacts,
                    "status": "Pendente",
                    "sent": 0,
                    "errors": 0,
                }
                self.file_batches.append(batch)
            
            self._refresh_batch_list()
            self._refresh_contacts()

    def _refresh_batch_list(self) -> None:
        """Update the batch file list display"""
        self.batch_listbox.delete(0, tk.END)
        total_contacts = 0
        for idx, batch in enumerate(self.file_batches):
            total = len(batch["contacts"])
            total_contacts += total
            display = f"{idx + 1}. {batch['name']} ({total} contatos) - {batch['status']}"
            self.batch_listbox.insert(tk.END, display)
        
        # Update file label with summary
        if self.file_batches:
            status_text = f"{len(self.file_batches)} arquivo(s) - {total_contacts} contato(s) total"
            self.status_label.configure(text=status_text, foreground="#176044")
        else:
            self.status_label.configure(text="Aguardando configuracao", foreground="#65727e")

    def _remove_batch(self) -> None:
        """Remove selected batch from list"""
        selection = self.batch_listbox.curselection()
        if selection:
            idx = selection[0]
            self.file_batches.pop(idx)
            self._refresh_batch_list()
            self._refresh_contacts()

    def _clear_batches(self) -> None:
        """Clear all batches"""
        if self.file_batches:
            if messagebox.askyesno("Confirmar", "Limpar todos os arquivos?"):
                self.file_batches = []
                self._refresh_batch_list()
                self._refresh_contacts()

    def _get_all_contacts(self) -> list[dict]:
        """Get all contacts from all batches"""
        all_contacts = []
        for batch in self.file_batches:
            for contact in batch["contacts"]:
                # Add batch reference for reporting
                contact["_batch_idx"] = len(all_contacts)
                all_contacts.append(contact)
        return all_contacts

    def _on_contact_selected(self, event) -> None:
        """Handle contact selection in table"""
        selection = self.contact_table.selection()
        if not selection:
            self.current_contact_idx = None
            self.selected_contact_label.configure(text="Nenhum contato selecionado")
            self.message_editor.configure(state="disabled")
            self.save_message_button.configure(state="disabled")
            self.reset_button.configure(state="disabled")
            return
        
        # Get selected contact index
        all_contacts = self._get_all_contacts()
        selected_item = selection[0]
        item_index = self.contact_table.index(selected_item)
        
        if item_index >= len(all_contacts):
            return
        
        contact = all_contacts[item_index]
        self.current_contact_idx = item_index
        
        # Update label with contact info
        self.selected_contact_label.configure(
            text=f"📱 {contact['name']} - {contact['phone']}"
        )
        
        # Load message for this contact
        self.message_editor.configure(state="normal")
        self.message_editor.delete("1.0", "end")
        
        if "custom_message" in contact:
            # Show custom message if exists
            self.message_editor.insert("1.0", contact["custom_message"])
            self.reset_button.configure(state="normal")
        else:
            # Show default message
            default_msg = self.message_text.get("1.0", "end").strip()
            self.message_editor.insert("1.0", default_msg)
            self.reset_button.configure(state="normal")
        
        self.save_message_button.configure(state="normal")

    def _save_contact_message(self) -> None:
        """Save custom message for selected contact"""
        if self.current_contact_idx is None:
            messagebox.showwarning("Erro", "Nenhum contato selecionado")
            return
        
        all_contacts = self._get_all_contacts()
        contact = all_contacts[self.current_contact_idx]
        
        custom_msg = self.message_editor.get("1.0", "end").strip()
        if not custom_msg:
            messagebox.showwarning("Erro", "A mensagem não pode estar vazia")
            return
        
        contact["custom_message"] = custom_msg
        messagebox.showinfo("Sucesso", f"Mensagem salva para {contact['name']}")
        self._refresh_contacts()

    def _reset_contact_message(self) -> None:
        """Reset contact message to default"""
        if self.current_contact_idx is None:
            return
        
        all_contacts = self._get_all_contacts()
        contact = all_contacts[self.current_contact_idx]
        
        if "custom_message" in contact:
            del contact["custom_message"]
            messagebox.showinfo("Sucesso", f"Mensagem de {contact['name']} restaurada para padrão")
            
            # Reload the editor
            self.message_editor.configure(state="normal")
            self.message_editor.delete("1.0", "end")
            default_msg = self.message_text.get("1.0", "end").strip()
            self.message_editor.insert("1.0", default_msg)
            self.reset_button.configure(state="disabled")
            self._refresh_contacts()
        else:
            messagebox.showinfo("Info", f"{contact['name']} já está usando a mensagem padrão")

    def _refresh_contacts(self) -> None:
        for item in self.contact_table.get_children():
            self.contact_table.delete(item)
        
        all_contacts = self._get_all_contacts()
        for contact in all_contacts:
            self.contact_table.insert("", "end", values=(contact["name"], contact["phone"], contact["status"]))
        
        sent = sum(contact["status"] == "Enviado" for contact in all_contacts)
        errors = sum(contact["status"] == "Erro" for contact in all_contacts)
        self.metric_values["total"].configure(text=str(len(all_contacts)))
        self.metric_values["sent"].configure(text=str(sent))
        self.metric_values["pending"].configure(text=str(len(all_contacts) - sent - errors))
        self.metric_values["errors"].configure(text=str(errors))

    def _start(self) -> None:
        if not self.file_batches:
            messagebox.showinfo("Importe uma lista", "Adicione pelo menos um arquivo com contatos antes de iniciar.")
            return
        message = self.message_text.get("1.0", "end").strip()
        if not message:
            messagebox.showinfo("Digite uma mensagem", "Informe a mensagem antes de iniciar.")
            return

        # Let webdriver-manager select a driver that matches the installed Edge.
        # A manually downloaded, outdated driver can start Edge and crash at once.
        driver_path = None

        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        self.is_stopped = False
        self.is_paused = False
        self.status_label.configure(text="Abrindo WhatsApp Web...")
        threading.Thread(
            target=self._send_contacts,
            args=(driver_path, message, self.use_edited_general_message),
            daemon=True,
        ).start()

    def _find_edgedriver(self) -> Path | None:
        candidates = [
            Path.home() / "Downloads" / "edgedriver_win64" / "msedgedriver.exe",
            Path.home() / "Downloads" / "edgedriver_win64" / "edgedriver" / "msedgedriver.exe",
            Path(__file__).resolve().parent.parent / "drivers" / "msedgedriver.exe",
        ]
        return next((path for path in candidates if path.exists()), None)

    def _send_contacts(
        self,
        driver_path: Path | None,
        message: str,
        use_edited_general_message: bool,
    ) -> None:
        try:
            self.sender = WhatsAppSender(
                driver_path,
                profile_path=Path.home() / "whatsapp_edge_profile",
                debugger_address=os.getenv("EDGE_DEBUGGER_ADDRESS"),
            )
            self._set_status("Escaneie o QR Code se necessario")
            time.sleep(5)
            
            # Process each batch
            for batch_idx, batch in enumerate(self.file_batches):
                self._set_status(f"Processando arquivo {batch_idx + 1}/{len(self.file_batches)}: {batch['name']}")
                batch["status"] = "Enviando"
                batch["sent"] = 0
                batch["errors"] = 0
                self._refresh_batch_list()
                
                for contact_idx, contact in enumerate(batch["contacts"]):
                    while self.is_paused and not self.is_stopped:
                        time.sleep(0.2)
                    if self.is_stopped:
                        return
                    
                    if use_edited_general_message:
                        # An explicitly confirmed general edit overrides every contact.
                        msg_to_send = message
                    elif "custom_message" in contact:
                        msg_to_send = contact["custom_message"]
                    else:
                        msg_to_send = contact.get(
                            "message", self.DEFAULT_APPOINTMENT_MESSAGE
                        )
                    personalized = self._personalize_message(
                        msg_to_send, contact
                    )
                    
                    
                    try:
                        self.sender.send(contact["phone"], personalized)
                        contact["status"] = "Enviado"
                        batch["sent"] += 1
                    except Exception:
                        contact["status"] = "Erro"
                        batch["errors"] += 1
                    
                    self.after(0, self._refresh_contacts)
                    self._set_status(
                        f"[{batch_idx + 1}/{len(self.file_batches)}] {batch['name']} - "
                        f"{contact_idx + 1}/{len(batch['contacts'])} contatos"
                    )
                    time.sleep(4)
                
                batch["status"] = "Concluído"
                self._refresh_batch_list()
            
            self._show_final_report()
        except Exception as error:
            self._set_status(self._friendly_error_message(error))
        finally:
            if self.sender is not None:
                try:
                    self.sender.close()
                except Exception:
                    pass
                self.sender = None
            self.after(0, self._finish_sending)

    @staticmethod
    def _friendly_error_message(error: Exception) -> str:
        details = str(error)
        technical_markers = (
            "session not created",
            "devtoolsactiveport",
            "stacktrace:",
            "msedgedriver!",
        )
        if any(marker in details.lower() for marker in technical_markers):
            return (
                "Nao foi possivel iniciar o Microsoft Edge. Feche as outras janelas "
                "do WhatsApp Message Sender e tente novamente com o executavel atualizado."
            )
        return details

    def _show_final_report(self) -> None:
        """Show final report of all batches"""
        total_sent = sum(batch["sent"] for batch in self.file_batches)
        total_errors = sum(batch["errors"] for batch in self.file_batches)
        
        report = "RELATÓRIO FINAL\n" + "=" * 50 + "\n\n"
        for batch in self.file_batches:
            report += f"📄 {batch['name']}\n"
            report += f"   Total: {len(batch['contacts'])} contatos\n"
            report += f"   ✅ Enviados: {batch['sent']}\n"
            report += f"   ❌ Erros: {batch['errors']}\n\n"
        
        report += "=" * 50 + "\n"
        report += f"TOTAL GERAL\n"
        report += f"✅ Enviados: {total_sent}\n"
        report += f"❌ Erros: {total_errors}\n"
        
        messagebox.showinfo("Envio Concluído", report)
        self._set_status(f"✅ Envio concluído: {total_sent} enviados, {total_errors} erros")

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=text))

    def _finish_sending(self) -> None:
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="Pausar")
        self.stop_button.configure(state="disabled")

    def _pause(self) -> None:
        self.is_paused = not self.is_paused
        self.pause_button.configure(text="Continuar" if self.is_paused else "Pausar")
        self.status_label.configure(text="Pausado" if self.is_paused else "Processando")

    def _stop(self) -> None:
        self.is_stopped = True
        self.is_paused = False
        self.status_label.configure(text="Envio parado")

    def _on_close(self) -> None:
        """Stop the worker and release Edge when the application is closed."""
        self.is_stopped = True
        self.is_paused = False
        if self.sender is not None:
            try:
                self.sender.close()
            except Exception:
                pass
            self.sender = None
        self.destroy()


if __name__ == "__main__":
    app = WhatsAppSenderApp()
    app.mainloop()
