#!/bin/bash
# Archon CLI 安装脚本
# 用于在不同操作系统上安装和配置 Archon 工作流引擎

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 版本配置
ARCHON_VERSION="1.0.0"
ARCHON_INSTALL_DIR="${HOME}/.archon"
ARCHON_BIN_DIR="${ARCHON_INSTALL_DIR}/bin"
ARCHON_CACHE_DIR="${ARCHON_INSTALL_DIR}/cache"

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# 检测架构
detect_arch() {
    local arch=$(uname -m)
    case $arch in
        x86_64|amd64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l)
            echo "arm"
            ;;
        *)
            print_error "Unsupported architecture: $arch"
            exit 1
            ;;
    esac
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    local missing_deps=()
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("python3-pip")
    fi
    
    # 检查 Docker (可选)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker 未安装，部分功能可能不可用"
    fi
    
    # 安装缺失的依赖
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_info "安装缺失的依赖..."
        local os=$(detect_os)
        
        case $os in
            debian|ubuntu)
                sudo apt-get update
                sudo apt-get install -y ${missing_deps[@]}
                ;;
            redhat|centos)
                sudo yum install -y ${missing_deps[@]}
                ;;
            macos)
                if command -v brew &> /dev/null; then
                    brew install ${missing_deps[@]}
                else
                    print_error "请先安装 Homebrew: https://brew.sh"
                    exit 1
                fi
                ;;
        esac
    fi
    
    print_success "依赖检查完成"
}

# 创建安装目录
create_directories() {
    print_info "创建安装目录..."
    
    mkdir -p "${ARCHON_BIN_DIR}"
    mkdir -p "${ARCHON_CACHE_DIR}"
    mkdir -p "${ARCHON_INSTALL_DIR}/workflows"
    mkdir -p "${ARCHON_INSTALL_DIR}/skills"
    mkdir -p "${ARCHON_INSTALL_DIR}/logs"
    
    print_success "安装目录创建完成: ${ARCHON_INSTALL_DIR}"
}

# 下载 Archon
download_archon() {
    print_info "下载 Archon CLI..."
    
    local os=$(detect_os)
    local arch=$(detect_arch)
    local archon_filename="archon-${ARCHON_VERSION}-${os}-${arch}"
    local download_url="https://github.com/ajlabek/archon/releases/download/v${ARCHON_VERSION}/${archon_filename}"
    
    # 如果下载链接不可用，创建 Python 版本的 Archon
    print_info "安装 Python 版本的 Archon..."
    
    # 创建虚拟环境
    python3 -m venv "${ARCHON_INSTALL_DIR}/venv"
    
    # 安装 Archon
    source "${ARCHON_INSTALL_DIR}/venv/bin/activate"
    pip install --upgrade pip
    pip install archon-cli pyyaml jinja2 loguru
    
    print_success "Archon CLI 安装完成"
}

# 创建符号链接
create_symlinks() {
    print_info "创建符号链接..."
    
    local archon_bin="${ARCHON_INSTALL_DIR}/venv/bin/archon"
    
    # 创建主命令链接
    if [ -L "${ARCHON_BIN_DIR}/archon" ]; then
        rm "${ARCHON_BIN_DIR}/archon"
    fi
    ln -sf "${archon_bin}" "${ARCHON_BIN_DIR}/archon"
    
    # 添加到 PATH (如果需要)
    local shell_rc=""
    case $(basename $SHELL) in
        bash)
            shell_rc="${HOME}/.bashrc"
            ;;
        zsh)
            shell_rc="${HOME}/.zshrc"
            ;;
        fish)
            shell_rc="${HOME}/.config/fish/config.fish"
            ;;
    esac
    
    # 检查是否已添加
    if ! grep -q "${ARCHON_BIN_DIR}" "${shell_rc}" 2>/dev/null; then
        echo "" >> "${shell_rc}"
        echo "# Archon CLI" >> "${shell_rc}"
        echo "export PATH=\"${ARCHON_BIN_DIR}:\$PATH\"" >> "${shell_rc}"
        print_info "已添加 ${ARCHON_BIN_DIR} 到 PATH"
    fi
    
    print_success "符号链接创建完成"
}

# 初始化配置
init_config() {
    print_info "初始化配置文件..."
    
    local config_file="${ARCHON_INSTALL_DIR}/config.yaml"
    
    cat > "${config_file}" << EOF
# Archon CLI 配置文件
version: "${ARCHON_VERSION}"

# 安装路径
install_dir: "${ARCHON_INSTALL_DIR}"

# 缓存配置
cache:
  enabled: true
  dir: "${ARCHON_CACHE_DIR}"
  max_size: "1GB"
  ttl: 86400  # 24小时

# 日志配置
logging:
  level: INFO
  dir: "${ARCHON_INSTALL_DIR}/logs"
  max_size: "100MB"
  backup_count: 5

# 默认工作流目录
workflows_dir: "${ARCHON_INSTALL_DIR}/workflows"

# 技能模块目录
skills_dir: "${ARCHON_INSTALL_DIR}/skills"

# Herms 连接配置
hermes:
  host: localhost
  port: 8080
  timeout: 30

# 执行器配置
executor:
  max_parallel: 4
  default_timeout: 300
  retry_count: 3
EOF
    
    print_success "配置文件创建完成: ${config_file}"
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    source "${ARCHON_INSTALL_DIR}/venv/bin/activate"
    
    if command -v archon &> /dev/null; then
        print_success "Archon CLI 安装验证成功!"
        archon --version
    elif "${ARCHON_INSTALL_DIR}/venv/bin/archon" --version &> /dev/null; then
        print_success "Archon CLI 安装验证成功!"
        "${ARCHON_INSTALL_DIR}/venv/bin/archon" --version
    else
        print_warning "请手动验证: source ${ARCHON_INSTALL_DIR}/venv/bin/activate"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "=============================================="
    echo "         Archon CLI 安装完成!"
    echo "=============================================="
    echo ""
    echo "使用方法:"
    echo "  1. 激活虚拟环境:"
    echo "     source ${ARCHON_INSTALL_DIR}/venv/bin/activate"
    echo ""
    echo "  2. 或直接使用完整路径:"
    echo "     ${ARCHON_INSTALL_DIR}/venv/bin/archon <command>"
    echo ""
    echo "  3. 常用命令:"
    echo "     archon --help              # 显示帮助"
    echo "     archon workflow list       # 列出工作流"
    echo "     archon workflow run <name> # 运行工作流"
    echo "     archon skills list        # 列出技能"
    echo ""
    echo "  配置文件: ${ARCHON_INSTALL_DIR}/config.yaml"
    echo ""
    echo "=============================================="
}

# 主安装流程
main() {
    echo ""
    echo "=============================================="
    echo "         Archon CLI 安装脚本"
    echo "         Version: ${ARCHON_VERSION}"
    echo "=============================================="
    echo ""
    
    print_info "检测操作系统: $(detect_os)"
    print_info "检测架构: $(detect_arch)"
    print_info "安装目录: ${ARCHON_INSTALL_DIR}"
    echo ""
    
    check_dependencies
    create_directories
    download_archon
    create_symlinks
    init_config
    verify_installation
    show_usage
}

# 卸载函数
uninstall() {
    print_warning "确定要卸载 Archon CLI 吗? (y/N)"
    read -r confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        print_info "开始卸载..."
        rm -rf "${ARCHON_INSTALL_DIR}"
        print_success "Archon CLI 已卸载"
    else
        print_info "取消卸载"
    fi
}

# 解析参数
case "${1:-install}" in
    install)
        main
        ;;
    uninstall)
        uninstall
        ;;
    update)
        print_info "更新 Archon CLI..."
        source "${ARCHON_INSTALL_DIR}/venv/bin/activate"
        pip install --upgrade archon-cli
        print_success "更新完成"
        ;;
    *)
        echo "Usage: $0 {install|uninstall|update}"
        exit 1
        ;;
esac
