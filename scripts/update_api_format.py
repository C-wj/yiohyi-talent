#!/usr/bin/env python3
"""
更新API格式脚本
将所有API路由函数更新为使用api_response装饰器，确保统一的返回格式
"""
import os
import re
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 需要处理的API目录
API_DIRS = [
    "app/api/v1",
    "app/routers"
]

# 导入部分模式匹配
IMPORT_PATTERN = re.compile(r"from\s+app\.core\.response\s+import\s+[^;\n]+")
DECORATOR_IMPORT_PATTERN = re.compile(r"from\s+app\.core\.decorators\s+import\s+[^;\n]+")

# 路由函数模式匹配
ROUTE_PATTERN = re.compile(r"@router\.[a-z]+\([^)]*\)(\s*@[^@\n]+)*\s*async\s+def\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*:")

# 需要添加的导入语句
DECORATOR_IMPORT = "from app.core.decorators import api_response"

# 统计信息
stats = {
    "files_processed": 0,
    "functions_updated": 0,
    "errors": 0
}

def update_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已导入装饰器
        has_decorator_import = bool(DECORATOR_IMPORT_PATTERN.search(content))
        
        # 查找所有路由函数
        matches = list(ROUTE_PATTERN.finditer(content))
        
        if not matches:
            print(f"  没有发现路由函数: {file_path}")
            return 0
        
        # 添加导入语句（如果需要）
        if not has_decorator_import:
            # 查找已有的导入语句
            imports = IMPORT_PATTERN.search(content)
            if imports:
                # 在已有的导入语句后添加
                content = content.replace(
                    imports.group(0),
                    f"{imports.group(0)}\n{DECORATOR_IMPORT}"
                )
            else:
                # 在文件顶部添加
                content = f"{DECORATOR_IMPORT}\n\n{content}"
        
        # 修改路由函数，添加装饰器
        updated_count = 0
        for match in matches:
            # 检查该函数是否已有装饰器
            if "@api_response" not in match.group(0):
                # 添加装饰器
                replacement = match.group(0).replace(
                    f"@router.",
                    f"@router."
                ).replace(
                    f")",
                    f")\n@api_response"
                )
                content = content.replace(match.group(0), replacement)
                updated_count += 1
        
        # 仅当有更改时才写入文件
        if updated_count > 0 or not has_decorator_import:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  更新了 {updated_count} 个函数: {file_path}")
            stats["functions_updated"] += updated_count
        else:
            print(f"  无需更新: {file_path}")
        
        return updated_count
    
    except Exception as e:
        print(f"  处理文件时出错: {file_path} - {str(e)}")
        stats["errors"] += 1
        return 0

def main():
    print("开始更新API返回格式...")
    
    for api_dir in API_DIRS:
        dir_path = os.path.join(project_root, api_dir)
        if not os.path.exists(dir_path):
            print(f"目录不存在: {dir_path}")
            continue
        
        print(f"处理目录: {dir_path}")
        
        # 遍历目录下的所有.py文件
        for root, _, files in os.walk(dir_path):
            for filename in files:
                if filename.endswith('.py') and filename != '__init__.py':
                    file_path = os.path.join(root, filename)
                    update_file(file_path)
                    stats["files_processed"] += 1
    
    print("\n完成!")
    print(f"处理了 {stats['files_processed']} 个文件")
    print(f"更新了 {stats['functions_updated']} 个函数")
    print(f"发生了 {stats['errors']} 个错误")

if __name__ == "__main__":
    main() 