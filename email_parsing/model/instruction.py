from dataclasses import dataclass


@dataclass
class Instruction:
    msg_file_path: str
    attachments_download_path: str
    replace_rules: dict
