import json


class JsonUtils:

    @staticmethod
    def create_json_file(json_meta, path):
        """
        Create json file with the meta data
        :param json_meta: data to create json file
        :param path: path to create json file
        :return: return success status
        """
        file_name = json_meta.get('message_id')
        with open(f'{path}/{file_name}.json', 'w') as outfile:
            json.dump(json_meta, outfile, indent=4)
        return True
