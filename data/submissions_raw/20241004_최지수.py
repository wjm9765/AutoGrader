# 오탈자가 있는 코드

for i in range(1, 6):
    spaces = " " * (5 - i)
    stars = "*" * (2 * i - 1)
    # 변수명 오타: stars -> star
    print(spaces + star)
