import pytest

from run import app, create_tables


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        create_tables()

    yield client


def test_login(client):
    resp = client.post('/login', json=dict(username='nevil', password='longbottom'))
    assert resp.status_code == 200


def test_login_wrong_password(client):
    resp = client.post('/login', json=dict(username='nevil', password='granger'))
    assert resp.status_code == 401


def test_login_wrong_username(client):
    username = 'hermioneeeee'
    resp = client.post('/login', json=dict(username=username, password='granger'))
    assert resp.status_code == 200
    assert resp.json == {'message': f'User {username} doesn\'t exist'}


def test_login_missing_data(client):
    resp = client.post('/login', json=dict(username='hermione'))
    assert resp.status_code == 400


def test_access_token_wrong(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']
    refresh_token = resp.json['refresh_token']

    resp = client.post('/jsonpatch',
                       headers={'Authorization': f'Bearer {refresh_token}'},
                       json=dict(json_object='{"foo": "bar"}',
                                 json_patch='[{"op": "add", "path": "/baz", "value": "qux"}]'))
    assert resp.status_code == 422


def test_refresh_token(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']
    refresh_token = resp.json['refresh_token']

    resp = client.post('/token/refresh',
                       headers={'Authorization': f'Bearer {refresh_token}'})
    assert resp.status_code == 200
    assert access_token != resp.json['access_token']


def test_refresh_wrong(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']
    refresh_token = resp.json['refresh_token']

    resp = client.post('/token/refresh',
                       headers={'Authorization': f'Bearer {access_token}'})
    assert resp.status_code == 422


def test_json_patch(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']

    resp = client.post('/jsonpatch',
                       headers={'Authorization': f'Bearer {access_token}'},
                       json=dict(json_object='{"foo": "bar"}',
                                 json_patch='[{"op": "add", "path": "/baz", "value": "qux"}]'))
    assert resp.status_code == 200
    assert resp.json == {'foo': 'bar', 'baz': 'qux'}


def test_json_patch_invalid_patch(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']

    resp = client.post('/jsonpatch',
                       headers={'Authorization': f'Bearer {access_token}'},
                       json=dict(json_object='{"foo": "bar"}',
                                 json_patch='[{"op": "add", "path": "baz", "value": "qux"}]'))
    assert resp.status_code == 400
    assert resp.get_data() == b'Invalid JSON Patch'


def test_thumbnail_png(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']

    resp = client.post('/thumbnail',
                       headers={'Authorization': f'Bearer {access_token}'},
                       json=dict(image_url='https://miro.medium.com/max/569/1*0G5zu7CnXdMT9pGbYUTQLQ.png'))
    assert resp.status_code == 200
    img_data = resp.get_data()
    # with open('image.png', 'wb') as f:
    #     f.write(img_data)
    assert img_data == b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x002\x00\x00\x00\x1b\x08\x02\x00\x00\x00\xb1\xfeK\x18\x00\x00\x06\xb9IDATx\x9c\xcd\x96YL\x13]\x1b\xc7\xcfL[\xba\xa66\x01j\xb5\xa1"[\x94\xcdP\t\x10-KH\nh"\xa8$FE\x03b\x887%D\x91\x0b\xb9 \x045!n7\x12.\x88\xa0&DSP\xa21m#EQ\xa3\x05W\n%m\x81\xd6\x14\xdaB\xb1\xad],\xb6\xd3e\xcew1o\x88/`>\xde7|\xf8\xfd\xaff\x9es\xe6\x9c\xdf<\xcf\xff,\x00B\x08!4\x1a\x8d\x12\x89dpp\x10\xfe\x7f\x88\x0c\x00\x00\x00\xc4\xc7\xc7\xcf\xcf\xcf+\x14\n\x04AD"\x11\x8dF\x03\x7fV\x04\xdd\xf0\xf00\x9f\xcf\xe7p8\xbbw\xef\xbev\xed\x9a\xd1h\xfc\xb3\xd9B\t\xb8\x89\x89\t\x87\xc3\x91\x99\x99\xd9\xd4\xd4488\x98\x9b\x9b{\xe9\xd2\xa5\xf9\xf9\xf9?\x99\xad\xd6\xd6V\x81@\xc0\xe5r\x13\x13\x13\x8f\x1d;&\x97\xcb\x0b\x0b\x0b\x93\x92\x92ZZZ\xde\xbd{\xf7\xe1\xc3\x07\x1c\xc77;[*\x95\xea\xee\xdd\xbb6\x9b\x8d\xcb\xe5\xa6\xa5\xa5eeeA\x08\x95Je___uu\xb5Z\xad>}\xfatKK\xcb\xcf\x9f?73YH^^^qq\xf1\xcc\xccLss\xf3\xb7o\xdf(\x14\x8aF\xa3\xf1\xfb\xfd\\.\xd7\xe9tfgg\x0b\x85B\xbd^\x9f\x9e\x9e\xce`06\x0f\xeb\xc8\x91#\xdb\xb7o\x8f\x8b\x8b\x1b\x1f\x1fw\xbb\xddcccuuub\xb18\'\'G\xaf\xd7\xe38\x9e\x95\x95\xb5\xfa\xb3`0\xe8p8\x98L\xa6\xdf\xef\x07\x00\xe08N\xa1P\xa2\xa3\xa3\xd5ju\x7f\x7f\x7fcccLL\xcc\x7f\x9d\xdbl6\xf7\xf6\xf6\x16\x17\x17\xe7\xe6\xe6\xael;z\xf4(\x82 ,\x16+%%\xa5\xa6\xa6\xc6h4\x06\x83A\x08a$\x12ikk\x93\xc9dk\xd6\xde\xe3\xf1\xd4\xd4\xd4\xec\xdc\xb9\xb3\xb9\xb9\xb9\xad\xad\xed\xd4\xa9SEEE\xa1P\xa8\xa9\xa9\x89J\xa5.,,\xac\xc7@O\x9e<\xa1P(\x8f\x1f?^\xdd\x04\xa4R)\x82 \xdb\xb6mKNNnmm\xd5\xe9tO\x9f>\xc5q<\x12\x89\xd8\xed\xf6\xe1\xe1\xe1\xdf\r\xfa\xe2\xc5\x0b.\x97\xbb\xb4\xb4\x04!\x0c\x85B\xdd\xdd\xdd\x10B\x8b\xc5\x92\x94\x94d\xb3\xd9\xd6\x83\x05!\x14\x89D}}}\xab\xe3hnn\xae@ \xa0\xd1h"\x91\xa8\xb2\xb2\xf2\xe1\xc3\x87;v\xec@\x10\x04EQ&\x93\xf9\xfd\xfb\xf7\xdf\x96\x1fA(\x14\n\xf1\x8caXmm-QM\x14E\xd7m!\xb0<\xc2\n\x91\xe3\xe2\xe2\xf2\xf3\xf3\x95J\xa5V\xab\x95\xc9d\x05\x05\x05\x1c\x0e\xc7\xe5r\xcd\xce\xceF"\x11\x9f\xcf\x07!D\x10dM\xac`0866\x86 \x88L&kkk#\x91H\x08\x82D"\x91p8\x0c\x00\xf0\xfb\xfdr\xb9\\\xadV\xb3\xd9\xec\x86\x86\x86\xa8\xa8(\xb7\xdb\xfd\xe0\xc1\x03\xab\xd5\x1a\x1d\x1d\xdd\xd0\xd0@"\x91 \x84d2Y\xab\xd5>{\xf6\x8cN\xa7\x8bD"\xa1P\x08\x00@Q\x14\x15\x8b\xc5\xfb\xf7\xef7\x1a\x8d\x00\x80\xc9\xc9\xc9\xf6\xf6\xf6\xce\xceN\x04A\xacV+\x89D"L\xbd&\x16\x86a*\x95\xaa\xbf\xbf\x7fjj\x8aD"\x11\xf1\xbf\xcc\x01@WW\x97B\xa1\xa8\xae\xae\xee\xe8\xe8\x98\x98\x98\x00\x00\\\xbf~}ffF"\x918\x9d\xce\xe5:P\xa9T\x8f\xc7322\x92\x92\x92"\x10\x08\xc0\xf2(ccc\x87\x0e\x1d\x8a\x8a\x8a*--\xad\xa8\xa88\x7f\xfe\xbc\xd7\xeb\x85\x10\xe28>::j0\x18\xd6\xb4\xc5\xcb\x97/\xf9|>\x86a\x10\xc2\xd7\xaf_\x13A\xb3\xd9\x9c\x90\x90`6\x9b\t\xc3\xd9\xed\xf6\xb7o\xdf&&&\x8e\x8e\x8eB\x08{{{\xf9|\xfe\x85\x0b\x17\xe6\xe6\xe6\x88\xfeb\xb1\xb8\xb2\xb22%%evv\xf6o\xde\x02\x00ddddggS\xa9\xd4\xf7\xef\xdf\x97\x95\x95edd\x10\x85 \x96\xc2\xd4\xd4\xd4\x9a\xd9"\xd2\x13\n\x85\x00\x00\x05\x05\x05D\x10E\xd1e\xcfuww_\xbdz5\x10\x080\x18\x0c:\x9d\x0e\x00\xa8\xaa\xaa\x1a\x18\x18\xf8\xfa\xf5kQQ\x11q\xb2\x85\xc3\xe1\xe4\xe4\xe4\x9c\x9c\x9c\xc6\xc6\xc6_\x07G\x89\t\xca\xcb\xcb\x05\x02\x81\xd7\xeb\xed\xe8\xe8\xd0\xe9t\'O\x9e\xac\xae\xae\x9e\x98\x98`\xb3\xd9\xcf\x9f?\xf7\xf9|+\x98"\x91\x88^\xaf\xb7\xdb\xed\x93\x93\x93\x18\x86-\xc7\x17\x16\x16l6\x9bF\xa3\xc10\xec\xf2\xe5\xcb111[\xb7n\xf5x<R\xa9\xd4\xe5r]\xbcx\x91L&\xdf\xbe}\x9bF\xa3\xb9\xddn\x9f\xcf777\x17\x1b\x1b{\xe3\xc6\r\x8dFs\xf6\xecY\xa3\xd1\x88\xe3\xf8_X\x00\x80\xcc\xcc\xcc\xaa\xaa*\x81@0==\x1d\x0c\x06\x0b\x0b\x0b\x1f=z\xa4\xd3\xe98\x1cN~~\xfe\xabW\xafV`---\xe18\xde\xde\xde\xfe\xe9\xd3\'\x87\xc3\xb1\x1c\xb7Z\xad---\x06\x83!\x10\x08tww;\x9dN\x83\xc1p\xe5\xca\x15>\x9fO\xa3\xd1\xf2\xf2\xf2\xa4RiOO\xcf\xcd\x9b7SSS\xb5Z\xed\xf1\xe3\xc7\x11\x04\xf1z\xbd2\x99\x8c\xc9d\x0e\r\r\x11\xcb\x05,\x97\xd3`0\xd4\xd6\xd6\xb2\xd9\xec}\xfb\xf6)\x14\x8a\xf8\xf8\xf8\x92\x92\x12\x85B\x01!\x1c\x19\x19\xf9\xfc\xf9\xf3:\xb7\xa2\r\x11\xf8\xf5E.\x97\x13.\xd9\xbbw/q\xfe\xd4\xd7\xd7C\x08\x03\x81\xc0\xad[\xb7t:\xdd\xa6a\xfdm\xeb+--\xad\xaf\xaf\xaf\xa8\xa8p\xb9\\\xf9\xf9\xf9\x1c\x0e\xc7\xe1p\xd4\xd5\xd5\xa9T\xaa3g\xce\xdc\xbbwO\xa5R\xadi\xff\x8d\xd7\n\xcc\x1f?~\xdc\xbf\x7f\xbf\xac\xac\x8c\xc5bQ(\x94\xf4\xf4t\x1e\x8fWRR\xa2T*M&\xd3\xb9s\xe7:;;\xddn\xf7\xea\xff\xdb\xd8;\xd9J,\x08\xa1\xc7\xe3\x19\x18\x18(//\'\x93\xc9,\x16\x8b\xc7\xe3%$$\x1c<x0\x14\nA\x08\xd5juWW\xd7\x9d;wL&\x13\xd1\xdf`0\x9c8q\xc2b\xb1l \x16yu\xfe\xd8l\xf6\xe1\xc3\x871\x0cs8\x1c\x91Hdzz\xdaf\xb3Y,\x96\x03\x07\x0eH$\x12\xbb\xdd\xce`0L&SOO\x8f\xc7\xe3\x89\x8d\x8d}\xf3\xe6\r\x8a\xa2\x93\x93\x93.\x97\xcbn\xb7GGG\xe38\x9e\x96\x96\xf6\xbb\xf3n=B \x84\xbfks\xbb\xdd\xc3\xc3\xc3\xe3\xe3\xe3\x16\x8bE\xab\xd5\x9aL&\xbb\xdd\x8e Haa\xa1\xdf\xef\xe7\xf1x>\x9fohhH(\x14\xd2h\xb4/_\xbe,--\x01\x00v\xed\xda\xc5\xe5r\xa5R)\x8f\xc7\xfb\x9f`\x11\xf2\xf9|\x8b\x8b\x8bV\xabU\xab\xd5~\xfc\xf8qqq\x91N\xa7{<\x9ep8l4\x1a\xbd^/\x95J\x8d\x8d\x8dMMM\x15\x8b\xc5\x0c\x06c\xcf\x9e=\xf1\xf1\xf1L&\xf3_3\xad\x0b\xebW\x85\xc3a\x0c\xc3\xc2\xe1p \x10\xc00,\x14\nEEEm\xd9\xb2\x85\xc5b\xfd\xa3\xfb\xcc\x06cm\x9a\xfe\x03\xaa\xb8Q\xa3s\xc2\x19$\x00\x00\x00\x00IEND\xaeB`\x82'


def test_thumbnail_jpg(client):
    resp = client.post('/login', json=dict(username='hermione', password='granger'))
    assert resp.status_code == 200

    access_token = resp.json['access_token']

    resp = client.post('/thumbnail',
                       headers={'Authorization': f'Bearer {access_token}'},
                       json=dict(image_url='https://www.fullstackpython.com/img/logos/flask.jpg'))
    assert resp.status_code == 200
    img_data = resp.get_data()
    # with open('image.jpg', 'wb') as f:
    #     f.write(img_data)
    assert img_data == b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x13\x002\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xe9<?\xae\xeb\xda\xe7\x8b5\x9dN\xd2\xe9\xe2\x86)v=\x9f\x93\x94E\x8b\x82\x87q\x04\xb9\xeeT\x1c\x1flW\xa3\xea-t|3x\xf2H \xb9\x16\xd26\xfbg?+\x05$\x15$};W\x9b\xf8\xae;\xbf\x02x\xb6\xe7^H<\xfd\x0fQ!\xe7M\xc5V)x\x0f\x9c\x11\xf7\x97$\x13\xc6\xe1\x8e\xf9\xae\xee\xc7R\xb3\xf1\'\x87Z\xde\xce\xfe3\xf6\x88\x0ci:\xaeC\x026\xeePz\x91\xdcv?\xa8\x06\x17\x83n\x0e\xb7c\xa5\xbc\x9a\xae\xb4n\xdbMI\xae\x84\xa1\x929\x0c\x89\x8c\xa9 r\x1b$\x15\xe0U\x9f\nk\xebc\xf0\xefC\xba\xbe7\xb7\x93\xcblX\x94F\x95\xdfh%\x99\x8f\xd0u\'\x9e\x9dk\xa1\xd0\xb4\xb7\xd1\xfc=k\xa5\xa5\xda\xcem!\x16\xf1\xccc\x00\xe1F\xd1\x90\x0f$c\x9e\x9f\x85r\xcb\xe1\x03o\xa5\xe9Z#jw\xd2Ab\xb2@\xcb\xf6<\xc52\xb8\x18,>\xe9+\xd8\xf3\x8c\x9e(\x03\xa0\x9b\xc5\xdadb\xc7\xca\x17\x17/}m\xf6\xb8c\x82"\xcea\xf9~}\xbd\x7f\x88p2}\xab\x12\xd7ZM#\xc6~$\x8e\xe2[\xcb\x95\x92[E\xb7\xb7M\xd2\xb0-\x1b\x12\x11;/\x198\xe0u5Z\xe7\xc2\xd0\xea\x1a\x06\x99\xa6\xcfwy,\x16p$\x11\xc8\xdap\xf3P\xa9\xc0\x927\x18(\xd8\x00dg8\x1cR\xdexf\xd6\xff\x00]\xbb\xd7#\xbc\xbe\x86\xfaf\x86K[\x88\xecN\xfbs\x1a\x95\x18\'\xef+\x02\xc1\x94\xf0s\xdb\x14\x01\xdf#oEm\xa5w\x00p\xc3\x04}h\xaaq\\8\x85\x04\x97 \xbe\xd1\xb8\xf9\x05r{\xf1\x9e>\x94P\x05\x9b\x9bh/-\xe4\xb7\xb9\x869\xa0\x90mx\xe4P\xca\xc3\xd0\x83^]\xe2\x8f\n\xe8\xfa<\x92&\x9bm%\x9cl\xa6C\x1d\xbd\xc4\x88\x9b\xbdv\x86\xc6}\xf1E\x14\x01\xbf\xf0\xfbE\xb3\xb5\xd3\xa3\xbb\x8f\xed>o?~\xeeW^z\x9d\xac\xc5r}q]s\xe9\xf6\xd2Nfdc!\xeaw\xb7\xa6:f\x8a(\x02\xb2\xe9vi?\x96\xb10C\x11\x04\t\x1b\xa6G\xbdO&\x9bi/\xdf\x88\x9es\xf7\xdb\xfc}\xa8\xa2\x80\x14i\xf6\xaa\x00\x11\x9c\x0e>\xf9\xff\x00\x1a(\xa2\x80?\xff\xd9'
