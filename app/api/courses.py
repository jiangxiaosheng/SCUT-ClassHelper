from . import api

@api.route('/drop-course', methods=['POST'])
def index():
    print('1')
    return None

