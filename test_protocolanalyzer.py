#!/usr/bin/env python3
"""
Comprehensive test suite for ProtocolAnalyzer.

Tests cover:
- Protocol detection patterns
- Complexity calculation
- Recommendation engine
- Migration guide generation
- CLI interface
- Edge cases and error handling

Run: python test_protocolanalyzer.py
Or:  pytest test_protocolanalyzer.py -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from protocolanalyzer import (
    ProtocolAnalyzer,
    ProtocolDetector,
    ComplexityCalculator,
    RecommendationEngine,
    ProtocolDetection,
    ProjectProtocol,
    ProtocolRecommendation,
    AnalysisResult,
    PROTOCOLS_DB,
    DETECTION_PATTERNS
)


class TestProtocolDetector(unittest.TestCase):
    """Test protocol detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ProtocolDetector()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test detector initializes correctly."""
        detector = ProtocolDetector()
        self.assertIsNotNone(detector)
        self.assertEqual(len(detector.detections), 0)
        
    def test_detect_websocket(self):
        """Test WebSocket detection."""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("""
import websocket

ws = websocket.WebSocketApp("ws://localhost:8080")
ws.send("Hello")
""")
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        websocket_detections = [d for d in detections if d.protocol == "websocket"]
        self.assertGreater(len(websocket_detections), 0)
        
    def test_detect_socketio(self):
        """Test Socket.IO detection."""
        test_file = Path(self.temp_dir) / "app.py"
        test_file.write_text("""
import socketio

sio = socketio.AsyncServer()

@sio.event
async def connect(sid, environ):
    print(f"Connected: {sid}")
    
sio.emit("message", "Hello")
""")
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        socketio_detections = [d for d in detections if d.protocol == "socket.io"]
        self.assertGreater(len(socketio_detections), 0)
        
    def test_detect_http_rest(self):
        """Test HTTP/REST detection."""
        test_file = Path(self.temp_dir) / "api.py"
        test_file.write_text("""
import requests

response = requests.get("https://api.example.com/data")
data = response.json()

requests.post("https://api.example.com/items", json={"name": "test"})
""")
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        http_detections = [d for d in detections if d.protocol == "http_rest"]
        self.assertGreater(len(http_detections), 0)
        
    def test_detect_grpc(self):
        """Test gRPC detection."""
        test_file = Path(self.temp_dir) / "service.py"
        test_file.write_text("""
import grpc

channel = grpc.insecure_channel('localhost:50051')
stub = MyServiceStub(channel)
""")
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        grpc_detections = [d for d in detections if d.protocol == "grpc"]
        self.assertGreater(len(grpc_detections), 0)
        
    def test_detect_graphql(self):
        """Test GraphQL detection."""
        test_file = Path(self.temp_dir) / "schema.py"
        test_file.write_text("""
from graphene import ObjectType, String, Schema

class Query(ObjectType):
    hello = String(name=String(default_value="World"))
    
    def resolve_hello(root, info, name):
        return f'Hello {name}!'
""")
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        graphql_detections = [d for d in detections if d.protocol == "graphql"]
        self.assertGreater(len(graphql_detections), 0)
        
    def test_detect_sse(self):
        """Test Server-Sent Events detection."""
        test_file = Path(self.temp_dir) / "client.js"
        test_file.write_text("""
const source = new EventSource('/events');
source.onmessage = (event) => {
    console.log(event.data);
};
""")
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        sse_detections = [d for d in detections if d.protocol == "sse"]
        self.assertGreater(len(sse_detections), 0)
        
    def test_detect_multiple_protocols(self):
        """Test detecting multiple protocols in same project."""
        # Create files with different protocols
        (Path(self.temp_dir) / "ws.py").write_text("import websocket\nws = websocket.connect('ws://host')")
        (Path(self.temp_dir) / "api.py").write_text("import requests\nrequests.get('http://api')")
        
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        protocols = set(d.protocol for d in detections)
        self.assertGreater(len(protocols), 1)
        
    def test_skip_node_modules(self):
        """Test that node_modules is skipped."""
        nm_dir = Path(self.temp_dir) / "node_modules" / "some_pkg"
        nm_dir.mkdir(parents=True)
        (nm_dir / "index.js").write_text("import socketio from 'socket.io';")
        
        detections = self.detector.scan_project(Path(self.temp_dir))
        
        # Should not detect anything in node_modules
        nm_detections = [d for d in detections if "node_modules" in d.file_path]
        self.assertEqual(len(nm_detections), 0)
        
    def test_get_protocol_summary(self):
        """Test protocol summary generation."""
        test_file = Path(self.temp_dir) / "app.py"
        test_file.write_text("""
import websocket
ws = websocket.WebSocketApp("ws://host")
ws.send("test")
ws.connect()
""")
        self.detector.scan_project(Path(self.temp_dir))
        summary = self.detector.get_protocol_summary()
        
        self.assertIn("websocket", summary)
        self.assertGreater(summary["websocket"]["total_matches"], 0)
        
    def test_client_server_detection(self):
        """Test client vs server pattern detection."""
        # Client code
        client_file = Path(self.temp_dir) / "client.py"
        client_file.write_text("""
import websocket
ws = websocket.connect('ws://localhost:8080')
ws.send("Hello")
""")
        
        self.detector.scan_project(Path(self.temp_dir))
        summary = self.detector.get_protocol_summary()
        
        if "websocket" in summary:
            self.assertTrue(summary["websocket"]["is_client"])
            
    def test_empty_project(self):
        """Test scanning empty project."""
        detections = self.detector.scan_project(Path(self.temp_dir))
        self.assertEqual(len(detections), 0)
        
    def test_nonexistent_path(self):
        """Test scanning non-existent path."""
        with self.assertRaises(FileNotFoundError):
            self.detector.scan_project(Path("/nonexistent/path/12345"))


class TestComplexityCalculator(unittest.TestCase):
    """Test complexity calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ComplexityCalculator()
        
    def test_initialization(self):
        """Test calculator initializes."""
        calc = ComplexityCalculator()
        self.assertIsNotNone(calc)
        
    def test_websocket_complexity(self):
        """Test WebSocket complexity is low."""
        detections = [
            ProtocolDetection(
                protocol="websocket",
                file_path="test.py",
                line_number=1,
                pattern_matched="import websocket",
                confidence=0.9,
                context="import websocket"
            )
        ]
        
        score = self.calculator.calculate_complexity(
            "websocket", detections, 1, 5
        )
        
        # WebSocket has base complexity 3, should be relatively low
        self.assertLess(score, 50)
        
    def test_grpc_complexity(self):
        """Test gRPC complexity is higher."""
        detections = [
            ProtocolDetection(
                protocol="grpc",
                file_path="test.py",
                line_number=1,
                pattern_matched="import grpc",
                confidence=0.95,
                context="import grpc"
            )
        ]
        
        score = self.calculator.calculate_complexity(
            "grpc", detections, 5, 50
        )
        
        # gRPC has base complexity 7, should be higher
        self.assertGreater(score, 40)
        
    def test_unknown_protocol(self):
        """Test unknown protocol gets default score."""
        score = self.calculator.calculate_complexity(
            "unknown_protocol", [], 1, 1
        )
        
        self.assertEqual(score, 50.0)
        
    def test_migration_complexity_same_category(self):
        """Test migration within same category is easier."""
        complexity = self.calculator.calculate_migration_complexity(
            "websocket", "socket.io", 10
        )
        
        # Same category (realtime) should be moderate
        self.assertIn(complexity, ["LOW", "MEDIUM"])
        
    def test_migration_complexity_different_category(self):
        """Test migration between categories is harder."""
        complexity = self.calculator.calculate_migration_complexity(
            "http_rest", "grpc", 50
        )
        
        # Different category and high usage should be hard
        self.assertEqual(complexity, "HIGH")
        
    def test_estimate_migration_time(self):
        """Test migration time estimation."""
        time_low = self.calculator.estimate_migration_time("LOW", 2)
        time_high = self.calculator.estimate_migration_time("HIGH", 20)
        
        self.assertIn("hour", time_low)
        self.assertTrue("day" in time_high or "week" in time_high)


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RecommendationEngine()
        
    def test_initialization(self):
        """Test engine initializes."""
        engine = RecommendationEngine()
        self.assertIsNotNone(engine)
        
    def test_recommendations_for_realtime(self):
        """Test recommendations for real-time requirement."""
        detected = {
            "websocket": {
                "total_matches": 5,
                "files": ["a.py", "b.py"]
            }
        }
        
        recs = self.engine.generate_recommendations(detected, "realtime")
        
        self.assertGreater(len(recs), 0)
        # WebSocket should be recommended for realtime
        proto_names = [r.protocol for r in recs]
        self.assertIn("WebSocket", proto_names)
        
    def test_recommendations_prefer_existing(self):
        """Test that existing protocols get bonus."""
        detected = {
            "http_rest": {
                "total_matches": 20,
                "files": ["api.py", "client.py", "test.py"]
            }
        }
        
        recs = self.engine.generate_recommendations(detected, "request-response")
        
        # HTTP/REST should be near the top since it's already used
        top_3 = [r.protocol for r in recs[:3]]
        self.assertIn("HTTP/REST", top_3)
        
    def test_recommendations_have_rationale(self):
        """Test that recommendations include rationale."""
        recs = self.engine.generate_recommendations({}, "realtime")
        
        for rec in recs:
            self.assertIsInstance(rec.rationale, list)
            self.assertGreater(len(rec.rationale), 0)
            
    def test_recommendations_have_pros_cons(self):
        """Test that recommendations include pros and cons."""
        recs = self.engine.generate_recommendations({}, "realtime")
        
        for rec in recs:
            self.assertIsInstance(rec.pros, list)
            self.assertIsInstance(rec.cons, list)
            self.assertGreater(len(rec.pros), 0)
            self.assertGreater(len(rec.cons), 0)
            
    def test_recommendations_sorted_by_score(self):
        """Test recommendations are sorted by score."""
        recs = self.engine.generate_recommendations({}, "realtime")
        
        scores = [r.score for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestProtocolAnalyzer(unittest.TestCase):
    """Test main analyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ProtocolAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test analyzer initializes."""
        analyzer = ProtocolAnalyzer()
        self.assertIsNotNone(analyzer)
        
    def test_initialization_verbose(self):
        """Test analyzer initializes with verbose flag."""
        analyzer = ProtocolAnalyzer(verbose=True)
        self.assertTrue(analyzer.verbose)
        
    def test_analyze_project(self):
        """Test full project analysis."""
        test_file = Path(self.temp_dir) / "app.py"
        test_file.write_text("""
import websocket

def connect():
    ws = websocket.WebSocketApp("ws://localhost:8080")
    return ws
""")
        
        result = self.analyzer.analyze(self.temp_dir)
        
        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.project_path, str(Path(self.temp_dir).absolute()))
        self.assertIsNotNone(result.timestamp)
        
    def test_analyze_with_requirement(self):
        """Test analysis with specific requirement."""
        result = self.analyzer.analyze(self.temp_dir, requirement="realtime")
        
        self.assertIsInstance(result, AnalysisResult)
        
    def test_analyze_nonexistent_project(self):
        """Test analyzing non-existent project."""
        with self.assertRaises(FileNotFoundError):
            self.analyzer.analyze("/nonexistent/path/12345")
            
    def test_result_has_recommendations(self):
        """Test result includes recommendations."""
        result = self.analyzer.analyze(self.temp_dir)
        
        self.assertIsInstance(result.recommendations, list)
        self.assertGreater(len(result.recommendations), 0)
        
    def test_result_has_summary(self):
        """Test result includes summary."""
        result = self.analyzer.analyze(self.temp_dir)
        
        self.assertIsInstance(result.summary, str)
        self.assertGreater(len(result.summary), 0)
        
    def test_compare_protocols(self):
        """Test protocol comparison."""
        comparison = self.analyzer.compare_protocols(["websocket", "socket.io"])
        
        self.assertIn("WebSocket", comparison)
        self.assertIn("Socket.IO", comparison)
        
        ws_data = comparison["WebSocket"]
        self.assertIn("category", ws_data)
        self.assertIn("pros", ws_data)
        self.assertIn("cons", ws_data)
        
    def test_compare_unknown_protocol(self):
        """Test comparing unknown protocol."""
        comparison = self.analyzer.compare_protocols(["unknown_proto_xyz"])
        
        self.assertIn("unknown_proto_xyz", comparison)
        self.assertIn("error", comparison["unknown_proto_xyz"])
        
    def test_get_migration_guide(self):
        """Test migration guide generation."""
        guide = self.analyzer.get_migration_guide("socket.io", "websocket")
        
        self.assertIn("from", guide)
        self.assertIn("to", guide)
        self.assertIn("difficulty", guide)
        self.assertIn("steps", guide)
        self.assertIsInstance(guide["steps"], list)
        
    def test_migration_guide_unknown_from(self):
        """Test migration with unknown source."""
        guide = self.analyzer.get_migration_guide("unknown_proto", "websocket")
        
        self.assertIn("error", guide)
        
    def test_migration_guide_unknown_to(self):
        """Test migration with unknown target."""
        guide = self.analyzer.get_migration_guide("websocket", "unknown_proto")
        
        self.assertIn("error", guide)
        
    def test_to_json(self):
        """Test JSON export."""
        result = self.analyzer.analyze(self.temp_dir)
        json_output = self.analyzer.to_json(result)
        
        # Should be valid JSON
        parsed = json.loads(json_output)
        self.assertIsInstance(parsed, dict)
        self.assertIn("project_path", parsed)
        
    def test_to_markdown(self):
        """Test Markdown export."""
        result = self.analyzer.analyze(self.temp_dir)
        md_output = self.analyzer.to_markdown(result)
        
        self.assertIn("# Protocol Analysis Report", md_output)
        self.assertIn("## Summary", md_output)
        self.assertIn("## Recommendations", md_output)


class TestProtocolsDatabase(unittest.TestCase):
    """Test protocol database integrity."""
    
    def test_all_protocols_have_required_fields(self):
        """Test all protocols have required fields."""
        required_fields = ['name', 'category', 'complexity_base', 'dependencies',
                          'pros', 'cons', 'typical_use_cases', 'compatibility_notes']
        
        for key, info in PROTOCOLS_DB.items():
            for field in required_fields:
                self.assertTrue(
                    hasattr(info, field),
                    f"Protocol {key} missing field {field}"
                )
                
    def test_complexity_in_range(self):
        """Test all complexity scores are in valid range."""
        for key, info in PROTOCOLS_DB.items():
            self.assertGreaterEqual(info.complexity_base, 1)
            self.assertLessEqual(info.complexity_base, 10)
            
    def test_categories_are_valid(self):
        """Test all categories are valid."""
        valid_categories = ['realtime', 'request-response', 'streaming', 'rpc']
        
        for key, info in PROTOCOLS_DB.items():
            self.assertIn(info.category, valid_categories,
                         f"Protocol {key} has invalid category: {info.category}")
                         
    def test_all_protocols_have_detection_patterns(self):
        """Test all protocols have detection patterns."""
        for key in PROTOCOLS_DB:
            self.assertIn(key, DETECTION_PATTERNS,
                         f"Protocol {key} has no detection patterns")
            self.assertGreater(len(DETECTION_PATTERNS[key]), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_binary_file_handling(self):
        """Test handling of binary files."""
        binary_file = Path(self.temp_dir) / "data.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xff\xfe')
        
        detector = ProtocolDetector()
        # Should not crash on binary files
        detections = detector.scan_project(Path(self.temp_dir))
        self.assertIsInstance(detections, list)
        
    def test_unicode_file_handling(self):
        """Test handling of Unicode content."""
        unicode_file = Path(self.temp_dir) / "test.py"
        unicode_file.write_text("""
# Файл с юникодом
import websocket  # вебсокет
ws = websocket.connect('ws://example.com')
""", encoding='utf-8')
        
        detector = ProtocolDetector()
        detections = detector.scan_project(Path(self.temp_dir))
        
        websocket_detections = [d for d in detections if d.protocol == "websocket"]
        self.assertGreater(len(websocket_detections), 0)
        
    def test_very_long_lines(self):
        """Test handling of very long lines."""
        test_file = Path(self.temp_dir) / "long.py"
        long_line = "x = " + "a" * 10000 + " # import websocket"
        test_file.write_text(long_line)
        
        detector = ProtocolDetector()
        # Should not crash
        detections = detector.scan_project(Path(self.temp_dir))
        self.assertIsInstance(detections, list)
        
    def test_single_file_analysis(self):
        """Test analyzing a single file instead of directory."""
        test_file = Path(self.temp_dir) / "single.py"
        test_file.write_text("import requests\nrequests.get('http://test')")
        
        detector = ProtocolDetector()
        detections = detector.scan_project(test_file)
        
        self.assertGreater(len(detections), 0)
        
    def test_nested_directory_structure(self):
        """Test deeply nested directories."""
        deep_path = Path(self.temp_dir)
        for i in range(10):
            deep_path = deep_path / f"level{i}"
        deep_path.mkdir(parents=True)
        
        test_file = deep_path / "deep.py"
        test_file.write_text("import websocket")
        
        detector = ProtocolDetector()
        detections = detector.scan_project(Path(self.temp_dir))
        
        self.assertGreater(len(detections), 0)
        
    def test_symlink_handling(self):
        """Test handling of symbolic links (if supported)."""
        # Create a regular file
        real_file = Path(self.temp_dir) / "real.py"
        real_file.write_text("import websocket")
        
        # Try to create symlink (may fail on some systems)
        link_file = Path(self.temp_dir) / "link.py"
        try:
            link_file.symlink_to(real_file)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not supported on this system")
            
        detector = ProtocolDetector()
        # Should not crash or infinite loop
        detections = detector.scan_project(Path(self.temp_dir))
        self.assertIsInstance(detections, list)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ProtocolAnalyzer()
        
    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_full_workflow(self):
        """Test complete analysis workflow."""
        # Create a realistic project structure
        src = Path(self.temp_dir) / "src"
        src.mkdir()
        
        (src / "server.py").write_text("""
import socketio

sio = socketio.AsyncServer()

@sio.event
async def connect(sid, environ):
    await sio.emit('welcome', {'message': 'Connected'})
    
@sio.event
async def disconnect(sid):
    print(f'Disconnected: {sid}')
""")
        
        (src / "api.py").write_text("""
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()
    
def post_data(url, data):
    return requests.post(url, json=data)
""")
        
        (src / "client.js").write_text("""
const io = require('socket.io-client');
const socket = io('http://localhost:3000');

socket.on('connect', () => {
    console.log('Connected!');
    socket.emit('message', 'Hello');
});
""")
        
        # Run analysis
        result = self.analyzer.analyze(self.temp_dir)
        
        # Verify results
        self.assertIsInstance(result, AnalysisResult)
        self.assertGreater(len(result.detected_protocols), 0)
        self.assertGreater(len(result.recommendations), 0)
        
        # Check detected protocols
        proto_names = [p.name for p in result.detected_protocols]
        self.assertTrue(
            "socket.io" in proto_names or "http_rest" in proto_names,
            f"Expected socket.io or http_rest in {proto_names}"
        )
        
        # Check warnings if applicable
        if "socket.io" in proto_names:
            socket_warnings = [w for w in result.warnings if "Socket.IO" in w]
            # Should have version compatibility warning
            self.assertGreater(len(socket_warnings), 0)
            
    def test_json_roundtrip(self):
        """Test JSON export and basic structure."""
        result = self.analyzer.analyze(self.temp_dir)
        
        json_str = self.analyzer.to_json(result)
        data = json.loads(json_str)
        
        self.assertEqual(data["project_path"], result.project_path)
        self.assertIsInstance(data["recommendations"], list)
        
    def test_markdown_generation(self):
        """Test Markdown report generation."""
        # Create test file
        (Path(self.temp_dir) / "test.py").write_text("import websocket")
        
        result = self.analyzer.analyze(self.temp_dir)
        md = self.analyzer.to_markdown(result)
        
        # Verify Markdown structure
        self.assertIn("# Protocol Analysis Report", md)
        self.assertIn("## Detected Protocols", md)
        self.assertIn("## Recommendations", md)
        self.assertIn("---", md)


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def test_parser_creation(self):
        """Test argument parser creates correctly."""
        from protocolanalyzer import create_parser
        
        parser = create_parser()
        self.assertIsNotNone(parser)
        
    def test_parser_analyze_command(self):
        """Test analyze command parsing."""
        from protocolanalyzer import create_parser
        
        parser = create_parser()
        args = parser.parse_args(['analyze', '/some/path'])
        
        self.assertEqual(args.command, 'analyze')
        self.assertEqual(args.project_path, '/some/path')
        
    def test_parser_compare_command(self):
        """Test compare command parsing."""
        from protocolanalyzer import create_parser
        
        parser = create_parser()
        args = parser.parse_args(['compare', 'websocket', 'socket.io'])
        
        self.assertEqual(args.command, 'compare')
        self.assertEqual(args.protocols, ['websocket', 'socket.io'])
        
    def test_parser_migrate_command(self):
        """Test migrate command parsing."""
        from protocolanalyzer import create_parser
        
        parser = create_parser()
        args = parser.parse_args(['migrate', 'socket.io', 'websocket'])
        
        self.assertEqual(args.command, 'migrate')
        self.assertEqual(args.from_protocol, 'socket.io')
        self.assertEqual(args.to_protocol, 'websocket')
        
    def test_parser_list_command(self):
        """Test list command parsing."""
        from protocolanalyzer import create_parser
        
        parser = create_parser()
        args = parser.parse_args(['list'])
        
        self.assertEqual(args.command, 'list')
        
    def test_parser_format_options(self):
        """Test format options."""
        from protocolanalyzer import create_parser
        
        parser = create_parser()
        
        for fmt in ['json', 'markdown', 'text']:
            args = parser.parse_args(['analyze', '/path', '--format', fmt])
            self.assertEqual(args.format, fmt)


def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: ProtocolAnalyzer v1.0")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexityCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolsDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"RESULTS: {total} tests")
    print(f"[OK] Passed: {passed}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
