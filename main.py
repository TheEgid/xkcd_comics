import requests
import os
import sys
import random
import vk_api
from dotenv import load_dotenv
import logging
import argparse


class VKApiPostingError(Exception):
    """Declare special exception."""
    pass


def get_file_extension(url):
    """Get extension from url."""
    return '.' + url.split('.')[-1]


def get_comics_total_qty():
    url = 'https://www.xkcd.com/info.0.json'
    response = requests.get(url=url)
    if response.ok:
        return response.json()['num']
    else:
        return None


def get_random_comics_number():
    comics_total_qty = get_comics_total_qty()
    if comics_total_qty is not None:
        return random.randint(1, comics_total_qty)
    else:
        return None


def save_picture(url, comics_number, path='images/'):
    path = path + str(comics_number)
    dir_name = path.split('/')[0]
    if not os.path.exists(dir_name):
         os.makedirs(dir_name)
    filename = path + get_file_extension(url)
    response = requests.get(url)
    if response.ok:
        with open(filename, 'wb') as f:
            f.write(response.content)
            logging.info('Download & saved ' + filename)
        return filename
    else:
        return None


def post_vkontakte(login, password, token, vk_group, vk_group_album,
            content_text, content_img_file_pathname):
    vk_session = vk_api.VkApi(login, password)
    try:
        vk_session.auth(token_only=True)
    except vk_api.exceptions:
         vk_api.AuthError()
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)
    img = upload.photo(photos=content_img_file_pathname,
                       album_id=vk_group_album,
                       group_id=vk_group)
    attach = 'photo{}_{}'.format(img[0]['owner_id'], img[0]['id'])
    vk_group = int(vk_group) * -1
    vk.wall.post(message=content_text,
                 access_token=token,
                 owner_id=vk_group,
                 attachments=attach)
    wallpostsdict = vk.wall.get(count=1, owner_id=vk_group)['items'][0]
    if wallpostsdict['text'] != content_text:
        raise VKApiPostingError()


def download_comics(comics_number):
    image_url = r'http://xkcd.com/{}/info.0.json'.format(comics_number)
    response = requests.get(image_url)
    image_link = response.json()['img']
    comment = response.json()['alt']
    img_file_pathname = save_picture(url=image_link, comics_number=comics_number)
    return img_file_pathname, comment


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, help='only 1 command: start')
    return parser


def main():
    load_dotenv()
    LOGIN_VK = os.getenv("LOGIN_VK")
    PASSWORD_VK = os.getenv("PASSWORD_VK")
    TOKEN_VK = os.getenv("TOKEN_VK")
    GROUP_ID_VK = os.getenv("GROUP_ID_VK")
    GROUP_ID_ALBUM_VK = os.getenv("GROUP_ID_ALBUM_VK")
    comics_number = get_random_comics_number()
    img_file_pathname, comment = download_comics(comics_number)
    post_vkontakte(login=LOGIN_VK, password=PASSWORD_VK,
                   token=TOKEN_VK,
                   vk_group=GROUP_ID_VK,
                   vk_group_album=GROUP_ID_ALBUM_VK,
                   content_text=comment,
                   content_img_file_pathname=img_file_pathname)
    os.remove(img_file_pathname)
    logging.info('Success publish: №{} published'.format(comics_number))


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    logging.basicConfig(level=logging.INFO)
    arg_parser = get_args_parser()
    args = arg_parser.parse_args()
    if args.command == "start":
        main()
    else:
        logging.info('Wrong command - only 1 command: start')
