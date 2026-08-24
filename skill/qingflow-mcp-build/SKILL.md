---
name: qingflow-mcp-build
description: Build cross-platform binaries for the Qingflow MCP server. Supports macOS (arm64/x64/universal), Linux (x64/arm64), and Windows. Use when the user wants to build standalone executables for distribution or when they need platform-specific binaries.
metadata:
  short-description: Build cross-platform MCP server binaries
---

# Qingflow MCP Cross-Platform Build

## Overview

This skill builds standalone, single-file executables of the Qingflow MCP server for different platforms. The resulting binaries can run without Python installation and can be directly used as MCP servers in Claude Desktop, Cursor, or other MCP clients.

## Supported Platforms

| Platform | Architecture | Build Method | Output Size |
|----------|--------------|--------------|-------------|
| macOS | Apple Silicon (arm64) | Native | ~23 MB |
| macOS | Intel (x86_64) | Native | ~23 MB |
| macOS | Universal (both) | Native (lipo) | ~46 MB |
| Linux | x86_64 | Docker or Native | ~25 MB |
| Linux | ARM64 | Docker or Native | ~25 MB |
| Windows | x86_64 | CI/CD or Docker (limited) | ~25 MB |

## When to Use

Use this skill when:
- User asks to "build a binary" or "create an executable"
- User needs a Windows/macOS/Linux version of the MCP server
- User wants to distribute the MCP server without Python dependencies
- User needs a Universal Binary for macOS

## Prerequisites

- Python 3.11+ (for native builds)
- Docker (optional, for Linux builds on macOS)
- macOS with Xcode Command Line Tools (for macOS Universal builds)

## Workflow

### Step 1: Locate the MCP server project

The MCP server source code lives at:

```
<repo_root>/qingflow-support/mcp-server/
```

Key files:
- `entry_point.py` - Entry point for PyInstaller
- `src/qingflow_mcp/` - Source code
- `scripts/build_binary.sh` - Build script

### Step 2: Determine target platform

Check current platform and user requirements:

```bash
# Detect current platform
uname -s  # Darwin (macOS), Linux, MINGW/MSYS (Windows)
uname -m  # arm64, x86_64
```

Common scenarios:
- **"Build for Windows"** → Use CI/CD (GitHub Actions) or Docker if available
- **"Build for macOS"** → Build native on Mac
- **"Build Universal Binary"** → Requires macOS + lipo
- **"Build for Linux"** → Use Docker on macOS, native on Linux

### Step 3: Run the build

Navigate to the MCP server directory:

```bash
cd <repo_root>/qingflow-support/mcp-server
```

#### Scenario A: Build for current platform (native)

```bash
./scripts/build_binary.sh
```

Output: `dist/binary/<platform>/qingflow-mcp`

#### Scenario B: Build macOS Universal Binary

```bash
./scripts/build_binary.sh --universal
```

Output: `dist/binary/macos-universal/qingflow-mcp` (works on both Intel and Apple Silicon)

**Requirements:** Must run on macOS. Uses `lipo` to combine arm64 and x64 binaries.

#### Scenario C: Build for Linux (on macOS)

```bash
./scripts/build_binary.sh --target linux
# or
./scripts/build_binary.sh --target linux-arm64
```

**Requirements:** Docker must be installed and running.

#### Scenario D: Build all platforms

```bash
./scripts/build_binary.sh --all
```

Builds:
- macOS Universal (if on macOS)
- Linux x64 and ARM64 (if Docker available)
- Windows instructions (manual/CI required)

### Step 4: Verify the build

Check the binary was created:

```bash
ls -lh dist/binary/*/qingflow-mcp
```

Verify architecture (macOS/Linux):

```bash
file dist/binary/macos-arm64/qingflow-mcp
dist/binary/macos-arm64/qingflow-mcp: Mach-O 64-bit executable arm64
```

Test execution (should start and wait for MCP input):

```bash
timeout 5 ./dist/binary/macos-arm64/qingflow-mcp || true
```

### Step 5: Provide usage instructions

Give the user the binary path and configuration example:

**推荐配置方式（使用环境变量）：**

这种方式无需额外的配置文件，直接在 Cursor/Claude 的 MCP 配置中设置：

```json
{
  "mcpServers": {
    "qingflow": {
      "command": "/absolute/path/to/qingflow-mcp",
      "env": {
        "QINGFLOW_MCP_DEFAULT_BASE_URL": "https://qingflow.com/api",
        "QINGFLOW_MCP_HOME": "/absolute/path/to/.qingflow-mcp"
      }
    }
  }
}
```

**环境变量说明：**

| 环境变量 | 说明 | 示例 |
|----------|------|------|
| `QINGFLOW_MCP_DEFAULT_BASE_URL` | Qingflow API 基础地址 | `https://qingflow.com/api` |
| `QINGFLOW_MCP_HOME` | MCP 数据存储目录（存放登录凭证等） | `~/.qingflow-mcp` |
| `QINGFLOW_MCP_TIMEOUT_SECONDS` | HTTP 请求超时时间（秒） | `30` |
| `QINGFLOW_MCP_LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） | `INFO` |
| `QINGFLOW_MCP_CONFIG_PATH` | 配置文件路径（可选，用于高级配置） | `/path/to/config.json` |

**替代方案（使用配置文件）：**

如果需要更复杂的配置，可创建配置文件：

```json
{
  "mcpServers": {
    "qingflow": {
      "command": "/path/to/qingflow-mcp",
      "env": {
        "QINGFLOW_MCP_CONFIG_PATH": "/path/to/qingflow-mcp.config.json"
      }
    }
  }
}
```

配置文件 `qingflow-mcp.config.json` 示例：
```json
{
  "default_base_url": "https://qingflow.com/api",
  "timeout_seconds": 30,
  "log_level": "INFO"
}
```

**配置文件搜索优先级：**
1. `QINGFLOW_MCP_CONFIG_PATH` 环境变量指定的路径
2. 当前工作目录下的 `qingflow-mcp.config.json`
3. `QINGFLOW_MCP_HOME` 目录下的 `config.json`（默认 `~/.qingflow-mcp/config.json`）
4. 系统级配置 `/etc/qingflow-mcp/config.json`（仅 Linux/Mac）

## Windows Build Special Handling

Windows binaries cannot be directly built on macOS/Linux. Use these methods:

### Method 1: GitHub Actions (Recommended)

Create `.github/workflows/build-windows.yml`:

```yaml
name: Build Windows Binary
on: [workflow_dispatch]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyinstaller
          pip install -e ".[build]"
        working-directory: qingflow-support/mcp-server
      
      - name: Build binary
        run: |
          python -m PyInstaller --name=qingflow-mcp --onefile --console entry_point.py
        working-directory: qingflow-support/mcp-server
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: qingflow-mcp-windows
          path: qingflow-support/mcp-server/dist/qingflow-mcp.exe
```

### Method 2: Local Windows Build (Simple)

On a Windows machine with Python 3.11+, double-click or run in Command Prompt:

```batch
# In Command Prompt
cd qingflow-support\mcp-server
scripts\build_binary.bat
```

Or manually:

```powershell
# In PowerShell
cd qingflow-support\mcp-server
python -m venv .venv
.\.venv\Scripts\pip install -e ".[build]"
.\.venv\Scripts\pip install pyinstaller
.\.venv\Scripts\python -m PyInstaller --name=qingflow-mcp --onefile --console entry_point.py
```

## Platform-Specific Notes

### macOS Universal Binary

- Combines arm64 and x86_64 into one executable
- Only builds on macOS (requires `lipo` tool)
- Best for distribution to mixed Mac environments

### Linux Builds

- Use Docker for cross-platform builds from macOS
- Native builds work on Linux machines
- Resulting binary is portable across Linux distributions with similar glibc

### Windows Builds

- PyInstaller cannot cross-compile from Unix to Windows
- Must use Windows environment or Wine (complex)
- GitHub Actions with `windows-latest` is easiest

## Troubleshooting

### "Docker not available"

Install Docker Desktop:
```bash
# macOS
brew install --cask docker

# Linux
curl -fsSL https://get.docker.com | sh
```

### "Python not found"

Install Python 3.11+:
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv
```

### "lipo command not found"

Install Xcode Command Line Tools:
```bash
xcode-select --install
```

### Binary too large

Expected sizes:
- Single arch: 22-25 MB
- Universal: 44-50 MB

If significantly larger, check PyInstaller excludes (matplotlib, numpy, etc. should be excluded).

### "Bad CPU type in executable"

Architecture mismatch. On Apple Silicon Mac:
```bash
# Check what you built
file dist/binary/macos-x64/qingflow-mcp  # Will say "x86_64"
file dist/binary/macos-arm64/qingflow-mcp  # Will say "arm64"

# Build Universal for both
./scripts/build_binary.sh --universal
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TARGET_PLATFORM` | Target platform | `linux`, `macos-arm64` |
| `USE_DOCKER` | Force Docker usage | `true`, `false` |

Example:
```bash
TARGET_PLATFORM=linux ./scripts/build_binary.sh
```

## Resources

- Unix build script: `scripts/build_binary.sh`
- Windows build script: `scripts/build_binary.bat`
- Cross-platform guide: `docs/cross-platform-build.md`
- Entry point: `entry_point.py`
- Output directory: `dist/binary/`
- GitHub Actions workflow: `.github/workflows/build-binaries.yml`

## Quick Command Reference

```bash
# Native build for current platform
cd qingflow-support/mcp-server && ./scripts/build_binary.sh

# macOS Universal Binary (macOS only)
./scripts/build_binary.sh --universal

# Linux builds via Docker
./scripts/build_binary.sh --target linux
./scripts/build_binary.sh --target linux-arm64

# Build all platforms
./scripts/build_binary.sh --all

# Trigger GitHub Actions builds
gh workflow run build-binaries.yml
```
