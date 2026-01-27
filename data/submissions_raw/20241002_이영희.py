def draw_star_tree(height):
    for i in range(height):
        # i는 0부터 4까지
        # 공백: height - 1 - i
        # 별: 2 * i + 1
        print(" " * (height - 1 - i) + "*" * (2 * i + 1))

if __name__ == "__main__":
    draw_star_tree(5)

