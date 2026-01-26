# ProtocolAnalyzer - Usage Examples

Quick navigation:
- [Example 1: Basic Project Analysis](#example-1-basic-project-analysis)
- [Example 2: Real-time Requirement Analysis](#example-2-real-time-requirement-analysis)
- [Example 3: Protocol Comparison](#example-3-protocol-comparison)
- [Example 4: Migration Planning](#example-4-migration-planning)
- [Example 5: JSON Report Generation](#example-5-json-report-generation)
- [Example 6: Markdown Documentation](#example-6-markdown-documentation)
- [Example 7: Python API Integration](#example-7-python-api-integration)
- [Example 8: Architecture Detection](#example-8-architecture-detection)
- [Example 9: Warning Detection](#example-9-warning-detection)
- [Example 10: Complete Workflow](#example-10-complete-workflow)

---

## Example 1: Basic Project Analysis

**Scenario:** First time using ProtocolAnalyzer to understand your project's communication patterns.

**Steps:**

```bash
# Navigate to ProtocolAnalyzer directory
cd C:\Users\logan\OneDrive\Documents\AutoProjects\ProtocolAnalyzer

# Check version
python protocolanalyzer.py --version

# Analyze a project
python protocolanalyzer.py analyze /path/to/your/project
```

**Expected Output:**

```
Protocol Analysis Report
========================
Project: /path/to/your/project
Architecture: backend
Complexity: 24.5

Summary: Architecture: backend. Detected protocols: http_rest, websocket.
         Recommended approach: WebSocket (score: 78/100).
         Rationale: Already in use (5 references found).

Detected Protocols:
  - http_rest: 4 files, 18 refs, complexity 16.5
  - websocket: 2 files, 5 refs, complexity 8.0

Recommendations:
  1. WebSocket (score: 78/100)
     Migration: LOW, Est: < 1 hour
  2. HTTP/REST (score: 75/100)
     Migration: LOW, Est: < 1 hour
  3. Server-Sent Events (SSE) (score: 62/100)
     Migration: MEDIUM, Est: 2-4 hours
```

**What You Learned:**
- Your project uses HTTP/REST and WebSocket
- WebSocket is the top recommendation (you already use it)
- Architecture is detected as "backend"

---

## Example 2: Real-time Requirement Analysis

**Scenario:** You're building a chat feature and need real-time communication advice.

**Steps:**

```bash
# Specify real-time requirement
python protocolanalyzer.py analyze ./my-chat-app --requirement realtime
```

**Expected Output:**

```
Protocol Analysis Report
========================
Project: ./my-chat-app
Architecture: full-stack
Complexity: 12.3

Summary: Architecture: full-stack. Detected protocols: http_rest.
         Recommended approach: WebSocket (score: 85/100).
         Rationale: Matches requirement: realtime, Simple, low-overhead protocol.

Detected Protocols:
  - http_rest: 3 files, 10 refs, complexity 12.3

Recommendations:
  1. WebSocket (score: 85/100)
     Migration: MEDIUM, Est: 2-4 hours
     Rationale: Matches requirement: realtime, Simple, low-overhead protocol
     
  2. Socket.IO (score: 70/100)
     Migration: MEDIUM, Est: 2-4 hours
     Rationale: Matches requirement: realtime
     
  3. Server-Sent Events (SSE) (score: 65/100)
     Migration: LOW, Est: < 1 hour
     Rationale: Good for real-time communication
```

**What You Learned:**
- WebSocket is recommended for chat (real-time)
- Socket.IO is an option but adds complexity
- SSE is simpler but one-way only

---

## Example 3: Protocol Comparison

**Scenario:** You're deciding between WebSocket and Socket.IO for a new feature.

**Steps:**

```bash
# Compare two protocols
python protocolanalyzer.py compare websocket socket.io
```

**Expected Output:**

```
=== WebSocket ===
  Category: realtime
  Complexity: 3/10
  Pros: Full-duplex communication, Low overhead after handshake, Standardized (RFC 6455)
  Cons: No automatic reconnection, No built-in message acknowledgment, Manual room/namespace management

=== Socket.IO ===
  Category: realtime
  Complexity: 6/10
  Pros: Automatic reconnection, Room/namespace support, Binary support
  Cons: Higher overhead than WebSocket, Version compatibility issues (v2/v3/v4), Not standard protocol
```

**What You Learned:**
- WebSocket has lower complexity (3/10 vs 6/10)
- Socket.IO adds features but has version compatibility issues
- Choose WebSocket for simplicity, Socket.IO for features

---

## Example 4: Migration Planning

**Scenario:** You want to migrate from Socket.IO to plain WebSocket.

**Steps:**

```bash
# Get migration guide
python protocolanalyzer.py migrate socket.io websocket
```

**Expected Output:**

```
Migration: Socket.IO -> WebSocket
Difficulty: MODERATE
Estimated Time: 2.0-4.0 days

Steps:
  1. Review all Socket.IO usage in codebase
  2. Install WebSocket dependencies: websockets, ws
  3. Create adapter/wrapper for WebSocket connections
  4. Migrate connection initialization code
  5. Update event handlers/callbacks
  6. Test all communication paths
  7. Remove Socket.IO dependencies
  8. Update documentation
```

**What You Learned:**
- Migration difficulty is MODERATE
- 8 concrete steps to follow
- Estimated 2-4 days of work

---

## Example 5: JSON Report Generation

**Scenario:** You need machine-readable output for CI/CD or other tools.

**Steps:**

```bash
# Generate JSON report
python protocolanalyzer.py analyze ./project --format json --output analysis.json

# View the JSON
cat analysis.json
```

**Expected Output:**

```json
{
  "project_path": "/full/path/to/project",
  "timestamp": "2026-01-25T12:30:45.123456",
  "detected_protocols": [
    {
      "name": "websocket",
      "total_lines": 8,
      "file_count": 2,
      "complexity_score": 24.5,
      "is_client": true,
      "is_server": false
    }
  ],
  "architecture_type": "frontend",
  "complexity_total": 24.5,
  "recommendations": [
    {
      "protocol": "WebSocket",
      "score": 82.5,
      "rationale": ["Already in use (8 references found)"],
      "pros": ["Full-duplex communication", "Low overhead"],
      "cons": ["No automatic reconnection"],
      "migration_complexity": "LOW",
      "estimated_time": "< 1 hour"
    }
  ],
  "summary": "Architecture: frontend...",
  "warnings": []
}
```

**What You Learned:**
- Full structured data available
- Can be parsed by other tools
- Includes detection details, recommendations, warnings

---

## Example 6: Markdown Documentation

**Scenario:** You want to generate protocol documentation for your project.

**Steps:**

```bash
# Generate Markdown report
python protocolanalyzer.py analyze ./project --format markdown --output PROTOCOLS.md
```

**Expected Output (PROTOCOLS.md):**

```markdown
# Protocol Analysis Report

**Project:** /path/to/project
**Analyzed:** 2026-01-25T12:30:45
**Architecture:** full-stack
**Total Complexity:** 45.2

## Summary

Architecture: full-stack. Detected protocols: websocket, http_rest.
Recommended approach: WebSocket (score: 82/100).

## Detected Protocols

| Protocol | Files | References | Complexity | Client | Server |
|----------|-------|------------|------------|--------|--------|
| websocket | 3 | 12 | 28.5 | [OK] | [OK] |
| http_rest | 5 | 25 | 16.7 | [OK] | |

## Recommendations

### 1. WebSocket (Score: 82/100)

**Migration Complexity:** LOW
**Estimated Time:** < 1 hour

**Rationale:**
- Already in use (12 references found)

**Pros:**
- Full-duplex communication
- Low overhead after handshake

**Cons:**
- No automatic reconnection
```

**What You Learned:**
- Professional documentation auto-generated
- Tables for easy scanning
- Structured recommendations

---

## Example 7: Python API Integration

**Scenario:** Integrate ProtocolAnalyzer into your Python workflow.

**Steps:**

```python
#!/usr/bin/env python3
"""Example: Using ProtocolAnalyzer Python API."""

from protocolanalyzer import ProtocolAnalyzer

# Initialize
analyzer = ProtocolAnalyzer(verbose=True)

# 1. Analyze a project
result = analyzer.analyze("./my-project", requirement="realtime")

# 2. Access detection results
print("Detected Protocols:")
for proto in result.detected_protocols:
    print(f"  - {proto.name}: {proto.file_count} files, complexity {proto.complexity_score:.1f}")
    print(f"    Client: {proto.is_client}, Server: {proto.is_server}")

# 3. Get recommendations
print("\nRecommendations:")
for i, rec in enumerate(result.recommendations[:3], 1):
    print(f"  {i}. {rec.protocol} (score: {rec.score:.0f}/100)")
    print(f"     Rationale: {rec.rationale[0]}")
    print(f"     Migration: {rec.migration_complexity}")

# 4. Check warnings
if result.warnings:
    print("\nWarnings:")
    for warning in result.warnings:
        print(f"  [!] {warning}")

# 5. Compare specific protocols
print("\nProtocol Comparison:")
comparison = analyzer.compare_protocols(["websocket", "socket.io"])
for name, data in comparison.items():
    print(f"  {name}: complexity {data['complexity']}/10")

# 6. Get migration guide
print("\nMigration Guide (Socket.IO -> WebSocket):")
guide = analyzer.get_migration_guide("socket.io", "websocket")
print(f"  Difficulty: {guide['difficulty']}")
print(f"  Time: {guide['estimated_time']}")

# 7. Export reports
json_report = analyzer.to_json(result)
md_report = analyzer.to_markdown(result)

# Save reports
with open("analysis.json", "w") as f:
    f.write(json_report)
    
with open("PROTOCOLS.md", "w") as f:
    f.write(md_report)
```

**Expected Output:**

```
Detected Protocols:
  - websocket: 2 files, complexity 24.5
    Client: True, Server: False
  - http_rest: 4 files, complexity 16.7
    Client: True, Server: True

Recommendations:
  1. WebSocket (score: 82/100)
     Rationale: Already in use (5 references found)
     Migration: LOW
  2. HTTP/REST (score: 76/100)
     Rationale: Already in use (18 references found)
     Migration: LOW

Warnings:
  [!] Multiple real-time protocols detected: websocket, socket.io. Consider consolidating.

Protocol Comparison:
  WebSocket: complexity 3/10
  Socket.IO: complexity 6/10

Migration Guide (Socket.IO -> WebSocket):
  Difficulty: MODERATE
  Time: 2.0-4.0 days
```

---

## Example 8: Architecture Detection

**Scenario:** Understand the architecture type of different projects.

**Steps:**

```bash
# Backend-only project
python protocolanalyzer.py analyze ./backend-api

# Frontend-only project  
python protocolanalyzer.py analyze ./frontend-app

# Full-stack project
python protocolanalyzer.py analyze ./fullstack-project
```

**Expected Outputs:**

```
# Backend-only (has server patterns like listen(), serve(), @app.route)
Architecture: backend

# Frontend-only (has client patterns like fetch(), connect(), io())
Architecture: frontend

# Full-stack (has both client and server patterns)
Architecture: full-stack

# No protocols detected
Architecture: unknown
```

**What You Learned:**
- Architecture is auto-detected from code patterns
- Helps understand project structure
- Guides appropriate recommendations

---

## Example 9: Warning Detection

**Scenario:** Identify potential issues in your protocol usage.

**Steps:**

```bash
# Analyze a project with multiple real-time protocols
python protocolanalyzer.py analyze ./multi-protocol-project
```

**Expected Output:**

```
Protocol Analysis Report
========================
Project: ./multi-protocol-project
Architecture: full-stack
Complexity: 85.3

Warnings:
  [!] Socket.IO detected: Ensure client/server versions match (v4 client requires v4 server)
  [!] Multiple real-time protocols detected: websocket, socket.io. Consider consolidating to reduce complexity.
  [!] High complexity protocols: socket.io, grpc. Review if simpler alternatives exist.

Detected Protocols:
  - socket.io: 5 files, 22 refs, complexity 42.5
  - websocket: 2 files, 8 refs, complexity 18.3
  - grpc: 3 files, 15 refs, complexity 24.5
```

**What You Learned:**
- Socket.IO version compatibility warning
- Multiple real-time protocols flagged
- High complexity protocols identified

---

## Example 10: Complete Workflow

**Scenario:** Full analysis workflow for a new project.

**Steps:**

```bash
# Step 1: Initial analysis
python protocolanalyzer.py analyze ./new-project

# Step 2: List available protocols for your requirement
python protocolanalyzer.py list --category realtime

# Step 3: Compare top candidates
python protocolanalyzer.py compare websocket sse

# Step 4: Make decision and analyze impact
python protocolanalyzer.py analyze ./new-project --requirement realtime

# Step 5: If migrating, get guide
python protocolanalyzer.py migrate http_rest websocket

# Step 6: Generate documentation
python protocolanalyzer.py analyze ./new-project --format markdown --output docs/PROTOCOL_DECISIONS.md

# Step 7: Generate JSON for CI/CD
python protocolanalyzer.py analyze ./new-project --format json --output .protocol-analysis.json
```

**Complete Session Example:**

```bash
$ python protocolanalyzer.py analyze ./chat-app

Protocol Analysis Report
========================
Project: ./chat-app
Architecture: full-stack
Complexity: 28.5

Summary: Currently using HTTP/REST. For real-time chat, recommend WebSocket.

Detected Protocols:
  - http_rest: 6 files, 24 refs, complexity 28.5

Recommendations:
  1. WebSocket (score: 75/100) - Best for chat
  2. Socket.IO (score: 68/100) - More features, more complexity
  3. HTTP/REST (score: 65/100) - Already in use

$ python protocolanalyzer.py compare websocket socket.io

=== WebSocket ===
  Complexity: 3/10
  Pros: Full-duplex, Low overhead, Standardized
  Cons: Manual reconnection, No rooms built-in

=== Socket.IO ===
  Complexity: 6/10
  Pros: Auto-reconnect, Rooms, Fallback support
  Cons: Version issues, Higher overhead

Decision: Use WebSocket for simplicity

$ python protocolanalyzer.py migrate http_rest websocket

Migration: HTTP/REST -> WebSocket
Difficulty: MODERATE
Steps: 8 concrete steps...

$ python protocolanalyzer.py analyze ./chat-app --format markdown --output PROTOCOLS.md

[OK] Report saved to: PROTOCOLS.md
```

---

## Advanced Examples

### Analyze Specific File Extensions

```python
from protocolanalyzer import ProtocolDetector

# Customize which extensions to scan
detector = ProtocolDetector()
detector.SCAN_EXTENSIONS = {'.py', '.ts'}  # Only Python and TypeScript

detections = detector.scan_project(Path("./project"))
```

### Custom Requirement Mapping

```python
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()

# Map your needs to protocol categories
requirement_map = {
    "chat": "realtime",
    "api": "request-response",
    "logs": "streaming",
    "microservices": "rpc"
}

need = "chat"
result = analyzer.analyze("./project", requirement=requirement_map[need])
```

### Batch Analysis

```bash
#!/bin/bash
# Analyze multiple projects

for project in ./project-*; do
    echo "Analyzing $project..."
    python protocolanalyzer.py analyze "$project" --format json --output "$project/protocol-analysis.json"
done
```

---

## Need More Help?

- **Documentation:** [README.md](README.md)
- **Quick Reference:** [CHEAT_SHEET.txt](CHEAT_SHEET.txt)
- **Integration:** [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- **GitHub Issues:** https://github.com/DonkRonk17/ProtocolAnalyzer/issues

---

*Built with 💙 by Team Brain*
