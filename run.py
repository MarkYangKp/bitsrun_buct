"""
BitSRun_BUCT - 深澜校园网自动认证工具 - 北京化工大学特供版自动认证工具入口脚本

用法:
    python run.py [options]

选项:
    -h, --help          显示此帮助信息
    -c, --config FILE   指定配置文件路径
    -u, --username USER 指定用户名 (覆盖配置文件)
    -p, --password PASS 指定密码 (覆盖配置文件)
    -t, --type TYPE     指定运营商类型
    --server URL        指定认证服务器地址
    -v, --verbose       显示详细日志
    -q, --quiet         仅显示错误信息
    -g, --guard         启用认证守卫模式
    -i, --interval SECS 守卫模式检查间隔(秒)
"""

import sys
import os
import argparse
import logging
import configparser
from bitsrun_buct import BitSRun, setup_logging

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='深澜校园网自动认证工具 - 北京化工大学特供版')
    
    parser.add_argument('-c', '--config', default='config.ini',
                        help='指定配置文件路径 (默认: config.ini)')
    
    parser.add_argument('-u', '--username', help='指定用户名 (覆盖配置文件)')
    parser.add_argument('-p', '--password', help='指定密码 (覆盖配置文件)')
    parser.add_argument('-t', '--type', help='指定运营商类型 (如: cmcc, unicom)')
    
    parser.add_argument('--server', help='指定认证服务器地址')
    
    # 守卫模式
    parser.add_argument('-g', '--guard', action='store_true',
                      help='启用认证守卫模式，定期检查登录状态')
    parser.add_argument('-i', '--interval', type=int, default=300,
                      help='守卫模式检查间隔(秒), 默认为300秒')
    
    # 日志级别
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument('-v', '--verbose', action='store_true',
                         help='显示详细日志')
    log_group.add_argument('-q', '--quiet', action='store_true',
                         help='仅显示错误信息')
    
    return parser.parse_args()

def load_config(config_path):
    """加载配置文件"""
    config = configparser.ConfigParser()
    
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        if os.path.exists('config.example.ini'):
            print(f"错误: 配置文件 '{config_path}' 不存在。请复制 config.example.ini 并进行配置。")
            sys.exit(1)
        else:
            print(f"错误: 配置文件 '{config_path}' 不存在且未找到配置模板。")
            sys.exit(1)
            
    config.read(config_path, encoding='utf-8')
    return config

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    
    # 配置日志
    setup_logging(log_level)
    logger = logging.getLogger('bitsrun')
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 创建登录客户端
        client = BitSRun(config)
        
        # 覆盖命令行参数指定的选项
        if args.username:
            client.username = args.username
        if args.password:
            client.password = args.password
        if args.type:
            client.user_type = args.type
        if args.server:
            client.server_url = args.server
        
        # 执行登录流程
        if args.guard:
            logger.info(f"启动认证守卫模式，检查间隔：{args.interval}秒")
            client.guard(interval_seconds=args.interval)
        else:
            client.run()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=args.verbose)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
