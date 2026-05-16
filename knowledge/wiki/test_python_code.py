# 测试代码 - 包含一些常见错误


def calculate_average(numbers):
    # 缺少参数验证
    total = 0
    for num in numbers:
        total += num
    average = total / len(numbers)  # 如果numbers为空会除零错误
    return average


def process_data(data):
    # 不安全的文件操作
    with open(data, "r") as f:
        content = f.read()

    # 硬编码的API密钥
    api_key = "sk-1234567890abcdef"  # noqa: F841

    # SQL注入风险
    query = f"SELECT * FROM users WHERE name = '{data}'"  # noqa: F841

    return content


class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, name, email):
        # 缺少输入验证
        user = {"name": name, "email": email}
        self.users.append(user)

    def find_user(self, name):
        # 低效的查找算法
        for user in self.users:
            if user["name"] == name:
                return user
        return None


# 主程序
if __name__ == "__main__":
    # 测试计算平均值
    numbers = [1, 2, 3, 4, 5]
    result = calculate_average(numbers)
    print(f"平均值: {result}")

    # 测试空列表 - 会出错
    try:
        empty_result = calculate_average([])
    except Exception as e:
        print(f"错误: {e}")

    # 创建用户管理器
    manager = UserManager()
    manager.add_user("Alice", "alice@example.com")
    manager.add_user("Bob", "bob@example.com")

    # 查找用户
    user = manager.find_user("Alice")
    print(f"找到用户: {user}")
