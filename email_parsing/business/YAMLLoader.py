import yaml

from model.instruction import Instruction


class YAMLLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_yaml(self):
        """
        Parse the instruction from YAML file
        :return: instruction object or None
        """
        with open(self.file_path) as yaml_file:
            data = yaml.load(yaml_file, yaml.FullLoader)

        if data:
            replace_rules_list = data[1]['replace_rules']
            replace_rules = {}
            for index in range(0, len(replace_rules_list), 2):
                replace_rules.update({replace_rules_list[index]['find']: replace_rules_list[index+1]['replace_with']})

            instruction = Instruction(data[0]['msg_file_path'], data[1]['attachments_download_path'], replace_rules)
            return instruction
        return None
