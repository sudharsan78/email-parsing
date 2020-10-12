import re
import os
import logging
from email import message_from_file


class EmailParser:
    def __init__(self, instruction_obj):
        self.instruction_obj = instruction_obj

    def get_email_meta(self, msg_file_path):
        """
        Parse the email file and return meta data
        :param msg_file_path: email file path
        :return: email meta data
        """
        with open(msg_file_path) as eml_file:
            msg = message_from_file(eml_file)
            header_data = self.__parse_mail_headers(msg)
            body_data = self.__get_mail_data(msg)
            body_data['message_body'] = self.__replace_text(body_data['message_body'])
            body_data['attachments'] = self.__download_attachments(msg, header_data.get('message_id'))

            return {**header_data, **body_data}

    @staticmethod
    def __parse_mail_headers(msg):
        """
        Method to extract header data
        :param msg: message to extract header data
        :return: header dictionary
        """
        logging.debug('parsing mail header')
        return {
            'message_id': re.findall(r'<(.+?)>', msg.get('message-id'))[0],
            'from': re.findall(r'<(.+?)>', msg.get('from'))[0],
            'to': re.findall(r'<(.+?)>', msg.get('to')),
            'cc': re.findall(r'<(.+?)>', msg.get('cc')),
            'date': msg.get('date'),
            'subject': msg.get('subject')
        }

    @staticmethod
    def __get_mail_data(msg):
        """
        Method to extract body data from message
        :param msg: message to extract message body data
        :return: message body dictionary
        """
        logging.debug('parsing mail body')
        body_dic = {}
        if msg.is_multipart():
            for payload in msg.walk():
                if payload.get_content_type() == 'text/plain':
                    body_dic.update({
                        'multipart': 'TEXT',
                        'message_encoding': payload.get('content-transfer-encoding'),
                        'message_body': payload.get_payload()
                    })
                    break

                if payload.get_content_type() == 'text/html':
                    body_dic.update({
                        'multipart': 'HTML',
                        'message_encoding': payload.get('content-transfer-encoding'),
                        'message_body': payload.get_payload()
                    })
                    break
            return body_dic
        else:
            multipart = msg.get_content_charset()
            if multipart == 'text/plain':
                multipart = 'TEXT'
            else:
                multipart = 'HTML'
            body_dic.update({
                'multipart': multipart,
                'message_encoding': msg.get('content-transfer-encoding'),
                'message_body': msg.get_payload()
            })
            return body_dic

    def __download_attachments(self, msg, message_id):
        """
        Extract attachment from message and save the attachment
        :param msg: message to extract attachments
        :param message_id: message id to create folder for attachments
        :return: list of attachments details
        """
        logging.debug('Downloading attachments')
        attachment_list = []
        attachment_dir_path = self.instruction_obj.attachments_download_path
        if not os.path.isdir(attachment_dir_path):
            os.mkdir(attachment_dir_path)
        if msg.is_multipart():
            for payload in msg.walk():
                if payload.get_content_disposition() == 'attachment':
                    msg_attachment_dir_path = f'{attachment_dir_path}/{message_id}'
                    if not os.path.isdir(msg_attachment_dir_path):
                        os.mkdir(msg_attachment_dir_path)

                    file_name_with_path = f'{msg_attachment_dir_path}/{payload.get_filename()}'
                    with open(file_name_with_path, 'wb') as attachment:
                        attachment.write(payload.get_payload(decode=True))

                    attachment_list.append({
                        'file_name': payload.get_filename(),
                        'file_size': self.__convert_bytes(os.path.getsize(file_name_with_path)),
                        'file_mime_type': payload.get_content_type(),
                        'file_location': msg_attachment_dir_path})
        return attachment_list

    @staticmethod
    def __convert_bytes(byte_val):
        """
        Method to convert file size from bytes to human readable unit
        :param byte_val: byte value to convert
        :return: return human readable unit
        """
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if byte_val < 1024:
                return f'{byte_val:.1f} {unit}'
            byte_val /= 1024

    def __replace_text(self, msg_body):
        """
        Replace text in message body with replace instruction
        :param msg_body: message body to replace text from instruction
        :return: returned the message body
        """
        for replace_text, replace_with_text in self.instruction_obj.replace_rules.items():
            msg_body = msg_body.replace(replace_text, replace_with_text)
        return msg_body
