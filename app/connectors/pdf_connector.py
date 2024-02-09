import logging

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.db.schemas import Unstructured, UnstructuredInDB
from app.db.services import register_unstructured


class PDFConnector:
    def __init__(self, file_path) -> None:
        self.file_name = None
        self.file_description = None

        self.reader = PdfReader(file_path)
        self.content = self.read_content()

    def save_data(self, file_name: str, file_description: str):
        self.file_name = file_name
        self.file_description = file_description

    def read_content(self) -> str:
        text = ""
        for page in self.reader.pages:
            text += page.extract_text() + "\n"
        return text

    def get_data_content(self) -> str:
        return self.content

    def get_data_info(self) -> dict[str, str]:
        response = {
            "file_name": self.file_name,
            "file_description": self.file_description,
        }
        return response

    def get_specifications(self) -> dict[str, list[str]]:
        specs = {
            "inputs_required": ["file_name", "file_description"],
            "inputs_required_prompts": [
                "Please, provide a short but significant name to the file you just uploaded.",
                "Provide a detailed description of the usage of the file you just uploaded.",
            ],
        }
        return specs

    def upload_data(self, db: Session | None) -> list[UnstructuredInDB] | None:
        if self.file_name is None or self.file_description is None:
            raise Exception("Cannot upload data to database with missing information")

        unstructured = Unstructured(
            name=self.file_name, description=self.file_description, content=self.content
        )

        logging.info(f"Uploading PDF to SQL database: {unstructured}")
        if db is not None:
            db_object = register_unstructured(db, unstructured)
            return [UnstructuredInDB.model_validate(db_object)]
