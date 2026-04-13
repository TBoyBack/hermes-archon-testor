# Archon CLI 部署指南

本文档详细说明如何安装和配置 Archon 工作流引擎。

## 目录

- [概述](#概述)
- [安装](#安装)
- [配置](#配置)
- [使用](#使用)
- [工作流](#工作流)
- [故障排查](#故障排查)

---

## 概述

Archon 是一个 AI 编程工作流引擎，用于编排和执行复杂的测试任务。它与 Hermes Agent 配合使用，Hermes 负责理解层（AI 分析），Archon 负责执行层（工作流编排）。

### 核心功能

- YAML 工作流定义
- 步骤编排与依赖管理
- 人工评审节点
- 并行/串行执行支持
- 错误处理与重试
- 通知与 webhook 集成

---

## 安装

### 方式一：自动安装（推荐）

```bash
# 下载安装脚本
curl -O https://raw.githubusercontent.com/TBoyBack/hermes-archon-testor/main/deploy/archon/install.sh

# 添加执行权限
chmod +x install.sh

# 运行安装
./install.sh

# 激活虚拟环境
source ~/.archon/venv/bin/activate

# 验证安装
archon --version
```

### 方式二：手动安装

```bash
# 1. 创建安装目录
mkdir -p ~/.archon
cd ~/.archon

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install archon-cli pyyaml jinja2 loguru

# 4. 创建符号链接
ln -sf ~/.archon/venv/bin/archon ~/.archon/bin/archon
export PATH="$HOME/.archon/bin:$PATH"
```

### 方式三：Docker 部署

```bash
# 使用 Docker 运行 Archon
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  archon/archon:latest archon --help
```

---

## 配置

### 配置文件位置

- 默认位置: `~/.archon/config.yaml`
- 项目级配置: `./.archon/config.yaml`

### 完整配置示例

```yaml
# Archon CLI 配置文件
version: "1.0.0"

# 安装路径
install_dir: "/root/.archon"

# 缓存配置
cache:
  enabled: true
  dir: "~/.archon/cache"
  max_size: "1GB"
  ttl: 86400

# 日志配置
logging:
  level: INFO
  dir: "~/.archon/logs"
  max_size: "100MB"
  backup_count: 5

# 默认工作流目录
workflows_dir: "./.archon/workflows"

# 技能模块目录
skills_dir: "./.archon/skills"

# Hermes 连接配置
hermes:
  host: localhost
  port: 8080
  timeout: 30
  api_key: ${HERMES_API_KEY}

# 执行器配置
executor:
  max_parallel: 4
  default_timeout: 300
  retry_count: 3
```

### 环境变量

| 变量名 | 说明 |
|--------|------|
| ARCHON_HOME | Archon 安装目录 |
| ARCHON_CONFIG | 配置文件路径 |
| HERMES_API_KEY | Hermes API 密钥 |
| HERMES_HOST | Hermes 服务地址 |
| HERMES_PORT | Hermes 服务端口 |

---

## 使用

### 基本命令

```bash
# 查看帮助
archon --help

# 查看版本
archon --version

# 列出所有工作流
archon workflow list

# 查看工作流详情
archon workflow show test-case-generation

# 运行工作流
archon workflow run test-case-generation

# 带参数运行
archon workflow run test-case-generation \
  --param module_name="登录模块" \
  --param test_type="功能测试"

# 验证工作流语法
archon workflow validate test-case-generation.yaml
```

### 工作流管理

```bash
# 创建新工作流
archon workflow create my-workflow

# 导出工作流
archon workflow export test-case-generation -o ./my-workflows/

# 导入工作流
archon workflow import ./my-workflows/

# 删除工作流
archon workflow delete my-workflow
```

### 执行管理

```bash
# 查看运行历史
archon run history

# 查看运行详情
archon run show <run-id>

# 取消运行
archon run cancel <run-id>

# 重新运行
archon run rerun <run-id>
```

---

## 工作流

### 工作流文件结构

```yaml
name: workflow-name           # 工作流名称
version: "1.0.0"              # 版本号
description: "工作流描述"      # 描述

trigger:
  type: manual                 # manual | webhook | schedule

inputs:                        # 输入参数
  - name: param_name
    type: string
    required: true

steps:                         # 执行步骤
  - name: step-1
    type: hermes.analyze
    inputs:
      data: "{{ inputs.param_name }}"
    outputs:
      - result
    depends_on: []            # 依赖步骤

outputs:                      # 输出定义
  - name: result
    value: "{{ steps.step-1.result }}"

error_handling:               # 错误处理
  default: log_and_continue

notifications:                # 通知配置
  on_complete:
    - type: log
```

### 步骤类型

| 类型 | 说明 | 示例 |
|------|------|------|
| hermes.* | Hermes Agent 操作 | hermes.analyze, hermes.generate |
| approval | 人工评审节点 | 等待人工确认 |
| output | 输出结果 | 导出文件 |
| webhook | 发送 webhook | 通知外部系统 |
| script | 执行脚本 | 运行自定义脚本 |
| condition | 条件判断 | if/else 分支 |

### 内置变量

| 变量 | 说明 |
|------|------|
| `{{ inputs.* }}` | 输入参数 |
| `{{ steps.*.* }}` | 步骤输出 |
| `{{ outputs.* }}` | 工作流输出 |
| `{{ timestamp }}` | 当前时间戳 |
| `{{ run_id }}` | 运行 ID |

---

## 故障排查

### 常见问题

#### 1. 安装失败

```bash
# 检查 Python 版本
python3 --version  # 需要 3.8+

# 检查 pip
pip3 --version

# 重新安装
pip3 install --force-reinstall archon-cli
```

#### 2. 命令未找到

```bash
# 添加到 PATH
export PATH="$HOME/.archon/bin:$PATH"

# 或激活虚拟环境
source ~/.archon/venv/bin/activate
```

#### 3. 工作流执行失败

```bash
# 验证工作流语法
archon workflow validate your-workflow.yaml

# 查看详细日志
archon run show <run-id> --verbose

# 检查 Hermes 连接
curl http://localhost:8080/health
```

### 日志位置

- 运行日志: `~/.archon/logs/`
- 执行日志: `~/.archon/logs/runs/`

---

## 相关文档

- [Archon 项目主页](https://github.com/ajlabek/archon)
- [Hermes 部署文档](./hermes.md)
- [示例工作流](../.archon/workflows/example.yaml)

---

*最后更新: 2026-04-13*
