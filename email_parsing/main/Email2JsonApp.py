import os
import sys
import glob
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from business.YAMLLoader import YAMLLoader
from business.EmailParser import EmailParser
from business.JsonUtil import JsonUtils


class Email2Json:

    def create_json_from_email(self):
        """
        Parse email file and extract data and create json file with the email meta data
        :return: no of json file created
        """
        yaml_file_path = self.get_yaml_file()
        yaml_loader = YAMLLoader(yaml_file_path)
        instruction = yaml_loader.parse_yaml()
        if instruction is None:
            return 'Error : Instructions are empty'

        email_parser = EmailParser(instruction)
        files_created = 0
        for eml in glob.glob(f"{instruction.msg_file_path}/*.eml"):
            email_data = email_parser.get_email_meta(eml)
            if email_data:
                is_created = JsonUtils.create_json_file(email_data, instruction.msg_file_path)
                if is_created:
                    files_created += 1

        return f'{files_created} json files created'

    @staticmethod
    def get_yaml_file():
        """
        :return: YAML file path
        """
        file_path = ''
        got_file_path = False
        while not got_file_path:
            yaml_file = input('Please enter your YAML file for instruction : ')
            if yaml_file.endswith('.yaml'):
                if os.path.isfile(yaml_file):
                    file_path = yaml_file
                    got_file_path = True
                else:
                    print("Error : The entered YAML file doesn't exists")
            else:
                print('Error : Invalid file format. Please enter YAML file path only')
        return file_path


if __name__ == '__main__':
    email_2_json = Email2Json()
    ret_val = email_2_json.create_json_from_email()
    print(ret_val)
