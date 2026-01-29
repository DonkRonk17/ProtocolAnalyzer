<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/2ef05927-c676-4216-8cc8-676053741e25" />

# 🔌 ProtocolAnalyzer

## Compare Protocol Options and Recommend the Simplest Solution

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/DonkRonk17/ProtocolAnalyzer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-yellow.svg)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-59%20passing-brightgreen.svg)](test_protocolanalyzer.py)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](requirements.txt)

> **The right protocol is the simplest one that solves your problem.**

ProtocolAnalyzer scans your project, identifies communication protocol usage (WebSocket, Socket.IO, HTTP, gRPC, GraphQL, etc.), and recommends the simplest approach based on your existing architecture.

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [CLI Commands](#cli-commands)
  - [Python API](#python-api)
- [Supported Protocols](#-supported-protocols)
- [Real-World Example](#-real-world-example)
- [How It Works](#-how-it-works)
- [Integration](#-integration)
- [Use Cases](#-use-cases)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Credits](#-credits)
- [License](#-license)

---

## 🚨 The Problem

When building applications that need real-time or API communication, developers face countless protocol choices:

**Common Mistakes:**
- Choosing Socket.IO when plain WebSocket would suffice
- Using gRPC when REST would be simpler
- Mixing multiple real-time protocols unnecessarily
- Version mismatches (Socket.IO v4 client + v3 server = silent failures)

**The BCH Story:**

During BCH (Beacon Command Hub) development, hours were wasted on Socket.IO v4/v5 incompatibility. The client connected but messages never arrived. After debugging, the solution was simple: use plain WebSocket instead.

**Had ProtocolAnalyzer existed, it would have said:**
```
[!] Warning: You already use WebSocket in 3 files.
    Recommendation: Stick with WebSocket (score: 85/100)
    Socket.IO adds complexity without clear benefit for your use case.
```

**Time Lost:** 2+ hours
**Time Saved with ProtocolAnalyzer:** ~30-60 minutes per session

---

## ✅ The Solution

ProtocolAnalyzer provides intelligent protocol recommendations:

```bash
$ protocolanalyzer analyze ./my-project

Protocol Analysis Report
========================
Project: ./my-project
Architecture: full-stack
Complexity: 45.2

Summary: Architecture: full-stack. Detected protocols: websocket, http_rest.
         Recommended approach: WebSocket (score: 82/100).
         Rationale: Already in use (8 references found).

Detected Protocols:
  - websocket: 2 files, 8 refs, complexity 28.5
  - http_rest: 3 files, 12 refs, complexity 16.7

Recommendations:
  1. WebSocket (score: 82/100)
     Migration: LOW, Est: < 1 hour
  2. HTTP/REST (score: 76/100)
     Migration: LOW, Est: < 1 hour
  3. Server-Sent Events (SSE) (score: 65/100)
     Migration: MEDIUM, Est: 2-4 hours
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Protocol Detection** | Scan project for 8+ protocol types with pattern matching |
| 📊 **Complexity Scoring** | Calculate complexity based on LOC, dependencies, risk |
| 🏗️ **Architecture Analysis** | Identify client/server/full-stack patterns |
| 💡 **Smart Recommendations** | Score and rank protocols for your use case |
| ⚖️ **Protocol Comparison** | Side-by-side comparison with pros/cons |
| 🔄 **Migration Guides** | Step-by-step guides for protocol switches |
| ⚠️ **Warning System** | Alert on version issues, complexity, conflicts |
| 📝 **Multiple Output Formats** | Text, JSON, Markdown reports |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/DonkRonk17/ProtocolAnalyzer.git
cd ProtocolAnalyzer

# No dependencies required! Just run:
python protocolanalyzer.py analyze ./your-project
```

### First Analysis

```bash
# Analyze your project
python protocolanalyzer.py analyze /path/to/your/project

# Compare protocols
python protocolanalyzer.py compare websocket socket.io

# Get migration guide
python protocolanalyzer.py migrate socket.io websocket
```

**That's it!** Zero dependencies, instant results.

---

## 📖 Usage

### CLI Commands

#### 1. Analyze a Project

```bash
# Basic analysis
protocolanalyzer analyze ./my-project

# Specify requirement type
protocolanalyzer analyze ./my-project --requirement realtime

# Output to file
protocolanalyzer analyze ./my-project --output report.md --format markdown

# Verbose mode
protocolanalyzer analyze ./my-project --verbose
```

**Output:**
```
Protocol Analysis Report
========================
Project: /home/user/my-project
Architecture: backend
Complexity: 32.5

Summary: Architecture: backend. Detected protocols: socket.io.
         Recommended approach: WebSocket (score: 75/100).
         Rationale: Simple, low-overhead protocol.

Warnings:
  [!] Socket.IO detected: Ensure client/server versions match

Detected Protocols:
  - socket.io: 4 files, 15 refs, complexity 32.5

Recommendations:
  1. WebSocket (score: 75/100)
     Migration: MEDIUM, Est: 2-4 hours
```

#### 2. Compare Protocols

```bash
# Compare multiple protocols
protocolanalyzer compare websocket socket.io grpc

# Output as JSON
protocolanalyzer compare websocket http --format json
```

**Output:**
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
  Cons: Higher overhead than WebSocket, Version compatibility issues (v2/v3/v4)

=== gRPC ===
  Category: rpc
  Complexity: 7/10
  Pros: High performance (HTTP/2), Strongly typed with protobuf, Bidirectional streaming
  Cons: Browser support limited (grpc-web), Requires protobuf knowledge, More complex setup
```

#### 3. Get Migration Guide

```bash
# Migration guide between protocols
protocolanalyzer migrate socket.io websocket

# As Markdown
protocolanalyzer migrate grpc http_rest --format markdown
```

**Output:**
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

#### 4. List Known Protocols

```bash
# List all protocols
protocolanalyzer list

# Filter by category
protocolanalyzer list --category realtime
```

**Output:**
```
Known Protocols:
==================================================

WebSocket
  Category: realtime
  Complexity: 3/10
  Use cases: Real-time chat, Live updates

Socket.IO
  Category: realtime
  Complexity: 6/10
  Use cases: Complex real-time apps, Chat with rooms

HTTP/REST
  Category: request-response
  Complexity: 2/10
  Use cases: CRUD APIs, Microservices
```

### Python API

```python
from protocolanalyzer import ProtocolAnalyzer

# Initialize analyzer
analyzer = ProtocolAnalyzer(verbose=True)

# Analyze a project
result = analyzer.analyze("/path/to/project", requirement="realtime")

# Access results
print(f"Architecture: {result.architecture_type}")
print(f"Detected protocols: {[p.name for p in result.detected_protocols]}")
print(f"Top recommendation: {result.recommendations[0].protocol}")

# Export reports
json_report = analyzer.to_json(result)
markdown_report = analyzer.to_markdown(result)

# Compare protocols
comparison = analyzer.compare_protocols(["websocket", "socket.io", "grpc"])
for name, data in comparison.items():
    print(f"{name}: complexity {data['complexity']}/10")

# Get migration guide
guide = analyzer.get_migration_guide("socket.io", "websocket")
print(f"Difficulty: {guide['difficulty']}")
for step in guide['steps']:
    print(f"  {step}")
```

---

## 📚 Supported Protocols

| Protocol | Category | Complexity | Detection Patterns |
|----------|----------|------------|-------------------|
| **WebSocket** | realtime | 3/10 | `new WebSocket`, `websocket.connect`, `ws://` |
| **Socket.IO** | realtime | 6/10 | `import socketio`, `io()`, `.emit()` |
| **HTTP/REST** | request-response | 2/10 | `requests.get`, `fetch()`, `axios.` |
| **HTTP Long-Polling** | request-response | 4/10 | `setInterval.*fetch`, `poll` |
| **gRPC** | rpc | 7/10 | `import grpc`, `.proto`, `protobuf` |
| **GraphQL** | request-response | 5/10 | `gql\``, `useQuery`, `ApolloClient` |
| **SSE** | streaming | 2/10 | `new EventSource`, `text/event-stream` |
| **MQTT** | realtime | 5/10 | `paho-mqtt`, `mqtt://` |

### Protocol Categories

- **realtime**: Bidirectional, persistent connections (WebSocket, Socket.IO, MQTT)
- **request-response**: Client initiates, server responds (HTTP/REST, GraphQL)
- **streaming**: Server pushes data to client (SSE)
- **rpc**: Remote procedure calls (gRPC)

---

## 🎯 Real-World Example

### Scenario: BCH Mobile App Development

Your project has:
- Flask backend with REST API
- React Native mobile app
- Need to add real-time notifications

```bash
$ protocolanalyzer analyze ./bch-mobile --requirement realtime
```

**Output:**
```
Protocol Analysis Report
========================
Project: ./bch-mobile
Architecture: full-stack
Complexity: 28.5

Summary: Architecture: full-stack. Detected protocols: http_rest.
         Recommended approach: Server-Sent Events (SSE) (score: 78/100).
         Rationale: Simple one-way streaming, works with existing HTTP infrastructure.

Detected Protocols:
  - http_rest: 8 files, 35 refs, complexity 28.5

Recommendations:
  1. Server-Sent Events (SSE) (score: 78/100)
     Migration: LOW, Est: < 1 hour
     Rationale: Good for real-time, Same category as existing http_rest
     
  2. WebSocket (score: 72/100)
     Migration: MEDIUM, Est: 2-4 hours
     Rationale: Matches requirement: realtime, Simple, low-overhead protocol
     
  3. HTTP/REST (score: 70/100)
     Migration: LOW, Est: < 1 hour
     Rationale: Already in use (35 references found)
```

**Insight:** SSE is recommended because:
1. You only need server → client notifications (one-way)
2. You already have HTTP infrastructure
3. SSE is simpler than WebSocket for this use case

---

## 🔧 How It Works

### 1. Detection Phase

ProtocolAnalyzer scans your project for protocol-specific patterns:

```python
# Example detection patterns
DETECTION_PATTERNS = {
    "websocket": [
        (r"new\s+WebSocket\s*\(", 0.95),   # High confidence
        (r"ws://|wss://", 0.8),             # Medium confidence
        (r"\.onmessage\s*=", 0.7),          # Context-dependent
    ],
    # ... more patterns for each protocol
}
```

Each detection has a confidence score (0.0 to 1.0).

### 2. Analysis Phase

For each detected protocol, we calculate:

```
Complexity Score = base_complexity * scale_factor * confidence_factor * spread_factor
```

Where:
- **base_complexity**: Protocol inherent complexity (1-10)
- **scale_factor**: Based on lines of code (1.0-2.0)
- **confidence_factor**: Based on detection confidence (0.5-1.0)
- **spread_factor**: Based on file count (1.0-1.5)

### 3. Recommendation Phase

Protocols are scored based on:
- **+20 points**: Matches your requirement category
- **+25 points**: Already in use (consistency bonus)
- **-27 points**: High complexity penalty
- **+10 points**: Same category as existing protocols
- **+10 points**: Simple protocol bonus (complexity ≤ 3)

### 4. Architecture Detection

```python
def _determine_architecture(self, protocols):
    has_client = any(p.is_client for p in protocols)
    has_server = any(p.is_server for p in protocols)
    
    if has_client and has_server:
        return "full-stack"
    elif has_server:
        return "backend"
    elif has_client:
        return "frontend"
    else:
        return "unknown"
```

---

## 🔗 Integration

### With Team Brain Tools

ProtocolAnalyzer integrates with the Team Brain ecosystem:

```python
# Integration with AgentHandoff
from agenthandoff import AgentHandoff
from protocolanalyzer import ProtocolAnalyzer

handoff = AgentHandoff()
analyzer = ProtocolAnalyzer()

# Analyze before architecture decisions
result = analyzer.analyze("./project")

# Include in handoff context
handoff.create_handoff(
    target="IRIS",
    context={
        "protocol_analysis": analyzer.to_json(result),
        "recommended_protocol": result.recommendations[0].protocol
    }
)
```

### With SynapseLink

```python
from synapselink import quick_send
from protocolanalyzer import ProtocolAnalyzer

analyzer = ProtocolAnalyzer()
result = analyzer.analyze("./project")

# Share analysis with team
quick_send(
    "TEAM",
    "Protocol Analysis Complete",
    f"Detected: {', '.join([p.name for p in result.detected_protocols])}\n"
    f"Recommendation: {result.recommendations[0].protocol}\n"
    f"Score: {result.recommendations[0].score:.0f}/100",
    priority="NORMAL"
)
```

### With BuildEnvValidator

```python
from buildenvvalidator import BuildEnvValidator
from protocolanalyzer import ProtocolAnalyzer

# Analyze protocols first
pa = ProtocolAnalyzer()
result = pa.analyze("./project")

# Validate environment for detected protocols
bev = BuildEnvValidator()
for proto in result.detected_protocols:
    if proto.name == "grpc":
        bev.check_tool("protoc", "protobuf compiler")
    elif proto.name == "mqtt":
        bev.check_tool("mosquitto", "MQTT broker")
```

---

## 💼 Use Cases

### 1. New Project Architecture Decisions

```bash
# You're starting a new chat app
protocolanalyzer list --category realtime

# Compare options
protocolanalyzer compare websocket socket.io mqtt
```

### 2. Debugging Protocol Issues

```bash
# Project has communication issues
protocolanalyzer analyze ./buggy-project --verbose

# Check for version warnings
# Check for mixed protocol usage
```

### 3. Migration Planning

```bash
# Planning to switch from Socket.IO to WebSocket
protocolanalyzer migrate socket.io websocket --format markdown > migration_plan.md
```

### 4. Code Review

```bash
# Review protocol choices in a PR
protocolanalyzer analyze ./feature-branch --output protocol_review.json --format json
```

### 5. Architecture Documentation

```bash
# Generate protocol documentation
protocolanalyzer analyze ./project --output docs/PROTOCOLS.md --format markdown
```

---

## 🔧 Troubleshooting

### Common Issues

**Q: No protocols detected in my project**

A: Check that your source files have supported extensions (`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.go`, `.rs`). Also ensure you're not scanning inside `node_modules` or `__pycache__`.

```bash
# Debug with verbose mode
protocolanalyzer analyze ./project --verbose
```

**Q: False positives in detection**

A: Some patterns have lower confidence scores. High-confidence detections (0.9+) are typically accurate. Review the context in JSON output:

```bash
protocolanalyzer analyze ./project --format json | grep "confidence"
```

**Q: Migration time estimates seem off**

A: Estimates are based on file count and complexity. For large codebases with many files, actual time may vary. Use the difficulty rating (LOW/MEDIUM/HIGH) as the primary indicator.

**Q: Custom protocol not detected**

A: Currently supports 8 major protocols. For custom protocols, you can extend the `DETECTION_PATTERNS` dictionary or request a feature.

### Error Messages

| Error | Solution |
|-------|----------|
| `FileNotFoundError: Project not found` | Check the project path exists |
| `Protocol not found in database` | Use `protocolanalyzer list` to see supported protocols |
| `Error: Source protocol not found` | Check spelling when using `migrate` command |

---

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/4881fc94-2196-482c-a0af-2451a5e45eb7" />


## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Report Issues**: Open a GitHub issue for bugs or feature requests
2. **Add Protocols**: Contribute detection patterns for new protocols
3. **Improve Detection**: Submit better regex patterns
4. **Documentation**: Help improve examples and guides

### Development Setup

```bash
git clone https://github.com/DonkRonk17/ProtocolAnalyzer.git
cd ProtocolAnalyzer

# Run tests
python test_protocolanalyzer.py

# Test a specific protocol
python -c "from protocolanalyzer import ProtocolAnalyzer; print(ProtocolAnalyzer().compare_protocols(['websocket']))"
```

---

## 📝 Credits

**Built by:** ATLAS (Team Brain)  
**For:** Logan Smith / Metaphy LLC  
**Requested by:** IRIS (Tool Request #20)  
**Why:** Would have prevented 2+ hours wasted on Socket.IO v4/v5 incompatibility during BCH development  
**Part of:** Beacon HQ / Team Brain Ecosystem  
**Date:** January 25, 2026

**Problem Origin:**

During BCH mobile development, IRIS spent hours debugging why Socket.IO connections would establish but messages never arrived. The root cause: Socket.IO v4 client with v3 server - a silent incompatibility. ProtocolAnalyzer now warns about these issues and recommends simpler alternatives when appropriate.

**Special Thanks:**
- IRIS for the insightful tool request and BCH debugging experience
- The Team Brain collective for protocol pattern contributions
- FORGE for Q-Mode infrastructure that enables autonomous tool building

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

```
MIT License

Copyright (c) 2026 Logan Smith / Metaphy LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 📚 Additional Resources

- **Examples:** [EXAMPLES.md](EXAMPLES.md)
- **Quick Reference:** [CHEAT_SHEET.txt](CHEAT_SHEET.txt)
- **Integration Guide:** [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- **Agent Quick Starts:** [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md)
- **Integration Examples:** [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md)
- **GitHub:** https://github.com/DonkRonk17/ProtocolAnalyzer
- **Issues:** https://github.com/DonkRonk17/ProtocolAnalyzer/issues

---

**ProtocolAnalyzer** - *The right protocol is the simplest one that solves your problem.*

*Built with 💙 by Team Brain*
