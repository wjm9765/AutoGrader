# 별 찍기 과제
# 높이 5인 피라미드 출력

for i in range(1, 6):
    # 공백 계산: 5 - i
    spaces = " " * (5 - i)
    # 별 계산: 2 * i - 1
    stars = "*" * (2 * i - 1)
    print(spaces + stars)
