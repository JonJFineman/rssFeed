import sys
import re



subjects = [
        'Is Hiring', \
        '3D'
        ]

bodies = [
        'xx', \
        'yy'
        ]



def rejectSubject(feed, subject):
    byPass = False
    email = ''

    for s in subjects:
        if s in subject:
            byPass = True

    return byPass



def rejectBody(feed, body):
    byPass = False
    email = ''

    for b in bodies:
        if b in body:
            byPass = True

    return byPass



def main(argv):

    print('starting')

    rc = rejectSubject('hn', 'Tesorio (YC S15) Is Hiring Senior Software Engineers (Web and ML)')
    print('hiring rc=',rc)

    rc  = rejectSubject('hn', '3D Printers')
    print('3d rc=',rc)

    rc  = rejectSubject('hn', 'Printers')
    print('printer rc=',rc)

    rc  = rejectBody('hn', 'xx')
    print('xx rc=',rc)

    print('stopping')



if __name__ == "__main__":
    main(sys.argv)
