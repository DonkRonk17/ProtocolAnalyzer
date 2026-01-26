# ProtocolAnalyzer - Integration Examples

## 🎯 INTEGRATION PHILOSOPHY

ProtocolAnalyzer is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: ProtocolAnalyzer + VersionGuard](#pattern-1-protocolanalyzer--versionguard)
2. [Pattern 2: ProtocolAnalyzer + BuildEnvValidator](#pattern-2-protocolanalyzer--buildenvvalidator)
3. [Pattern 3: ProtocolAnalyzer + SynapseLink](#pattern-3-protocolanalyzer--synapselink)
4. [Pattern 4: ProtocolAnalyzer + AgentHandoff](#pattern-4-protocolanalyzer--agenthandoff)
5. [Pattern 5: ProtocolAnalyzer + PostMortem](#pattern-5-protocolanalyzer--postmortem)
6. [Pattern 6: ProtocolAnalyzer + ContextSynth](#pattern-6-protocolanalyzer--contextsynth)
7. [Pattern 7: ProtocolAnalyzer + TeamCoherenceMonitor](#pattern-7-protocolanalyzer--teamcoherencemonitor)
8. [Pattern 8: ProtocolAnalyzer + SessionReplay](#pattern-8-protocolanalyzer--sessionreplay)
9. [Pattern 9: Pre-Build Validation Workflow](#pattern-9-pre-build-validation-workflow)
10. [Pattern 10: Complete Architecture Review](#pattern-10-complete-architecture-review)

---

## Pattern 1: ProtocolAnalyzer + VersionGuard

**Use Case:** Validate protocol library versions before implementation

**Why:** Prevent version incompatibility issues (like Socket.IO v4/v3 mismatch)

**Code:**

```python
from versionguard import VersionGuard
from protocolanalyzer import ProtocolAnalyzer

# Initialize tools
vg = VersionGuard()
pa = ProtocolAnalyzer()

# Analyze project
result = pa.analyze("./project")

# Check versions for each detected protocol
for proto in result.detected_protocols:
    if proto.name == "socket.io":
        # Check Socket.IO version compatibility
        check = vg.check_compatibility(
            frontend={"package": "socket.io-client", "min_version": "4.0.0"},
            backend={"package": "python-socketio", "min_version": "5.0.0"}
        )
        
        print(f"Socket.IO Compatibility: {check.status}")
        if check.status != "COMPATIBLE":
            print(f"  Issue: {check.message}")
            print(f"  Fix: {check.recommendation}")
            
    elif proto.name == "grpc":
        check = vg.check_compatibility(
            frontend={"package": "@grpc/grpc-js", "min_version": "1.0.0"},
            backend={"package": "grpcio", "min_version": "1.40.0"}
        )
        print(f"gRPC Compatibility: {check.status}")
```

**Result:** Version issues caught before implementation begins

---

## Pattern 2: ProtocolAnalyzer + BuildEnvValidator

**Use Case:** Ensure build environment has protocol dependencies

**Why:** Catch missing tools (protoc, mosquitto) before build failures

**Code:**

```python
from buildenvvalidator import BuildEnvValidator
from protocolanalyzer import ProtocolAnalyzer

# Initialize tools
bev = BuildEnvValidator()
pa = ProtocolAnalyzer()

# Analyze project
result = pa.analyze("./mobile-app")

# Protocol-specific dependency mapping
PROTOCOL_REQUIREMENTS = {
    "grpc": {
        "tools": [("protoc", "protobuf compiler")],
        "env_vars": ["PROTOBUF_HOME"],
        "packages": ["grpcio", "protobuf"]
    },
    "mqtt": {
        "tools": [("mosquitto", "MQTT broker")],
        "env_vars": [],
        "packages": ["paho-mqtt"]
    },
    "socket.io": {
        "tools": [],
        "env_vars": [],
        "packages": ["python-socketio", "python-engineio"]
    }
}

# Validate each detected protocol
print("Protocol Environment Check:")
print("=" * 50)

for proto in result.detected_protocols:
    if proto.name in PROTOCOL_REQUIREMENTS:
        reqs = PROTOCOL_REQUIREMENTS[proto.name]
        print(f"\n{proto.name.upper()}:")
        
        # Check tools
        for tool, desc in reqs["tools"]:
            status = bev.check_tool(tool, desc)
            icon = "[OK]" if status.found else "[X]"
            print(f"  {icon} {tool}: {status.message}")
            
        # Check env vars
        for var in reqs["env_vars"]:
            status = bev.check_env(var)
            icon = "[OK]" if status.found else "[X]"
            print(f"  {icon} ${var}: {status.message}")
```

**Result:** All protocol dependencies validated before build attempt

---

## Pattern 3: ProtocolAnalyzer + SynapseLink

**Use Case:** Share protocol analysis with team

**Why:** Keep team informed about architecture decisions

**Code:**

```python
from synapselink import quick_send
from protocolanalyzer import ProtocolAnalyzer

# Analyze project
pa = ProtocolAnalyzer()
result = pa.analyze("./new-feature-branch")

# Build message
detected = ', '.join([p.name for p in result.detected_protocols]) or "None"
top_rec = result.recommendations[0]
warning_count = len(result.warnings)

# Create detailed message
message = f"""Protocol Analysis Complete

Project: ./new-feature-branch
Architecture: {result.architecture_type}
Complexity: {result.complexity_total:.1f}

Detected Protocols: {detected}

Recommendation: {top_rec.protocol}
  Score: {top_rec.score:.0f}/100
  Migration: {top_rec.migration_complexity}
  Time: {top_rec.estimated_time}

Warnings: {warning_count}"""

if result.warnings:
    message += "\n\nWarnings:"
    for w in result.warnings:
        message += f"\n  [!] {w}"

# Send to team
quick_send(
    "FORGE,IRIS",  # Reviewers
    "Protocol Analysis: New Feature",
    message,
    priority="NORMAL"
)

print("[OK] Analysis shared with team via SynapseLink")
```

**Result:** Team automatically notified of protocol decisions

---

## Pattern 4: ProtocolAnalyzer + AgentHandoff

**Use Case:** Include protocol context in agent handoffs

**Why:** New agent has full protocol understanding from start

**Code:**

```python
from agenthandoff import AgentHandoff
from protocolanalyzer import ProtocolAnalyzer

# Initialize
handoff = AgentHandoff()
pa = ProtocolAnalyzer()

# Analyze current state
result = pa.analyze("./project")

# Create comprehensive handoff
handoff_id = handoff.create_handoff(
    target="IRIS",
    title="BCH Mobile Protocol Investigation",
    context={
        "protocol_analysis": pa.to_json(result),
        "detected_protocols": [p.name for p in result.detected_protocols],
        "architecture": result.architecture_type,
        "complexity": result.complexity_total,
        "recommended_protocol": result.recommendations[0].protocol,
        "recommendation_score": result.recommendations[0].score,
        "warnings": result.warnings,
        "migration_info": pa.get_migration_guide(
            result.detected_protocols[0].name if result.detected_protocols else "http_rest",
            result.recommendations[0].protocol.lower().replace('/', '_').replace(' ', '_')
        ) if result.detected_protocols else None
    },
    summary=f"Project uses {', '.join([p.name for p in result.detected_protocols]) or 'no protocols'}. "
            f"Architecture: {result.architecture_type}. "
            f"Recommendation: {result.recommendations[0].protocol} ({result.recommendations[0].score:.0f}/100). "
            f"Warnings: {len(result.warnings)}."
)

print(f"[OK] Handoff created: {handoff_id}")
print(f"[OK] Protocol context included for IRIS")
```

**Result:** Seamless context transfer with full protocol understanding

---

## Pattern 5: ProtocolAnalyzer + PostMortem

**Use Case:** Analyze protocol issues after session failures

**Why:** Learn from communication problems, improve future decisions

**Code:**

```python
from postmortem import PostMortem
from protocolanalyzer import ProtocolAnalyzer

# Initialize for post-failure analysis
pm = PostMortem()
pa = ProtocolAnalyzer()

# Analyze the problematic project
result = pa.analyze("./failed-project")

# Identify protocol-related issues
protocol_issues = []

# Check warnings
for warning in result.warnings:
    protocol_issues.append({
        "type": "warning",
        "message": warning,
        "severity": "MEDIUM"
    })

# Check for complexity issues
if result.complexity_total > 50:
    protocol_issues.append({
        "type": "complexity",
        "message": f"High protocol complexity: {result.complexity_total:.1f}",
        "severity": "HIGH"
    })

# Check for mixed protocols
proto_categories = {}
for p in result.detected_protocols:
    cat = pa.compare_protocols([p.name]).get(p.name, {}).get('category', 'unknown')
    proto_categories.setdefault(cat, []).append(p.name)

if 'realtime' in proto_categories and len(proto_categories['realtime']) > 1:
    protocol_issues.append({
        "type": "mixed_protocols",
        "message": f"Multiple realtime protocols: {proto_categories['realtime']}",
        "severity": "MEDIUM"
    })

# Add to post-mortem
pm.add_finding(
    category="protocol_analysis",
    description=f"Detected protocols: {[p.name for p in result.detected_protocols]}",
    severity="INFO",
    details={
        "architecture": result.architecture_type,
        "complexity": result.complexity_total,
        "issues": protocol_issues,
        "recommendations": [
            {
                "protocol": r.protocol,
                "score": r.score,
                "rationale": r.rationale
            }
            for r in result.recommendations[:3]
        ]
    }
)

# Generate learnings
if protocol_issues:
    pm.add_recommendation(
        "protocol_choice",
        f"Consider switching to {result.recommendations[0].protocol} "
        f"(complexity reduction, score: {result.recommendations[0].score:.0f}/100)"
    )

pm.save("./postmortem_report.md")
print("[OK] Protocol analysis added to post-mortem")
```

**Result:** Protocol issues documented for learning

---

## Pattern 6: ProtocolAnalyzer + ContextSynth

**Use Case:** Summarize protocol decisions for context compression

**Why:** Preserve critical protocol info in compressed context

**Code:**

```python
from contextsynth import ContextSynth
from protocolanalyzer import ProtocolAnalyzer

# Initialize
cs = ContextSynth()
pa = ProtocolAnalyzer()

# Analyze
result = pa.analyze("./project")

# Create key facts for context preservation
protocol_facts = [
    f"Architecture: {result.architecture_type}",
    f"Protocols: {', '.join([p.name for p in result.detected_protocols]) or 'None'}",
    f"Complexity: {result.complexity_total:.1f}",
    f"Recommendation: {result.recommendations[0].protocol}",
]

if result.warnings:
    protocol_facts.append(f"Warnings: {'; '.join(result.warnings)}")

# Add to context synthesis
summary = cs.create_summary(
    title="Protocol Architecture",
    facts=protocol_facts,
    importance="HIGH",  # Protocols are architectural decisions
    category="technical",
    searchable_terms=[p.name for p in result.detected_protocols] + ["protocol", "architecture"]
)

print(f"[OK] Protocol summary created: {summary.id}")
print(f"Key facts: {len(protocol_facts)}")
```

**Result:** Protocol decisions preserved in compressed context

---

## Pattern 7: ProtocolAnalyzer + TeamCoherenceMonitor

**Use Case:** Track protocol analysis as part of team coordination

**Why:** Ensure all agents have consistent protocol understanding

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
from protocolanalyzer import ProtocolAnalyzer

# Initialize
tcm = TeamCoherenceMonitor()
pa = ProtocolAnalyzer()

# Analyze
result = pa.analyze("./shared-project")

# Log protocol decision as shared fact
tcm.log_fact(
    category="architecture",
    fact_type="protocol_decision",
    content={
        "detected_protocols": [p.name for p in result.detected_protocols],
        "recommended": result.recommendations[0].protocol,
        "score": result.recommendations[0].score,
        "complexity": result.complexity_total
    },
    importance=0.9  # High importance for architecture decisions
)

# Check if team is aligned on protocol choice
aligned_agents = tcm.check_alignment(
    fact_type="protocol_decision",
    expected_value=result.recommendations[0].protocol
)

if len(aligned_agents) < 3:
    print("[!] Team may not be aligned on protocol choice")
    tcm.broadcast_fact(
        "protocol_decision",
        f"Recommended protocol: {result.recommendations[0].protocol}"
    )
```

**Result:** Team coherence maintained on protocol decisions

---

## Pattern 8: ProtocolAnalyzer + SessionReplay

**Use Case:** Record protocol decisions for debugging

**Why:** Replay protocol analysis decisions when issues arise

**Code:**

```python
from sessionreplay import SessionReplay
from protocolanalyzer import ProtocolAnalyzer

# Initialize
replay = SessionReplay()
pa = ProtocolAnalyzer()

# Start session
session_id = replay.start_session("ATLAS", task="Protocol Selection")

# Log input
replay.log_input(session_id, "Analyzing ./project for realtime requirement")

# Analyze
result = pa.analyze("./project", requirement="realtime")

# Log decision process
replay.log_output(session_id, f"Detected: {[p.name for p in result.detected_protocols]}")
replay.log_output(session_id, f"Recommendations: {[(r.protocol, r.score) for r in result.recommendations[:3]]}")

# Log final decision
chosen_protocol = result.recommendations[0].protocol
replay.log_decision(
    session_id,
    decision_type="protocol_selection",
    choice=chosen_protocol,
    rationale=result.recommendations[0].rationale,
    alternatives=[r.protocol for r in result.recommendations[1:3]]
)

# Complete session
replay.end_session(session_id, status="COMPLETED")

print(f"[OK] Protocol selection recorded in session {session_id}")
```

**Result:** Full protocol decision audit trail

---

## Pattern 9: Pre-Build Validation Workflow

**Use Case:** Complete pre-build check for protocol readiness

**Why:** Catch all protocol issues before build attempt

**Code:**

```python
#!/usr/bin/env python3
"""Complete pre-build protocol validation."""

from protocolanalyzer import ProtocolAnalyzer

def validate_protocols(project_path: str) -> dict:
    """
    Complete protocol validation for pre-build check.
    
    Returns dict with:
        - ready: bool
        - issues: list of issues
        - recommendations: list of recommendations
    """
    pa = ProtocolAnalyzer()
    result = pa.analyze(project_path)
    
    issues = []
    recommendations = []
    
    # Check 1: Warnings
    issues.extend([{"type": "warning", "message": w} for w in result.warnings])
    
    # Check 2: High complexity
    if result.complexity_total > 60:
        issues.append({
            "type": "complexity",
            "message": f"High protocol complexity: {result.complexity_total:.1f}/100"
        })
        recommendations.append(f"Consider simplifying to {result.recommendations[0].protocol}")
    
    # Check 3: Multiple realtime protocols
    realtime_protos = []
    for p in result.detected_protocols:
        comparison = pa.compare_protocols([p.name])
        if p.name in comparison and comparison[p.name].get('category') == 'realtime':
            realtime_protos.append(p.name)
    
    if len(realtime_protos) > 1:
        issues.append({
            "type": "mixed_realtime",
            "message": f"Multiple realtime protocols: {realtime_protos}"
        })
        recommendations.append("Consolidate to single realtime protocol")
    
    # Check 4: Unknown architecture
    if result.architecture_type == "unknown":
        issues.append({
            "type": "architecture",
            "message": "Could not determine architecture type"
        })
    
    # Determine readiness
    critical_issues = [i for i in issues if i["type"] in ["warning", "complexity"]]
    ready = len(critical_issues) == 0
    
    return {
        "ready": ready,
        "architecture": result.architecture_type,
        "complexity": result.complexity_total,
        "detected": [p.name for p in result.detected_protocols],
        "issues": issues,
        "recommendations": recommendations,
        "top_recommendation": {
            "protocol": result.recommendations[0].protocol,
            "score": result.recommendations[0].score
        }
    }

# Usage
if __name__ == "__main__":
    import sys
    import json
    
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Validating protocols in: {project}")
    print("=" * 50)
    
    validation = validate_protocols(project)
    
    status = "[OK] READY" if validation["ready"] else "[X] NOT READY"
    print(f"\nStatus: {status}")
    print(f"Architecture: {validation['architecture']}")
    print(f"Complexity: {validation['complexity']:.1f}")
    print(f"Detected: {', '.join(validation['detected']) or 'None'}")
    
    if validation["issues"]:
        print("\nIssues:")
        for issue in validation["issues"]:
            print(f"  [{issue['type'].upper()}] {issue['message']}")
    
    if validation["recommendations"]:
        print("\nRecommendations:")
        for rec in validation["recommendations"]:
            print(f"  - {rec}")
    
    print(f"\nTop Recommendation: {validation['top_recommendation']['protocol']} "
          f"(score: {validation['top_recommendation']['score']:.0f}/100)")
```

**Result:** Complete protocol readiness assessment

---

## Pattern 10: Complete Architecture Review

**Use Case:** Full architecture review combining multiple tools

**Why:** Production-grade architecture validation

**Code:**

```python
#!/usr/bin/env python3
"""Complete architecture review workflow."""

from protocolanalyzer import ProtocolAnalyzer
# Assuming other Team Brain tools are available
# from versionguard import VersionGuard
# from buildenvvalidator import BuildEnvValidator
# from synapselink import quick_send

def architecture_review(project_path: str) -> dict:
    """
    Complete architecture review.
    
    Integrates:
    - Protocol analysis
    - Version compatibility (placeholder)
    - Build environment (placeholder)
    - Team notification
    """
    results = {
        "project": project_path,
        "protocol_analysis": None,
        "version_check": None,
        "env_check": None,
        "overall_status": "UNKNOWN"
    }
    
    # Step 1: Protocol Analysis
    print("Step 1: Protocol Analysis")
    pa = ProtocolAnalyzer()
    proto_result = pa.analyze(project_path)
    
    results["protocol_analysis"] = {
        "architecture": proto_result.architecture_type,
        "complexity": proto_result.complexity_total,
        "detected": [p.name for p in proto_result.detected_protocols],
        "recommendation": proto_result.recommendations[0].protocol,
        "warnings": proto_result.warnings
    }
    
    print(f"  Architecture: {proto_result.architecture_type}")
    print(f"  Protocols: {[p.name for p in proto_result.detected_protocols]}")
    print(f"  Recommendation: {proto_result.recommendations[0].protocol}")
    
    # Step 2: Version Check (placeholder)
    print("\nStep 2: Version Compatibility")
    # In real integration:
    # vg = VersionGuard()
    # version_result = vg.check_project(project_path)
    results["version_check"] = {"status": "SKIPPED", "message": "VersionGuard not integrated"}
    print("  [SKIP] VersionGuard integration pending")
    
    # Step 3: Environment Check (placeholder)
    print("\nStep 3: Build Environment")
    # In real integration:
    # bev = BuildEnvValidator()
    # env_result = bev.validate(project_path)
    results["env_check"] = {"status": "SKIPPED", "message": "BuildEnvValidator not integrated"}
    print("  [SKIP] BuildEnvValidator integration pending")
    
    # Step 4: Determine Overall Status
    print("\nStep 4: Overall Assessment")
    
    issues = []
    if proto_result.warnings:
        issues.extend(proto_result.warnings)
    if proto_result.complexity_total > 60:
        issues.append(f"High complexity: {proto_result.complexity_total:.1f}")
    
    if len(issues) == 0:
        results["overall_status"] = "GOOD"
        print("  [OK] Architecture looks good!")
    elif len(issues) <= 2:
        results["overall_status"] = "WARNINGS"
        print(f"  [!] Minor issues: {len(issues)}")
    else:
        results["overall_status"] = "NEEDS_REVIEW"
        print(f"  [X] Multiple issues: {len(issues)}")
    
    # Step 5: Generate Report
    print("\nStep 5: Generating Report")
    report_path = f"{project_path}/ARCHITECTURE_REVIEW.md"
    
    report_content = f"""# Architecture Review Report

**Project:** {project_path}
**Status:** {results['overall_status']}

## Protocol Analysis

- **Architecture:** {proto_result.architecture_type}
- **Complexity:** {proto_result.complexity_total:.1f}
- **Detected Protocols:** {', '.join([p.name for p in proto_result.detected_protocols]) or 'None'}
- **Recommendation:** {proto_result.recommendations[0].protocol} (score: {proto_result.recommendations[0].score:.0f}/100)

### Warnings
{chr(10).join(['- ' + w for w in proto_result.warnings]) if proto_result.warnings else 'None'}

### All Recommendations
{''.join([f'''
#### {i+1}. {r.protocol} (Score: {r.score:.0f}/100)
- Migration: {r.migration_complexity}
- Time: {r.estimated_time}
- Rationale: {', '.join(r.rationale)}
''' for i, r in enumerate(proto_result.recommendations[:3])])}

---
*Generated by ProtocolAnalyzer + Team Brain*
"""
    
    try:
        with open(report_path, 'w') as f:
            f.write(report_content)
        print(f"  [OK] Report saved: {report_path}")
    except Exception as e:
        print(f"  [X] Could not save report: {e}")
    
    return results

# Usage
if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print("=" * 60)
    print("ARCHITECTURE REVIEW")
    print("=" * 60)
    
    results = architecture_review(project)
    
    print("\n" + "=" * 60)
    print(f"FINAL STATUS: {results['overall_status']}")
    print("=" * 60)
```

**Result:** Complete architecture review with report generation

---

## 📊 RECOMMENDED INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✓ VersionGuard - Version compatibility
2. ✓ BuildEnvValidator - Environment checks
3. ✓ SynapseLink - Team notifications

**Week 2 (Productivity):**
4. ☐ AgentHandoff - Context transfer
5. ☐ PostMortem - Learning from failures
6. ☐ ContextSynth - Context compression

**Week 3 (Advanced):**
7. ☐ TeamCoherenceMonitor - Team alignment
8. ☐ SessionReplay - Decision audit
9. ☐ Full architecture review workflow

---

## 🔧 TROUBLESHOOTING INTEGRATIONS

**Import Errors:**

```python
# Ensure all tools are in Python path
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "OneDrive/Documents/AutoProjects"))

# Then import
from protocolanalyzer import ProtocolAnalyzer
```

**Version Conflicts:**

```bash
# Check versions
python -c "from protocolanalyzer import ProtocolAnalyzer; print('OK')"

# Update if needed
cd AutoProjects/ProtocolAnalyzer
git pull origin main
```

**Missing Dependencies:**

```bash
# ProtocolAnalyzer has ZERO dependencies
# If other tools need packages:
pip install -r requirements.txt
```

---

**Last Updated:** January 25, 2026  
**Maintained By:** ATLAS (Team Brain)
