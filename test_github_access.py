#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub网站访问测试脚本
测试两个网站是否可以从GitHub Actions环境访问
"""

import requests
import json
import time
from datetime import datetime
import sys

print("=" * 60)
print("GitHub网站访问测试 - 开始")
print("=" * 60)

# 要测试的两个网站
test_sites = [
    {
        "name": "图标数据源",
        "url": "https://epg.51zmt.top:8001",
        "type": "icons"
    },
    {
        "name": "频道列表源", 
        "url": "https://epg.51zmt.top:8001/sctvmulticast.html",
        "type": "channels"
    }
]

# 获取GitHub Runner的IP地址
print("\n📡 获取GitHub Runner网络信息...")
try:
    ip_response = requests.get("https://api.ipify.org?format=json", timeout=10)
    github_ip = ip_response.json()["ip"]
    print(f"✅ GitHub Runner公网IP: {github_ip}")
except Exception as e:
    print(f"⚠️  无法获取IP地址: {e}")
    github_ip = "未知"

print(f"\n📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🐍 Python版本: {sys.version.split()[0]}")

# 测试结果存储
all_results = []

print("\n" + "=" * 60)
print("开始测试网站访问性")
print("=" * 60)

# 测试每个网站
for site in test_sites:
    print(f"\n🔍 测试: {site['name']}")
    print(f"   URL: {site['url']}")
    
    try:
        start_time = time.time()
        
        # 发送请求（忽略证书验证，与你的脚本一致）
        response = requests.get(
            site['url'], 
            verify=False,  # 忽略证书验证
            timeout=30,    # 30秒超时
            headers={
                'User-Agent': 'Mozilla/5.0 (GitHub-Actions-Tester)'
            }
        )
        
        response_time = time.time() - start_time
        status_code = response.status_code
        content_size = len(response.content)
        
        print(f"   ✅ 请求成功")
        print(f"      状态码: {status_code}")
        print(f"      响应时间: {response_time:.2f}秒")
        print(f"      内容大小: {content_size}字节")
        
        # 尝试解析内容
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if site['type'] == 'icons':
                # 查找图标链接
                icon_links = []
                for a in soup.find_all('a', href=True):
                    if a['href'].endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico')):
                        icon_links.append(a['href'])
                
                found_count = len(icon_links)
                print(f"      找到图标链接: {found_count}个")
                if found_count > 0:
                    print(f"      示例图标: {icon_links[0][:50]}...")
                
            elif site['type'] == 'channels':
                # 查找频道表格
                table_rows = soup.find_all('tr')
                channel_count = 0
                
                for tr in table_rows:
                    tds = tr.find_all('td')
                    if len(tds) >= 3 and tds[0].text.strip().isdigit():
                        channel_count += 1
                
                print(f"      找到频道数据行: {channel_count}行")
                
        except ImportError:
            print("      警告: 未安装BeautifulSoup，跳过内容解析")
        except Exception as e:
            print(f"      内容解析失败: {str(e)[:50]}")
        
        # 保存成功结果
        result = {
            "site": site['name'],
            "url": site['url'],
            "accessible": True,
            "status_code": status_code,
            "response_time": response_time,
            "content_size": content_size
        }
        
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时 (30秒)")
        result = {
            "site": site['name'],
            "url": site['url'],
            "accessible": False,
            "error": "请求超时"
        }
        
    except requests.exceptions.ConnectionError:
        print("   ❌ 连接错误")
        result = {
            "site": site['name'],
            "url": site['url'],
            "accessible": False,
            "error": "连接错误"
        }
        
    except Exception as e:
        print(f"   ❌ 请求失败: {str(e)[:50]}")
        result = {
            "site": site['name'],
            "url": site['url'], 
            "accessible": False,
            "error": str(e)
        }
    
    all_results.append(result)
    time.sleep(1)  # 等待1秒再测试下一个网站

print("\n" + "=" * 60)
print("测试结果总结")
print("=" * 60)

# 统计结果
successful_sites = [r for r in all_results if r['accessible']]
failed_sites = [r for r in all_results if not r['accessible']]

print(f"\n📊 统计:")
print(f"   总测试网站: {len(all_results)} 个")
print(f"   成功访问: {len(successful_sites)} 个")
print(f"   访问失败: {len(failed_sites)} 个")

# 显示每个网站的最终状态
print(f"\n📋 详细结果:")
for result in all_results:
    if result['accessible']:
        print(f"   ✅ {result['site']}: 成功 (状态码: {result['status_code']}, 时间: {result['response_time']:.2f}秒)")
    else:
        print(f"   ❌ {result['site']}: 失败 - {result.get('error', '未知错误')}")

# 生成JSON报告
report = {
    "test_info": {
        "timestamp": datetime.now().isoformat(),
        "github_runner_ip": github_ip,
        "python_version": sys.version.split()[0]
    },
    "test_sites": [
        {
            "name": "图标数据源",
            "url": "https://epg.51zmt.top:8001",
            "description": "IPTV图标数据源"
        },
        {
            "name": "频道列表源",
            "url": "https://epg.51zmt.top:8001/sctvmulticast.html",
            "description": "成都电信IPTV频道列表"
        }
    ],
    "results": all_results,
    "summary": {
        "total_tested": len(all_results),
        "successful": len(successful_sites),
        "failed": len(failed_sites),
        "all_accessible": len(successful_sites) == len(all_results)
    }
}

# 保存报告到文件
with open("github_access_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n📄 详细报告已保存到: github_access_report.json")

# 最终判断
if len(successful_sites) == len(all_results):
    print("\n🎉 结论: 两个网站都可以从GitHub环境访问！")
    sys.exit(0)  # 成功退出
else:
    print(f"\n⚠️  结论: {len(failed_sites)} 个网站无法从GitHub环境访问")
    sys.exit(1)  # 失败退出