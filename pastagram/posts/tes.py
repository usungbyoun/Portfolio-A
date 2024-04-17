
a = '       '

# if a.strip() == '':
#     print('폼 필드에 공백만 입력되었습니다.', a)
# else:
#     print('폼 필드에 입력된 값이 있습니다.', a.strip())

if len(a.strip()) > 0:
    print('폼 필드에 입력된 값이 있습니다.', len(a.strip()))
else:
    print('폼 필드에 입력된 값이 없습니다.', len(a.strip()))