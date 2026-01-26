#!/usr/bin/env python3
"""
ProtocolAnalyzer - Compare protocol options and recommend simplest solution

A smart protocol analysis tool that scans your project, identifies communication
protocol usage (WebSocket, Socket.IO, HTTP, gRPC, REST, GraphQL, etc.), and
recommends the simplest solution based on your existing architecture.

Problem Solved:
During BCH development, hours were wasted on Socket.IO v4/v5 incompatibility
when plain WebSocket would have been simpler. This tool prevents such issues
by analyzing existing patterns and recommending the path of least resistance.

Features:
- Protocol detection: Scan project for protocol usage patterns
- Complexity scoring: Calculate complexity based on LOC, dependencies, risk
- Architecture analysis: Identify existing patterns (client/server, polling)
- Recommendation engine: Suggest match existing vs. add new protocol
- Pros/cons generator: Detailed comparison for each option
- Migration guide: Steps to switch from one protocol to another

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Version: 1.0
Date: January 25, 2026
License: MIT
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime
from collections import defaultdict


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ProtocolDetection:
    """Represents a detected protocol in the codebase."""
    protocol: str
    file_path: str
    line_number: int
    pattern_matched: str
    confidence: float  # 0.0 to 1.0
    context: str  # Code snippet around detection


@dataclass
class ProtocolInfo:
    """Information about a communication protocol."""
    name: str
    category: str  # realtime, request-response, streaming, rpc
    complexity_base: int  # Base complexity score (1-10)
    dependencies: List[str]
    pros: List[str]
    cons: List[str]
    typical_use_cases: List[str]
    compatibility_notes: Dict[str, str]


@dataclass
class ProjectProtocol:
    """A protocol detected in the project."""
    name: str
    detections: List[ProtocolDetection]
    total_lines: int
    file_count: int
    complexity_score: float
    is_client: bool
    is_server: bool


@dataclass
class ProtocolRecommendation:
    """A protocol recommendation with rationale."""
    protocol: str
    score: float  # 0-100, higher is better recommendation
    rationale: List[str]
    pros: List[str]
    cons: List[str]
    migration_complexity: str  # LOW, MEDIUM, HIGH
    estimated_time: str


@dataclass
class AnalysisResult:
    """Complete analysis result for a project."""
    project_path: str
    timestamp: str
    detected_protocols: List[ProjectProtocol]
    architecture_type: str
    complexity_total: float
    recommendations: List[ProtocolRecommendation]
    summary: str
    warnings: List[str]


# ============================================================================
# PROTOCOL DATABASE
# ============================================================================

PROTOCOLS_DB: Dict[str, ProtocolInfo] = {
    "websocket": ProtocolInfo(
        name="WebSocket",
        category="realtime",
        complexity_base=3,
        dependencies=["websockets", "ws", "websocket-client"],
        pros=[
            "Full-duplex communication",
            "Low overhead after handshake",
            "Standardized (RFC 6455)",
            "Wide browser support",
            "Simple API"
        ],
        cons=[
            "No automatic reconnection",
            "No built-in message acknowledgment",
            "Manual room/namespace management"
        ],
        typical_use_cases=[
            "Real-time chat",
            "Live updates",
            "Gaming",
            "Streaming data"
        ],
        compatibility_notes={
            "browser": "Native support in all modern browsers",
            "python": "websockets, websocket-client libraries",
            "nodejs": "ws, native WebSocket in browsers"
        }
    ),
    "socket.io": ProtocolInfo(
        name="Socket.IO",
        category="realtime",
        complexity_base=6,
        dependencies=["socket.io", "socket.io-client", "python-socketio", "socketio"],
        pros=[
            "Automatic reconnection",
            "Room/namespace support",
            "Binary support",
            "Fallback to HTTP long-polling",
            "Event-based API"
        ],
        cons=[
            "Higher overhead than WebSocket",
            "Version compatibility issues (v2/v3/v4)",
            "Requires matching client/server versions",
            "Not standard protocol"
        ],
        typical_use_cases=[
            "Complex real-time apps",
            "Chat with rooms",
            "Collaborative editing",
            "Real-time dashboards"
        ],
        compatibility_notes={
            "browser": "Requires socket.io-client library",
            "python": "python-socketio (note version compatibility)",
            "nodejs": "socket.io server, socket.io-client for client",
            "warning": "v4 client requires v4 server - version mismatch causes connection failures"
        }
    ),
    "http_rest": ProtocolInfo(
        name="HTTP/REST",
        category="request-response",
        complexity_base=2,
        dependencies=["requests", "httpx", "aiohttp", "fetch", "axios"],
        pros=[
            "Universal support",
            "Stateless and cacheable",
            "Simple to debug",
            "Works through proxies/firewalls",
            "Well-understood patterns"
        ],
        cons=[
            "No server push (without polling)",
            "Higher latency for real-time",
            "Connection overhead per request"
        ],
        typical_use_cases=[
            "CRUD APIs",
            "Microservices",
            "Public APIs",
            "Traditional web apps"
        ],
        compatibility_notes={
            "browser": "Native fetch API",
            "python": "requests, httpx, aiohttp",
            "nodejs": "fetch, axios"
        }
    ),
    "http_polling": ProtocolInfo(
        name="HTTP Long-Polling",
        category="request-response",
        complexity_base=4,
        dependencies=["requests", "httpx", "aiohttp"],
        pros=[
            "Works everywhere HTTP works",
            "No WebSocket support needed",
            "Simple server implementation"
        ],
        cons=[
            "Higher server load",
            "Not truly real-time",
            "Resource intensive for many clients"
        ],
        typical_use_cases=[
            "Legacy browser support",
            "Firewall-restricted environments",
            "Simple notification systems"
        ],
        compatibility_notes={
            "browser": "Works with any HTTP client",
            "python": "Standard HTTP libraries",
            "nodejs": "Standard HTTP libraries"
        }
    ),
    "grpc": ProtocolInfo(
        name="gRPC",
        category="rpc",
        complexity_base=7,
        dependencies=["grpcio", "grpc", "protobuf", "@grpc/grpc-js"],
        pros=[
            "High performance (HTTP/2)",
            "Strongly typed with protobuf",
            "Bidirectional streaming",
            "Code generation"
        ],
        cons=[
            "Browser support limited (grpc-web)",
            "Requires protobuf knowledge",
            "More complex setup",
            "Binary protocol harder to debug"
        ],
        typical_use_cases=[
            "Microservices communication",
            "High-performance APIs",
            "Mobile backends",
            "Service mesh"
        ],
        compatibility_notes={
            "browser": "Requires grpc-web proxy",
            "python": "grpcio library",
            "nodejs": "@grpc/grpc-js"
        }
    ),
    "graphql": ProtocolInfo(
        name="GraphQL",
        category="request-response",
        complexity_base=5,
        dependencies=["graphql", "graphene", "apollo", "strawberry", "@apollo/client"],
        pros=[
            "Flexible queries",
            "No over-fetching",
            "Strong typing",
            "Introspection",
            "Single endpoint"
        ],
        cons=[
            "Learning curve",
            "Complex caching",
            "N+1 query problem",
            "More server complexity"
        ],
        typical_use_cases=[
            "Complex data relationships",
            "Mobile apps (bandwidth optimization)",
            "Evolving APIs",
            "Frontend-driven development"
        ],
        compatibility_notes={
            "browser": "Apollo Client, urql",
            "python": "graphene, strawberry",
            "nodejs": "apollo-server"
        }
    ),
    "sse": ProtocolInfo(
        name="Server-Sent Events (SSE)",
        category="streaming",
        complexity_base=2,
        dependencies=["aiohttp", "flask", "fastapi"],
        pros=[
            "Simple one-way streaming",
            "Built on HTTP",
            "Automatic reconnection",
            "Native browser support"
        ],
        cons=[
            "One-way only (server to client)",
            "Text-based only",
            "Limited browser connections"
        ],
        typical_use_cases=[
            "News feeds",
            "Stock tickers",
            "Progress updates",
            "Notifications"
        ],
        compatibility_notes={
            "browser": "Native EventSource API",
            "python": "Built into web frameworks",
            "nodejs": "Built-in or libraries"
        }
    ),
    "mqtt": ProtocolInfo(
        name="MQTT",
        category="realtime",
        complexity_base=5,
        dependencies=["paho-mqtt", "mqtt", "mosquitto"],
        pros=[
            "Very lightweight",
            "Publish/subscribe pattern",
            "QoS levels",
            "Great for IoT"
        ],
        cons=[
            "Requires broker",
            "Not browser-native",
            "Different paradigm"
        ],
        typical_use_cases=[
            "IoT devices",
            "Sensor data",
            "Home automation",
            "Low-bandwidth environments"
        ],
        compatibility_notes={
            "browser": "Requires MQTT over WebSocket",
            "python": "paho-mqtt",
            "nodejs": "mqtt.js"
        }
    )
}


# ============================================================================
# DETECTION PATTERNS
# ============================================================================

DETECTION_PATTERNS: Dict[str, List[Tuple[str, float]]] = {
    "websocket": [
        (r"new\s+WebSocket\s*\(", 0.95),
        (r"websocket\.connect", 0.9),
        (r"from\s+websockets\s+import", 0.95),
        (r"import\s+websocket", 0.9),
        (r"ws://|wss://", 0.8),
        (r"WebSocketClient", 0.85),
        (r"websocket\.WebSocketApp", 0.95),
        (r"\.onmessage\s*=", 0.7),
        (r"\.onopen\s*=", 0.7),
        (r"socket\.send\(", 0.6),
    ],
    "socket.io": [
        (r"import\s+socketio", 0.95),
        (r"from\s+socketio\s+import", 0.95),
        (r"require\(['\"]socket\.io['\"]", 0.95),
        (r"require\(['\"]socket\.io-client['\"]", 0.95),
        (r"io\s*\(\s*['\"]http", 0.85),
        (r"\.emit\s*\(", 0.6),
        (r"\.on\s*\(['\"]connect", 0.8),
        (r"socketio\.AsyncServer", 0.95),
        (r"socketio\.Server", 0.95),
        (r"@sio\.", 0.9),
    ],
    "http_rest": [
        (r"import\s+requests", 0.9),
        (r"from\s+requests\s+import", 0.9),
        (r"import\s+httpx", 0.9),
        (r"fetch\s*\(", 0.7),
        (r"axios\.", 0.85),
        (r"requests\.(get|post|put|delete|patch)", 0.95),
        (r"@app\.(get|post|put|delete|patch)\(", 0.9),
        (r"\.json\(\)", 0.5),
        (r"Content-Type.*application/json", 0.7),
    ],
    "http_polling": [
        (r"setInterval.*fetch", 0.8),
        (r"setTimeout.*request", 0.7),
        (r"poll|polling", 0.6),
        (r"long[-_]?poll", 0.9),
    ],
    "grpc": [
        (r"import\s+grpc", 0.95),
        (r"from\s+grpc\s+import", 0.95),
        (r"grpc\.insecure_channel", 0.95),
        (r"grpc\.secure_channel", 0.95),
        (r"\.proto\b", 0.7),
        (r"protobuf", 0.8),
        (r"@grpc/", 0.95),
        (r"grpc\.ServerCredentials", 0.95),
    ],
    "graphql": [
        (r"import.*graphql", 0.9),
        (r"from\s+graphene\s+import", 0.95),
        (r"from\s+strawberry\s+import", 0.95),
        (r"gql`", 0.9),
        (r"useQuery|useMutation", 0.85),
        (r"ApolloClient", 0.95),
        (r"type\s+Query\s*{", 0.9),
        (r"@strawberry\.", 0.95),
    ],
    "sse": [
        (r"new\s+EventSource", 0.95),
        (r"text/event-stream", 0.95),
        (r"EventSource", 0.8),
        (r"Server-Sent Events", 0.9),
    ],
    "mqtt": [
        (r"import\s+paho", 0.95),
        (r"from\s+paho\s+import", 0.95),
        (r"mqtt\.Client", 0.95),
        (r"mqtt://|mqtts://", 0.9),
        (r"\.subscribe\s*\(", 0.5),
        (r"\.publish\s*\(", 0.5),
    ]
}


# Client vs Server patterns
CLIENT_PATTERNS = [
    r"connect\s*\(",
    r"\.send\s*\(",
    r"\.emit\s*\(",
    r"fetch\s*\(",
    r"axios\.",
    r"new\s+WebSocket",
    r"io\s*\(",
    r"EventSource",
]

SERVER_PATTERNS = [
    r"listen\s*\(",
    r"serve\s*\(",
    r"app\.(get|post|put|delete)",
    r"@app\.",
    r"AsyncServer",
    r"Server\(",
    r"createServer",
    r"bind\s*\(",
]


# ============================================================================
# PROTOCOL DETECTOR
# ============================================================================

class ProtocolDetector:
    """Detects protocols in project files."""
    
    # File extensions to scan
    SCAN_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs'}
    
    # Directories to skip
    SKIP_DIRS = {
        'node_modules', '__pycache__', '.git', '.venv', 'venv',
        'env', '.env', 'dist', 'build', '.cache', 'coverage',
        '.pytest_cache', '.mypy_cache', 'target', 'vendor'
    }
    
    def __init__(self):
        """Initialize the detector."""
        self.detections: List[ProtocolDetection] = []
        self.file_protocol_lines: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
    def scan_project(self, project_path: Path) -> List[ProtocolDetection]:
        """Scan a project directory for protocol patterns."""
        self.detections = []
        self.file_protocol_lines = defaultdict(lambda: defaultdict(int))
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")
            
        if project_path.is_file():
            self._scan_file(project_path)
        else:
            self._scan_directory(project_path)
            
        return self.detections
    
    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan a directory."""
        try:
            for entry in directory.iterdir():
                if entry.name in self.SKIP_DIRS:
                    continue
                if entry.name.startswith('.'):
                    continue
                    
                if entry.is_dir():
                    self._scan_directory(entry)
                elif entry.is_file() and entry.suffix in self.SCAN_EXTENSIONS:
                    self._scan_file(entry)
        except PermissionError:
            pass  # Skip directories we can't access
    
    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for protocol patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return
            
        for protocol, patterns in DETECTION_PATTERNS.items():
            for pattern, confidence in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Get context (2 lines before and after)
                        start = max(0, i - 3)
                        end = min(len(lines), i + 2)
                        context = '\n'.join(lines[start:end])
                        
                        detection = ProtocolDetection(
                            protocol=protocol,
                            file_path=str(file_path),
                            line_number=i,
                            pattern_matched=pattern,
                            confidence=confidence,
                            context=context
                        )
                        self.detections.append(detection)
                        self.file_protocol_lines[str(file_path)][protocol] += 1
    
    def get_protocol_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of detected protocols."""
        summary = defaultdict(lambda: {
            'detections': [],
            'files': set(),
            'total_matches': 0,
            'max_confidence': 0.0,
            'avg_confidence': 0.0,
            'is_client': False,
            'is_server': False
        })
        
        for detection in self.detections:
            proto = detection.protocol
            summary[proto]['detections'].append(detection)
            summary[proto]['files'].add(detection.file_path)
            summary[proto]['total_matches'] += 1
            summary[proto]['max_confidence'] = max(
                summary[proto]['max_confidence'],
                detection.confidence
            )
            
            # Check if client or server
            for pattern in CLIENT_PATTERNS:
                if re.search(pattern, detection.context, re.IGNORECASE):
                    summary[proto]['is_client'] = True
            for pattern in SERVER_PATTERNS:
                if re.search(pattern, detection.context, re.IGNORECASE):
                    summary[proto]['is_server'] = True
        
        # Calculate averages
        for proto in summary:
            if summary[proto]['total_matches'] > 0:
                total_conf = sum(d.confidence for d in summary[proto]['detections'])
                summary[proto]['avg_confidence'] = total_conf / summary[proto]['total_matches']
            summary[proto]['files'] = list(summary[proto]['files'])
        
        return dict(summary)


# ============================================================================
# COMPLEXITY CALCULATOR
# ============================================================================

class ComplexityCalculator:
    """Calculate protocol complexity scores."""
    
    def __init__(self):
        """Initialize the calculator."""
        pass
    
    def calculate_complexity(
        self,
        protocol: str,
        detections: List[ProtocolDetection],
        file_count: int,
        line_count: int
    ) -> float:
        """
        Calculate complexity score for a protocol.
        
        Score = base_complexity * scale_factor * confidence_factor * spread_factor
        
        Returns score from 0-100.
        """
        if protocol not in PROTOCOLS_DB:
            return 50.0  # Unknown protocol gets medium score
            
        info = PROTOCOLS_DB[protocol]
        base = info.complexity_base  # 1-10
        
        # Scale factor based on usage (1.0 to 2.0)
        scale = 1.0 + min(1.0, line_count / 500)
        
        # Confidence factor (0.5 to 1.0)
        if detections:
            avg_conf = sum(d.confidence for d in detections) / len(detections)
            confidence_factor = 0.5 + (avg_conf * 0.5)
        else:
            confidence_factor = 0.5
        
        # Spread factor - more files = higher complexity (1.0 to 1.5)
        spread = 1.0 + min(0.5, file_count / 20)
        
        # Calculate final score (normalize to 0-100)
        score = base * scale * confidence_factor * spread * 10
        
        return min(100.0, max(0.0, score))
    
    def calculate_migration_complexity(
        self,
        from_protocol: str,
        to_protocol: str,
        current_usage: int
    ) -> str:
        """
        Estimate migration complexity between protocols.
        
        Returns: LOW, MEDIUM, or HIGH
        """
        # Same category = easier migration
        if from_protocol in PROTOCOLS_DB and to_protocol in PROTOCOLS_DB:
            from_cat = PROTOCOLS_DB[from_protocol].category
            to_cat = PROTOCOLS_DB[to_protocol].category
            
            if from_cat == to_cat:
                if current_usage < 10:
                    return "LOW"
                elif current_usage < 50:
                    return "MEDIUM"
                else:
                    return "HIGH"
            else:
                # Different category = harder
                if current_usage < 5:
                    return "MEDIUM"
                else:
                    return "HIGH"
        
        return "MEDIUM"
    
    def estimate_migration_time(
        self,
        complexity: str,
        file_count: int
    ) -> str:
        """Estimate time to migrate based on complexity."""
        base_times = {
            "LOW": (0.5, 2),      # 0.5-2 hours
            "MEDIUM": (2, 8),     # 2-8 hours
            "HIGH": (8, 40)       # 8-40 hours (1-5 days)
        }
        
        min_h, max_h = base_times.get(complexity, (2, 8))
        
        # Adjust for file count
        multiplier = 1 + (file_count / 10)
        min_h *= multiplier
        max_h *= multiplier
        
        if max_h < 1:
            return "< 1 hour"
        elif max_h < 4:
            return f"{min_h:.0f}-{max_h:.0f} hours"
        elif max_h < 16:
            return f"{min_h/8:.1f}-{max_h/8:.1f} days"
        else:
            return f"{min_h/40:.1f}-{max_h/40:.1f} weeks"


# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """Generate protocol recommendations."""
    
    def __init__(self):
        """Initialize the engine."""
        self.complexity_calc = ComplexityCalculator()
        
    def generate_recommendations(
        self,
        detected_protocols: Dict[str, Dict],
        requirement: str = "realtime"
    ) -> List[ProtocolRecommendation]:
        """
        Generate protocol recommendations based on detected usage.
        
        Args:
            detected_protocols: Summary from ProtocolDetector
            requirement: realtime, request-response, streaming, or rpc
            
        Returns:
            List of recommendations sorted by score (best first)
        """
        recommendations = []
        
        # Get existing protocols
        existing = set(detected_protocols.keys())
        
        # Score each potential protocol
        for protocol, info in PROTOCOLS_DB.items():
            score, rationale = self._calculate_recommendation_score(
                protocol, info, existing, detected_protocols, requirement
            )
            
            # Calculate migration complexity if switching
            if existing and protocol not in existing:
                main_existing = max(
                    existing,
                    key=lambda p: detected_protocols.get(p, {}).get('total_matches', 0)
                )
                migration = self.complexity_calc.calculate_migration_complexity(
                    main_existing,
                    protocol,
                    detected_protocols.get(main_existing, {}).get('total_matches', 0)
                )
                file_count = len(detected_protocols.get(main_existing, {}).get('files', []))
                time_est = self.complexity_calc.estimate_migration_time(migration, file_count)
            else:
                migration = "LOW" if protocol in existing else "MEDIUM"
                time_est = "< 1 hour" if protocol in existing else "2-4 hours"
            
            rec = ProtocolRecommendation(
                protocol=info.name,
                score=score,
                rationale=rationale,
                pros=info.pros.copy(),
                cons=info.cons.copy(),
                migration_complexity=migration,
                estimated_time=time_est
            )
            recommendations.append(rec)
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda r: r.score, reverse=True)
        
        return recommendations
    
    def _calculate_recommendation_score(
        self,
        protocol: str,
        info: ProtocolInfo,
        existing: Set[str],
        detected: Dict,
        requirement: str
    ) -> Tuple[float, List[str]]:
        """Calculate recommendation score and rationale."""
        score = 50.0  # Base score
        rationale = []
        
        # Bonus for matching requirement category
        if info.category == requirement:
            score += 20
            rationale.append(f"Matches requirement: {requirement}")
        elif requirement == "realtime" and info.category in ["realtime", "streaming"]:
            score += 15
            rationale.append(f"Good for real-time communication")
        
        # Bonus for already being used (consistency)
        if protocol in existing:
            usage = detected.get(protocol, {}).get('total_matches', 0)
            score += min(25, usage * 2)  # Up to 25 points
            rationale.append(f"Already in use ({usage} references found)")
        
        # Penalty for complexity
        complexity_penalty = (info.complexity_base - 1) * 3  # 0-27 penalty
        score -= complexity_penalty
        if complexity_penalty > 15:
            rationale.append(f"Higher complexity (base: {info.complexity_base}/10)")
        
        # Bonus for same category as existing
        for existing_proto in existing:
            if existing_proto in PROTOCOLS_DB:
                if PROTOCOLS_DB[existing_proto].category == info.category:
                    score += 10
                    rationale.append(f"Same category as existing {existing_proto}")
                    break
        
        # Bonus for simplicity (fewer dependencies typically = simpler)
        if info.complexity_base <= 3:
            score += 10
            rationale.append("Simple, low-overhead protocol")
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        
        if not rationale:
            rationale.append("Standard option")
        
        return score, rationale


# ============================================================================
# MAIN ANALYZER
# ============================================================================

class ProtocolAnalyzer:
    """
    Main protocol analyzer class.
    
    Analyzes a project's communication protocol usage and provides
    recommendations for the simplest approach.
    
    Example:
        >>> analyzer = ProtocolAnalyzer()
        >>> result = analyzer.analyze("/path/to/project")
        >>> print(result.summary)
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the analyzer.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.detector = ProtocolDetector()
        self.complexity_calc = ComplexityCalculator()
        self.recommender = RecommendationEngine()
        
    def analyze(
        self,
        project_path: str,
        requirement: str = "auto"
    ) -> AnalysisResult:
        """
        Analyze a project for protocol usage.
        
        Args:
            project_path: Path to project directory
            requirement: Type of communication needed (realtime, request-response,
                        streaming, rpc, or auto for auto-detect)
                        
        Returns:
            AnalysisResult with full analysis
        """
        path = Path(project_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")
        
        # Detect protocols
        detections = self.detector.scan_project(path)
        summary = self.detector.get_protocol_summary()
        
        # Build ProjectProtocol objects
        detected_protocols = []
        for proto, data in summary.items():
            proj_proto = ProjectProtocol(
                name=proto,
                detections=data['detections'],
                total_lines=data['total_matches'],
                file_count=len(data['files']),
                complexity_score=self.complexity_calc.calculate_complexity(
                    proto,
                    data['detections'],
                    len(data['files']),
                    data['total_matches']
                ),
                is_client=data['is_client'],
                is_server=data['is_server']
            )
            detected_protocols.append(proj_proto)
        
        # Determine architecture type
        architecture = self._determine_architecture(detected_protocols)
        
        # Auto-detect requirement if needed
        if requirement == "auto":
            requirement = self._auto_detect_requirement(detected_protocols)
        
        # Generate recommendations
        recommendations = self.recommender.generate_recommendations(
            summary,
            requirement
        )
        
        # Calculate total complexity
        total_complexity = sum(p.complexity_score for p in detected_protocols)
        
        # Generate warnings
        warnings = self._generate_warnings(detected_protocols, summary)
        
        # Generate summary
        summary_text = self._generate_summary(
            detected_protocols,
            recommendations,
            architecture
        )
        
        return AnalysisResult(
            project_path=str(path.absolute()),
            timestamp=datetime.now().isoformat(),
            detected_protocols=detected_protocols,
            architecture_type=architecture,
            complexity_total=total_complexity,
            recommendations=recommendations[:5],  # Top 5
            summary=summary_text,
            warnings=warnings
        )
    
    def _determine_architecture(
        self,
        protocols: List[ProjectProtocol]
    ) -> str:
        """Determine the overall architecture type."""
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
    
    def _auto_detect_requirement(
        self,
        protocols: List[ProjectProtocol]
    ) -> str:
        """Auto-detect the communication requirement."""
        categories = defaultdict(int)
        
        for proto in protocols:
            if proto.name in PROTOCOLS_DB:
                cat = PROTOCOLS_DB[proto.name].category
                categories[cat] += proto.total_lines
        
        if categories:
            return max(categories, key=categories.get)
        return "request-response"  # Default
    
    def _generate_warnings(
        self,
        protocols: List[ProjectProtocol],
        summary: Dict
    ) -> List[str]:
        """Generate warnings based on analysis."""
        warnings = []
        
        # Check for Socket.IO version issues
        if "socket.io" in summary:
            warnings.append(
                "Socket.IO detected: Ensure client/server versions match "
                "(v4 client requires v4 server)"
            )
        
        # Check for multiple real-time protocols
        realtime_protos = [
            p for p in protocols
            if p.name in PROTOCOLS_DB and
            PROTOCOLS_DB[p.name].category == "realtime"
        ]
        if len(realtime_protos) > 1:
            names = [p.name for p in realtime_protos]
            warnings.append(
                f"Multiple real-time protocols detected: {', '.join(names)}. "
                "Consider consolidating to reduce complexity."
            )
        
        # Check for high complexity
        high_complexity = [p for p in protocols if p.complexity_score > 50]
        if high_complexity:
            names = [p.name for p in high_complexity]
            warnings.append(
                f"High complexity protocols: {', '.join(names)}. "
                "Review if simpler alternatives exist."
            )
        
        return warnings
    
    def _generate_summary(
        self,
        protocols: List[ProjectProtocol],
        recommendations: List[ProtocolRecommendation],
        architecture: str
    ) -> str:
        """Generate a human-readable summary."""
        if not protocols:
            return (
                "No communication protocols detected. "
                "This project may not yet implement network communication."
            )
        
        proto_names = [p.name for p in protocols]
        top_rec = recommendations[0] if recommendations else None
        
        summary = f"Architecture: {architecture}. "
        summary += f"Detected protocols: {', '.join(proto_names)}. "
        
        if top_rec:
            summary += f"Recommended approach: {top_rec.protocol} (score: {top_rec.score:.0f}/100). "
            if top_rec.rationale:
                summary += f"Rationale: {top_rec.rationale[0]}."
        
        return summary
    
    def compare_protocols(
        self,
        protocols: List[str]
    ) -> Dict[str, Dict]:
        """
        Compare multiple protocols side by side.
        
        Args:
            protocols: List of protocol names to compare
            
        Returns:
            Comparison dict with all protocol info
        """
        comparison = {}
        
        for proto in protocols:
            proto_lower = proto.lower().replace(' ', '_').replace('-', '_')
            
            # Try to find matching protocol
            if proto_lower in PROTOCOLS_DB:
                info = PROTOCOLS_DB[proto_lower]
            elif proto_lower.replace('_', '.') in PROTOCOLS_DB:
                info = PROTOCOLS_DB[proto_lower.replace('_', '.')]
            else:
                # Try partial match
                matches = [k for k in PROTOCOLS_DB if proto_lower in k or k in proto_lower]
                if matches:
                    info = PROTOCOLS_DB[matches[0]]
                else:
                    comparison[proto] = {"error": "Protocol not found in database"}
                    continue
            
            comparison[info.name] = {
                "category": info.category,
                "complexity": info.complexity_base,
                "pros": info.pros,
                "cons": info.cons,
                "use_cases": info.typical_use_cases,
                "compatibility": info.compatibility_notes
            }
        
        return comparison
    
    def get_migration_guide(
        self,
        from_protocol: str,
        to_protocol: str
    ) -> Dict[str, Any]:
        """
        Get a migration guide from one protocol to another.
        
        Args:
            from_protocol: Source protocol name
            to_protocol: Target protocol name
            
        Returns:
            Migration guide with steps and considerations
        """
        from_key = from_protocol.lower().replace(' ', '_').replace('-', '_')
        to_key = to_protocol.lower().replace(' ', '_').replace('-', '_')
        
        # Normalize keys
        if from_key.replace('_', '.') in PROTOCOLS_DB:
            from_key = from_key.replace('_', '.')
        if to_key.replace('_', '.') in PROTOCOLS_DB:
            to_key = to_key.replace('_', '.')
        
        if from_key not in PROTOCOLS_DB:
            return {"error": f"Source protocol not found: {from_protocol}"}
        if to_key not in PROTOCOLS_DB:
            return {"error": f"Target protocol not found: {to_protocol}"}
        
        from_info = PROTOCOLS_DB[from_key]
        to_info = PROTOCOLS_DB[to_key]
        
        # Determine migration difficulty
        same_category = from_info.category == to_info.category
        complexity_diff = to_info.complexity_base - from_info.complexity_base
        
        if same_category:
            difficulty = "MODERATE"
        elif complexity_diff > 3:
            difficulty = "HARD"
        elif complexity_diff < -3:
            difficulty = "EASY"
        else:
            difficulty = "MODERATE"
        
        # Generate steps
        steps = [
            f"1. Review all {from_info.name} usage in codebase",
            f"2. Install {to_info.name} dependencies: {', '.join(to_info.dependencies[:2])}",
            f"3. Create adapter/wrapper for {to_info.name} connections",
            f"4. Migrate connection initialization code",
            f"5. Update event handlers/callbacks",
            f"6. Test all communication paths",
            f"7. Remove {from_info.name} dependencies",
            "8. Update documentation"
        ]
        
        return {
            "from": from_info.name,
            "to": to_info.name,
            "difficulty": difficulty,
            "estimated_time": self.complexity_calc.estimate_migration_time(
                difficulty, 10
            ),
            "steps": steps,
            "considerations": [
                f"Category change: {from_info.category} -> {to_info.category}"
                if not same_category else "Same category - patterns similar",
                f"New pros: {', '.join(to_info.pros[:2])}",
                f"New cons: {', '.join(to_info.cons[:2])}"
            ],
            "breaking_changes": [
                "API differences will require code changes",
                "Configuration format may differ",
                "Error handling patterns may differ"
            ]
        }
    
    def to_json(self, result: AnalysisResult) -> str:
        """Convert analysis result to JSON string."""
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            else:
                return obj
        
        return json.dumps(serialize(result), indent=2)
    
    def to_markdown(self, result: AnalysisResult) -> str:
        """Convert analysis result to Markdown report."""
        lines = []
        
        lines.append("# Protocol Analysis Report")
        lines.append("")
        lines.append(f"**Project:** {result.project_path}")
        lines.append(f"**Analyzed:** {result.timestamp}")
        lines.append(f"**Architecture:** {result.architecture_type}")
        lines.append(f"**Total Complexity:** {result.complexity_total:.1f}")
        lines.append("")
        
        lines.append("## Summary")
        lines.append("")
        lines.append(result.summary)
        lines.append("")
        
        if result.warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in result.warnings:
                lines.append(f"- [!] {warning}")
            lines.append("")
        
        lines.append("## Detected Protocols")
        lines.append("")
        if result.detected_protocols:
            lines.append("| Protocol | Files | References | Complexity | Client | Server |")
            lines.append("|----------|-------|------------|------------|--------|--------|")
            for proto in result.detected_protocols:
                client = "[OK]" if proto.is_client else ""
                server = "[OK]" if proto.is_server else ""
                lines.append(
                    f"| {proto.name} | {proto.file_count} | "
                    f"{proto.total_lines} | {proto.complexity_score:.1f} | "
                    f"{client} | {server} |"
                )
            lines.append("")
        else:
            lines.append("No protocols detected.")
            lines.append("")
        
        lines.append("## Recommendations")
        lines.append("")
        for i, rec in enumerate(result.recommendations[:3], 1):
            lines.append(f"### {i}. {rec.protocol} (Score: {rec.score:.0f}/100)")
            lines.append("")
            lines.append(f"**Migration Complexity:** {rec.migration_complexity}")
            lines.append(f"**Estimated Time:** {rec.estimated_time}")
            lines.append("")
            lines.append("**Rationale:**")
            for r in rec.rationale:
                lines.append(f"- {r}")
            lines.append("")
            lines.append("**Pros:**")
            for p in rec.pros[:3]:
                lines.append(f"- {p}")
            lines.append("")
            lines.append("**Cons:**")
            for c in rec.cons[:3]:
                lines.append(f"- {c}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*Generated by ProtocolAnalyzer v1.0 (Team Brain)*")
        
        return '\n'.join(lines)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='protocolanalyzer',
        description='Compare protocol options and recommend simplest solution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./my-project
  %(prog)s analyze ./my-project --requirement realtime
  %(prog)s analyze ./my-project --output report.md --format markdown
  %(prog)s compare websocket socket.io
  %(prog)s migrate socket.io websocket

Protocol Categories:
  - realtime: WebSocket, Socket.IO, MQTT
  - request-response: HTTP/REST, GraphQL
  - streaming: SSE
  - rpc: gRPC

For more information: https://github.com/DonkRonk17/ProtocolAnalyzer
        """
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a project for protocol usage'
    )
    analyze_parser.add_argument(
        'project_path',
        help='Path to project directory'
    )
    analyze_parser.add_argument(
        '--requirement', '-r',
        choices=['realtime', 'request-response', 'streaming', 'rpc', 'auto'],
        default='auto',
        help='Type of communication needed (default: auto-detect)'
    )
    analyze_parser.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )
    analyze_parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    analyze_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Compare command
    compare_parser = subparsers.add_parser(
        'compare',
        help='Compare multiple protocols side by side'
    )
    compare_parser.add_argument(
        'protocols',
        nargs='+',
        help='Protocols to compare (e.g., websocket socket.io grpc)'
    )
    compare_parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Migrate command
    migrate_parser = subparsers.add_parser(
        'migrate',
        help='Get migration guide between protocols'
    )
    migrate_parser.add_argument(
        'from_protocol',
        help='Source protocol'
    )
    migrate_parser.add_argument(
        'to_protocol',
        help='Target protocol'
    )
    migrate_parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List all known protocols'
    )
    list_parser.add_argument(
        '--category', '-c',
        choices=['realtime', 'request-response', 'streaming', 'rpc', 'all'],
        default='all',
        help='Filter by category'
    )
    
    return parser


def format_comparison(comparison: Dict, format_type: str) -> str:
    """Format comparison output."""
    if format_type == 'json':
        return json.dumps(comparison, indent=2)
    elif format_type == 'markdown':
        lines = ["# Protocol Comparison", ""]
        for name, data in comparison.items():
            if "error" in data:
                lines.append(f"## {name}")
                lines.append(f"Error: {data['error']}")
                continue
            lines.append(f"## {name}")
            lines.append(f"**Category:** {data['category']}")
            lines.append(f"**Complexity:** {data['complexity']}/10")
            lines.append("")
            lines.append("**Pros:**")
            for p in data['pros']:
                lines.append(f"- {p}")
            lines.append("")
            lines.append("**Cons:**")
            for c in data['cons']:
                lines.append(f"- {c}")
            lines.append("")
        return '\n'.join(lines)
    else:
        lines = []
        for name, data in comparison.items():
            lines.append(f"\n=== {name} ===")
            if "error" in data:
                lines.append(f"  Error: {data['error']}")
                continue
            lines.append(f"  Category: {data['category']}")
            lines.append(f"  Complexity: {data['complexity']}/10")
            lines.append(f"  Pros: {', '.join(data['pros'][:3])}")
            lines.append(f"  Cons: {', '.join(data['cons'][:3])}")
        return '\n'.join(lines)


def format_migration(guide: Dict, format_type: str) -> str:
    """Format migration guide output."""
    if format_type == 'json':
        return json.dumps(guide, indent=2)
    elif format_type == 'markdown':
        if "error" in guide:
            return f"Error: {guide['error']}"
        lines = [
            f"# Migration Guide: {guide['from']} -> {guide['to']}",
            "",
            f"**Difficulty:** {guide['difficulty']}",
            f"**Estimated Time:** {guide['estimated_time']}",
            "",
            "## Steps",
            ""
        ]
        for step in guide['steps']:
            lines.append(f"- {step}")
        lines.append("")
        lines.append("## Considerations")
        for c in guide['considerations']:
            lines.append(f"- {c}")
        return '\n'.join(lines)
    else:
        if "error" in guide:
            return f"Error: {guide['error']}"
        lines = [
            f"\nMigration: {guide['from']} -> {guide['to']}",
            f"Difficulty: {guide['difficulty']}",
            f"Estimated Time: {guide['estimated_time']}",
            "",
            "Steps:"
        ]
        for step in guide['steps']:
            lines.append(f"  {step}")
        return '\n'.join(lines)


def main():
    """CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    analyzer = ProtocolAnalyzer(verbose=getattr(args, 'verbose', False))
    
    try:
        if args.command == 'analyze':
            result = analyzer.analyze(args.project_path, args.requirement)
            
            if args.format == 'json':
                output = analyzer.to_json(result)
            elif args.format == 'markdown':
                output = analyzer.to_markdown(result)
            else:
                # Text format
                output = f"""
Protocol Analysis Report
========================
Project: {result.project_path}
Architecture: {result.architecture_type}
Complexity: {result.complexity_total:.1f}

Summary: {result.summary}

Detected Protocols:
"""
                for proto in result.detected_protocols:
                    output += f"  - {proto.name}: {proto.file_count} files, {proto.total_lines} refs, complexity {proto.complexity_score:.1f}\n"
                
                if result.warnings:
                    output += "\nWarnings:\n"
                    for w in result.warnings:
                        output += f"  [!] {w}\n"
                
                output += "\nRecommendations:\n"
                for i, rec in enumerate(result.recommendations[:3], 1):
                    output += f"  {i}. {rec.protocol} (score: {rec.score:.0f}/100)\n"
                    output += f"     Migration: {rec.migration_complexity}, Est: {rec.estimated_time}\n"
            
            if args.output:
                Path(args.output).write_text(output, encoding='utf-8')
                print(f"[OK] Report saved to: {args.output}")
            else:
                print(output)
        
        elif args.command == 'compare':
            comparison = analyzer.compare_protocols(args.protocols)
            output = format_comparison(comparison, args.format)
            print(output)
        
        elif args.command == 'migrate':
            guide = analyzer.get_migration_guide(args.from_protocol, args.to_protocol)
            output = format_migration(guide, args.format)
            print(output)
        
        elif args.command == 'list':
            print("\nKnown Protocols:")
            print("=" * 50)
            for key, info in sorted(PROTOCOLS_DB.items()):
                if args.category == 'all' or info.category == args.category:
                    print(f"\n{info.name}")
                    print(f"  Category: {info.category}")
                    print(f"  Complexity: {info.complexity_base}/10")
                    print(f"  Use cases: {', '.join(info.typical_use_cases[:2])}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"[X] Error: {e}")
        return 1
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
