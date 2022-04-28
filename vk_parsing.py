import vk
import json
import time
import datetime
import re


class VkCommentsParsing:
    def __init__(self):
        self.vk_api = self.connect_api()

    # Подключение к API
    @staticmethod
    def connect_api(token):
        session = vk.Session(access_token=token)
        return vk.API(session)

    # Получение owner_id паблика по домену
    def get_owner_id_by_domain(self, domain):
        id = self.vk_api.utils.resolveScreenName(screen_name=domain, v=5.92)
        return -id['object_id']

    # Получение id постов за с заданной даты по текущую
    def get_public_posts_ids(self, owner_id, date_start):
        ids = []
        date_end = time.time()
        date_start = time.mktime(datetime.datetime.strptime(date_start, "%d/%m/%Y").timetuple())
        it = 0

        while date_end > date_start:
            posts = self.vk_api.wall.get(owner_id=owner_id, count=100, offset=100*it, v=5.92)
            
            for post in posts['items']:
                if post['date'] < date_start:
                    date_end = post['date']
                else:
                    ids.append(post['id'])

            it += 1
        return ids

    # Получение комментариев поста
    def get_post_comments(self, owner_id, post_id):
        comments = []
        first = self.vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, count=100, v=5.92)
        comments += first['items']

        count_offset = first['count'] // 100

        for i in range(1, count_offset+1):
            comments += self.vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, count=100, offset=i*100, v=5.92)['items']
        
        sub_comments = []
        for comment in comments:
            sub_first = self.vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, comment_id=comment['id'], count=100, v=5.92)
            sub_comments += sub_first['items']
            
            count_sub_offset = sub_first['count'] // 100
            for i in range(1, count_sub_offset+1):
                sub_comments += self.vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, comment_id=comment['id'], count=100, offset=i*100, v=5.92)['items']

        comments += sub_comments

        return comments

    # Получение текста всех комментариев по всем доменам
    def get_all_comments_text(self, domains, date_end):
        all_comments = []
        for domain in domains:
            owner_id = self.get_owner_id_by_domain(domain)
            post_ids = self.get_public_posts_ids(owner_id, date_end)

            for post in post_ids:
                post_comments = self.get_post_comments(owner_id, post)
                comments_text = self.get_comments_text(post_comments)
                all_comments += comments_text

        return all_comments

    # Получение текста комментариев по объектам
    @staticmethod
    def get_comments_text(comments):
        comments_text = []

        for comment in comments:
            if 'deleted' in comment or comment['text'] == "":
                continue

            text = comment['text']
            text = text.replace("\n", "")
            text = re.sub(r'\[.*\|.*\],', '', text)  # без обращений
            text = re.sub('[^\x00-\x7Fа-яА-Я]', '', text)  # без смайликов
            text = re.sub(" +", " ", text)  # без лишних пробелов
            text = re.sub("\"", "", text)
            text = text.strip()

            if text != "" and len(text) > 30:  # больше 30 символов
                comments_text.append(text)
        
        return comments_text

    @staticmethod
    def write_json(filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
