# BitSRun_BUCT - 深澜校园网自动认证工具 - 北京化工大学特供版

BitSRun_BUCT 是一个北京化工大学特供版的用于自动完成深澜(srun)认证系统校园网登录的Python工具，支持多种设备平台。

## 功能特点

- 自动获取IP地址并完成认证过程
- 支持检查在线状态
- 适用于不同运营商网络
- 跨平台支持 (Windows, Linux, macOS, ESP32等)
- 配置灵活，使用方便

## 安装方法

### 基本要求
- Python 3.6 及以上版本

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置文件
首次使用前，请复制配置模板并填写个人信息：

```bash
cp config.example.ini config.ini
```

然后编辑 `config.ini` 文件，填入您的校园网账号和密码。

## 使用方法

### 命令行运行
```bash
python run.py
```

### 参数说明
- `-c, --config`: 指定配置文件路径 (默认: config.ini)
- `-u, --username`: 指定用户名 (将覆盖配置文件)
- `-p, --password`: 指定密码 (将覆盖配置文件)
- `-t, --type`: 指定运营商类型 (如: cmcc, unicom)
- `--server`: 指定认证服务器地址
- `-v, --verbose`: 显示详细日志
- `-q, --quiet`: 仅显示错误信息

### 示例
```bash
# 使用默认配置运行
python run.py

# 指定用户名和密码
python run.py -u student123 -p password123

# 使用移动运营商网络
python run.py -t cmcc

# 使用自定义配置文件
python run.py -c my_config.ini
```

## 服务自动化

### Windows计划任务
可通过Windows任务计划程序设置定时运行，确保网络保持连接。

### Linux Cron任务
在Linux系统上，可以添加cron任务实现自动运行：

```bash
# 每小时检查并登录
0 * * * * cd /path/to/bitsrun_buct && python run.py
```

## 故障排除

1. **无法获取IP地址**
   - 检查网络连接
   - 确认认证服务器地址是否正确

2. **认证失败**
   - 确认账号密码正确
   - 检查是否需要指定正确的运营商类型

3. **日志显示JSON解析错误**
   - 可能是认证服务器响应格式改变
   - 尝试使用`--verbose`参数获取详细信息

## 开发相关

### 项目结构
```
bitsrun_buct/
├── run.py                 # 主入口脚本
├── bitsrun_buct.py             # 核心功能模块
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── base64_utils.py    # Base64编码工具
│   ├── xencoding.py       # 加密编码工具
├── config.ini             # 用户配置
├── config.example.ini     # 配置模板
├── README.md              # 项目文档
└── requirements.txt       # 依赖列表
```

### 扩展开发
如需添加新功能或适配其他认证系统，请参考`bitsrun.py`中的注释说明。

## 许可证

MIT License

