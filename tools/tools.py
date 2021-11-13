import random

def generate_random_code():
    ETALON = list('qwertyuiopadfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZZXCVBNM')
    random.shuffle(ETALON)
    return ''.join(ETALON[:10])

def generate_unique_code(db_sess, table):
    code = generate_random_code()
    while not (db_sess.query(table).filter(table.code == code).first() is None):
        code = generate_random_code()
    return code