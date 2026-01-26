# ProtocolAnalyzer - Quick Start Guides

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)
- [IRIS (Build Specialist)](#-iris-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Learn to review protocol choices and flag complexity issues

### Step 1: Installation Check

```bash
# Verify ProtocolAnalyzer is available
python protocolanalyzer.py --version

# Expected: protocolanalyzer 1.0
```

### Step 2: First Use - Review a PR

```bash
# Analyze the feature branch
python protocolanalyzer.py analyze ./feature-branch

# Look for:
# - Warnings about version compatibility
# - High complexity scores
# - Mixed protocol usage
```

### Step 3: Code Review Workflow

```python
# In your Forge review session
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()
result = analyzer.analyze("./pr-branch")

# Quick checks for reviews
print(f"Complexity: {result.complexity_total:.1f}")
print(f"Warnings: {len(result.warnings)}")

# Flag issues
if result.complexity_total > 50:
    print("[!] HIGH COMPLEXITY - Review needed")
if result.warnings:
    for w in result.warnings:
        print(f"[!] {w}")
```

### Step 4: Common Forge Commands

```bash
# Compare protocol options (for architecture decisions)
python protocolanalyzer.py compare websocket socket.io grpc

# Check if migration is needed
python protocolanalyzer.py migrate socket.io websocket

# Generate review report
python protocolanalyzer.py analyze ./project -f markdown -o PROTOCOL_REVIEW.md
```

### Next Steps for Forge
1. Add to code review checklist
2. Flag high-complexity protocol choices
3. Recommend simplifications where possible

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Select optimal protocol before building tools

### Step 1: Installation Check

```bash
python -c "from protocolanalyzer import ProtocolAnalyzer; print('OK')"
```

### Step 2: First Use - Pre-Build Analysis

```python
# Before starting a new tool with communication needs
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()

# Analyze existing patterns in the codebase
result = analyzer.analyze("./AutoProjects", requirement="realtime")

print(f"Existing protocols: {[p.name for p in result.detected_protocols]}")
print(f"Recommended: {result.recommendations[0].protocol}")
```

### Step 3: Integration with Tool Building

```python
# During Holy Grail automation - protocol selection phase
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()

# Compare options for your use case
comparison = analyzer.compare_protocols(["websocket", "http_rest", "sse"])

for name, data in comparison.items():
    print(f"{name}: complexity {data['complexity']}/10")
    print(f"  Pros: {', '.join(data['pros'][:2])}")

# Document your choice in README
PROTOCOL_CHOICE = "websocket"
RATIONALE = "Low complexity (3/10), full-duplex needed for real-time updates"
```

### Step 4: Common Atlas Commands

```bash
# Quick analysis before building
python protocolanalyzer.py analyze ./existing-project -r realtime

# Compare two main options
python protocolanalyzer.py compare websocket socket.io

# List all options for a category
python protocolanalyzer.py list -c realtime
```

### Next Steps for Atlas
1. Run analysis at start of every tool build needing communication
2. Document protocol choice rationale in README
3. Re-analyze after implementation to verify

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 5 minutes  
**Goal:** Analyze Linux projects from CLI

### Step 1: Linux Installation

```bash
# Clone from GitHub
git clone https://github.com/DonkRonk17/ProtocolAnalyzer.git
cd ProtocolAnalyzer

# No dependencies needed! Verify it works:
python3 protocolanalyzer.py --version
```

### Step 2: First Use - Analyze Linux Project

```bash
# Navigate to your project
cd ~/projects/my-linux-app

# Run analysis
python3 ~/AutoProjects/ProtocolAnalyzer/protocolanalyzer.py analyze .

# Or with specific requirement
python3 protocolanalyzer.py analyze . --requirement realtime
```

### Step 3: CLI-Focused Workflow

```bash
# Quick comparison
python3 protocolanalyzer.py compare websocket mqtt

# Output to file for sharing
python3 protocolanalyzer.py analyze . -f markdown -o PROTOCOLS.md

# JSON for scripting
python3 protocolanalyzer.py analyze . -f json | jq '.recommendations[0].protocol'
```

### Step 4: Common Clio Commands

```bash
# Full analysis with verbose output
python3 protocolanalyzer.py analyze . -v

# Migration guide as Markdown
python3 protocolanalyzer.py migrate grpc http_rest -f markdown > migration.md

# List all streaming protocols
python3 protocolanalyzer.py list -c streaming
```

### Platform-Specific Notes
- Works identically on Ubuntu, Debian, other Linux distros
- MQTT may need mosquitto: `sudo apt install mosquitto`
- gRPC needs protoc: `sudo apt install protobuf-compiler`

### Next Steps for Clio
1. Add to project analysis scripts
2. Include in ABIOS startup checks
3. Share reports via SynapseLink

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Validate cross-platform protocol compatibility

### Step 1: Platform Detection

```python
import platform
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()
print(f"Running on: {platform.system()}")  # Windows, Linux, or Darwin

result = analyzer.analyze("./cross-platform-project")
print(f"Architecture: {result.architecture_type}")
```

### Step 2: First Use - Cross-Platform Validation

```python
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()
result = analyzer.analyze("./project")

# Check platform compatibility notes
for proto in result.detected_protocols:
    comparison = analyzer.compare_protocols([proto.name])
    if proto.name in comparison:
        compat = comparison[proto.name].get('compatibility', {})
        print(f"\n{proto.name} compatibility:")
        for platform_name, note in compat.items():
            print(f"  {platform_name}: {note}")
```

### Step 3: Platform-Specific Analysis

```bash
# Windows
python protocolanalyzer.py analyze .\windows-app

# Linux  
python3 protocolanalyzer.py analyze ./linux-app

# macOS
python3 protocolanalyzer.py analyze ./mac-app
```

### Step 4: Common Nexus Commands

```bash
# Compare protocols with platform focus
python protocolanalyzer.py compare websocket grpc -f json

# Check for platform-specific warnings
python protocolanalyzer.py analyze ./project -v | grep -i platform

# Generate cross-platform report
python protocolanalyzer.py analyze ./project -f markdown -o CROSS_PLATFORM.md
```

### Cross-Platform Notes
- WebSocket: Native support everywhere
- Socket.IO: Version matching critical on all platforms
- gRPC: Requires protoc on all platforms
- MQTT: May need platform-specific broker setup

### Next Steps for Nexus
1. Test on all 3 platforms
2. Document platform-specific requirements
3. Report any platform-specific issues

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Cost-efficient protocol analysis without API usage

### Step 1: Verify Free Access

```bash
# No API key required!
python protocolanalyzer.py --version

# Zero dependencies, zero external calls
```

### Step 2: First Use - Batch Analysis

```bash
# Analyze single project
python protocolanalyzer.py analyze ./my-project

# Batch analyze multiple projects (cost-free!)
for dir in ./project-*; do
    echo "=== $dir ===" >> report.txt
    python protocolanalyzer.py analyze "$dir" >> report.txt
done
```

### Step 3: Cost-Efficient Workflows

```bash
# Quick protocol lookup (no analysis needed)
python protocolanalyzer.py list -c realtime

# Simple comparison
python protocolanalyzer.py compare websocket http

# Generate reports for later review
python protocolanalyzer.py analyze ./project -f json -o analysis.json
```

### Step 4: Common Bolt Commands

```bash
# Minimal output for quick decisions
python protocolanalyzer.py analyze ./project | head -20

# Text format (most compact)
python protocolanalyzer.py analyze ./project -f text

# Offline-friendly (all local processing)
python protocolanalyzer.py compare websocket socket.io sse mqtt
```

### Cost Benefits
- Zero API calls
- Zero external dependencies
- Local processing only
- Can run in restricted environments

### Next Steps for Bolt
1. Add to Cline workflows
2. Use for repetitive analysis tasks
3. Generate reports for team review

---

## 🔧 IRIS QUICK START

**Role:** Build Environment Specialist  
**Time:** 5 minutes  
**Goal:** Pre-validate protocol dependencies before builds

### Step 1: Installation Check

```python
# Verify both tools available
from protocolanalyzer import ProtocolAnalyzer
from buildenvvalidator import BuildEnvValidator  # Your tool

print("ProtocolAnalyzer: OK")
print("BuildEnvValidator: OK")
```

### Step 2: First Use - Pre-Build Validation

```python
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()
result = analyzer.analyze("./mobile-app", requirement="realtime")

# Check what protocols are used
print("Detected protocols:")
for proto in result.detected_protocols:
    print(f"  - {proto.name}")

# Flag potential build issues
if any(p.name == "grpc" for p in result.detected_protocols):
    print("[!] gRPC detected - verify protoc is installed")
if any(p.name == "socket.io" for p in result.detected_protocols):
    print("[!] Socket.IO detected - verify version compatibility")
```

### Step 3: Integration with BuildEnvValidator

```python
from protocolanalyzer import ProtocolAnalyzer
from buildenvvalidator import BuildEnvValidator

pa = ProtocolAnalyzer()
bev = BuildEnvValidator()

result = pa.analyze("./project")

# Auto-check dependencies based on protocols
PROTOCOL_DEPS = {
    "grpc": [("protoc", "protobuf compiler")],
    "mqtt": [("mosquitto", "MQTT broker (optional)")],
}

for proto in result.detected_protocols:
    if proto.name in PROTOCOL_DEPS:
        for tool, desc in PROTOCOL_DEPS[proto.name]:
            bev.check_tool(tool, desc)

# Check for version warnings
for warning in result.warnings:
    if "version" in warning.lower():
        print(f"[!] VERSION CHECK NEEDED: {warning}")
```

### Step 4: Common IRIS Commands

```bash
# Full analysis before build attempt
python protocolanalyzer.py analyze ./project -v

# Check specific protocol requirements
python protocolanalyzer.py compare grpc -f json | grep dependencies

# Integration with VersionGuard
python protocolanalyzer.py analyze ./project -f json > protocols.json
# Then feed to VersionGuard for dependency checking
```

### Integration Pattern

```python
# Complete pre-build check
def pre_build_protocol_check(project_path):
    from protocolanalyzer import ProtocolAnalyzer
    
    analyzer = ProtocolAnalyzer()
    result = analyzer.analyze(project_path)
    
    issues = []
    
    # Check warnings
    issues.extend(result.warnings)
    
    # Check high complexity
    if result.complexity_total > 60:
        issues.append(f"High protocol complexity: {result.complexity_total:.1f}")
    
    # Check for known problematic patterns
    proto_names = [p.name for p in result.detected_protocols]
    if "socket.io" in proto_names and "websocket" in proto_names:
        issues.append("Mixed WebSocket and Socket.IO - potential conflicts")
    
    return issues

# Use before any build
issues = pre_build_protocol_check("./mobile-app")
if issues:
    print("PRE-BUILD WARNINGS:")
    for issue in issues:
        print(f"  [!] {issue}")
```

### Next Steps for IRIS
1. Add protocol check to build validation workflow
2. Create protocol dependency database
3. Integrate warnings into build reports

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/ProtocolAnalyzer/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Message ATLAS

---

**Last Updated:** January 25, 2026  
**Maintained By:** ATLAS (Team Brain)
