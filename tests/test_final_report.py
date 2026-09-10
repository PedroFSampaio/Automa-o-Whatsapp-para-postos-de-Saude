import unittest

from app.main import WhatsAppSenderApp


class FinalReportTests(unittest.TestCase):
    def test_report_lists_failed_patient_name_and_phone(self) -> None:
        app = object.__new__(WhatsAppSenderApp)
        app.file_batches = [
            {
                "name": "agenda.pdf",
                "contacts": [
                    {
                        "name": "Mariana",
                        "phone": "5514991139046",
                        "status": "Erro",
                    },
                    {
                        "name": "Pedro",
                        "phone": "5514999999999",
                        "status": "Enviado",
                    },
                ],
                "sent": 1,
                "errors": 1,
            }
        ]

        report = app._build_final_report()

        self.assertIn("Pacientes com erro:", report)
        self.assertIn("Mariana (+55 (14) 99113-9046)", report)
        self.assertIn("Com erro: Mariana", report)
        self.assertNotIn("Com erro: Pedro", report)


if __name__ == "__main__":
    unittest.main()
