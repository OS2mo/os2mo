# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel
from ramodels import lora
from ramodels import mo


def model_writer(model_list: Iterator[BaseModel], md_file: Path) -> None:
    def to_schema_string(model: BaseModel):
        model_title = model.schema().get("title")
        schema = model.schema_json(indent=2)
        return f"## {model_title}\n```json\n {schema} \n```"

    md_file.write_text("\n".join(map(to_schema_string, model_list)))


def main() -> None:
    docs_path = Path(__file__).parent

    mo_objs: Iterator = map(mo.__dict__.get, mo.__all__)
    mo_models: Iterator[BaseModel] = filter(lambda obj: obj is not None, mo_objs)
    mo_models = filter(lambda model: model is not mo.MOBase, mo_models)

    lora_objs: Iterator = map(lora.__dict__.get, lora.__all__)
    lora_models: Iterator[BaseModel] = filter(lambda obj: obj is not None, lora_objs)
    lora_models = filter(lambda model: model is not lora.LoraBase, lora_models)

    model_writer(mo_models, docs_path / "mo/schemas.md")
    model_writer(lora_models, docs_path / "lora/schemas.md")


if __name__ == "__main__":
    main()
