def json_to_markdown(data, indent_level=0):
    indent = "    " * indent_level  # 当前缩进

    # 处理字典类型
    if isinstance(data, dict):
        if not data:
            return f"{indent}- {{}}"

        lines = []
        for key, value in data.items():
            # 键名加粗显示
            header = f"{indent}- **{key}**:"

            # 处理嵌套结构
            if isinstance(value, (dict, list)):
                lines.append(header)
                lines.append(json_to_markdown(value, indent_level + 1))
            # 处理空值
            elif value is None:
                lines.append(f"{header} `null`")
            # 处理布尔值
            elif isinstance(value, bool):
                lines.append(f"{header} {'`true`' if value else '`false`'}")
            # 处理基本类型
            else:
                lines.append(f"{header} {value}")

        return "\n".join(lines)
