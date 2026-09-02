import unittest
from unittest.mock import patch

from app.main import WhatsAppSenderApp


class MessageModeTests(unittest.TestCase):
    def test_default_message_uses_pdf_patient_fields(self) -> None:
        contact = {
            "name": "Mariana",
            "data": "10/09/2026",
            "horario": "14:30",
        }

        result = WhatsAppSenderApp._personalize_message(
            WhatsAppSenderApp.DEFAULT_APPOINTMENT_MESSAGE,
            contact,
        )

        self.assertIn("Mariana", result)
        self.assertIn("10/09/2026", result)
        self.assertIn("14:30", result)

    def test_edited_message_replaces_patient_name(self) -> None:
        result = WhatsAppSenderApp._personalize_message(
            "Olá [nome], sua consulta foi alterada.",
            {"name": "Pedro"},
        )

        self.assertEqual("Olá Pedro, sua consulta foi alterada.", result)

    def test_confirmed_edit_changes_mode_and_default_can_be_restored(self) -> None:
        app = WhatsAppSenderApp()
        app.withdraw()
        editor_window = None
        try:
            app._open_general_message_editor()
            editor_window = next(
                widget
                for widget in app.winfo_children()
                if widget.winfo_class() == "Toplevel"
            )

            def descendants(widget):
                children = []
                for child in widget.winfo_children():
                    children.append(child)
                    children.extend(descendants(child))
                return children

            editor = next(
                widget
                for widget in descendants(editor_window)
                if widget.winfo_class() == "Text"
            )
            editor.delete("1.0", "end")
            editor.insert("1.0", "Olá [nome]")

            with (
                patch("app.main.messagebox.askyesno", return_value=True),
                patch("app.main.messagebox.showinfo"),
            ):
                app._save_general_message(editor, editor_window)

            self.assertTrue(app.use_edited_general_message)

            with patch("app.main.messagebox.showinfo"):
                app._restore_default_general_message()

            self.assertFalse(app.use_edited_general_message)
            self.assertIn("[data]", app.message_text.get("1.0", "end"))
        finally:
            if editor_window is not None and editor_window.winfo_exists():
                editor_window.destroy()
            app.destroy()


if __name__ == "__main__":
    unittest.main()
