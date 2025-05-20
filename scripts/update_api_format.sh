#!/bin/bash
# 更新API格式脚本

# 设置工作目录为项目根目录
cd "$(dirname "$0")/.."
CURRENT_DIR=$(pwd)
echo "当前工作目录: $CURRENT_DIR"

# 确保激活了虚拟环境
if [ -d "venv" ]; then
    echo "发现venv虚拟环境，激活中..."
    source venv/bin/activate
else
    echo "没有找到虚拟环境，请确保已安装所有依赖"
fi

# 执行更新API格式的Python脚本
echo "开始更新API格式..."
python scripts/update_api_format.py

# 执行API格式测试
echo "测试API格式..."
pytest tests/api/test_standard_format.py -v

echo "更新完成！" 