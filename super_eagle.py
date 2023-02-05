import requests
from hashlib import md5


class SuperEagleClient(object):
    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, codetype):
        """
        im: Image bytes
        codetype: question types refer to https://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('https://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def post_pic_base64(self, base64_str, codetype):
        """
        im: Image bytes
        codetype: question types refer to https://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
            'file_base64': base64_str
        }
        params.update(self.base_params)
        r = requests.post('https://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """
        im_id: Picture id of the wrong question
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('https://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    superEagle = SuperEagleClient('2027231725', 'q2027231725', '944623')
    img = open('images/test.jpg', 'rb').read()
    print(superEagle.post_pic(img, 1902))
