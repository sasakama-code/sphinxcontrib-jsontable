#!/usr/bin/env python3
"""
Memory usage analysis for TableConverter.

This script analyzes the theoretical memory footprint of the TableConverter
and provides recommendations for memory-safe default limits.
"""

import sys
from typing import Dict, Any, List


def estimate_object_memory_size(obj: Dict[str, Any]) -> int:
    """
    Estimate memory usage of a Python object in bytes.
    
    This is a rough estimation based on Python's internal structure.
    """
    size = sys.getsizeof(obj)  # Base dict size
    
    for key, value in obj.items():
        size += sys.getsizeof(key)  # Key string
        size += sys.getsizeof(value)  # Value
        
        # Additional overhead for dict entry
        size += 24  # Rough estimate for dict entry overhead
    
    return size


def analyze_memory_usage():
    """Analyze memory usage patterns for different data sizes."""
    print("🧠 MEMORY USAGE ANALYSIS")
    print("=" * 50)
    
    # Simulate different object sizes
    object_configs = [
        {"keys": 5, "avg_key_len": 10, "avg_value_len": 20},
        {"keys": 10, "avg_key_len": 15, "avg_value_len": 30},
        {"keys": 20, "avg_key_len": 20, "avg_value_len": 50},
        {"keys": 50, "avg_key_len": 25, "avg_value_len": 100},
    ]
    
    dataset_sizes = [1000, 5000, 10000, 25000, 50000, 100000]
    
    print("\n📊 Estimated Memory Usage by Configuration:")
    print("-" * 80)
    print(f"{'Config':<15} {'Objects':<10} {'Per Object':<12} {'Total (MB)':<12} {'Headers (KB)':<15}")
    print("-" * 80)
    
    recommendations = []
    
    for config in object_configs:
        keys = config["keys"]
        key_len = config["avg_key_len"]
        value_len = config["avg_value_len"]
        
        # Estimate single object size
        sample_obj = {
            f"key_{i:02d}{'x' * (key_len-6)}": f"value_{i}{'x' * (value_len-8)}"
            for i in range(keys)
        }
        obj_size = estimate_object_memory_size(sample_obj)
        
        # Estimate header memory (list of strings)
        headers_size = sum(sys.getsizeof(f"key_{i:02d}{'x' * (key_len-6)}") for i in range(keys))
        headers_size += sys.getsizeof([])  # List overhead
        
        config_name = f"{keys}keys/{key_len}c/{value_len}c"
        
        for size in dataset_sizes:
            total_size_mb = (obj_size * size) / (1024 * 1024)
            headers_size_kb = headers_size / 1024
            
            print(f"{config_name:<15} {size:<10,} {obj_size:<12} {total_size_mb:<12.1f} {headers_size_kb:<15.1f}")
            
            # Add to recommendations if within reasonable limits
            if total_size_mb <= 100:  # 100MB threshold
                recommendations.append({
                    'config': config_name,
                    'max_safe_objects': size,
                    'memory_mb': total_size_mb
                })
            elif size == dataset_sizes[0]:  # Even smallest size exceeds limit
                recommendations.append({
                    'config': config_name,
                    'max_safe_objects': int(100 * 1024 * 1024 / obj_size),  # 100MB limit
                    'memory_mb': 100.0
                })
                break
    
    print("\n💡 MEMORY-BASED RECOMMENDATIONS:")
    print("-" * 50)
    
    # Find conservative recommendation
    min_safe_objects = min(r['max_safe_objects'] for r in recommendations)
    print(f"🛡️  Conservative limit (100MB threshold): {min_safe_objects:,} objects")
    
    # Table conversion memory overhead
    print(f"\n📋 TABLE CONVERSION OVERHEAD:")
    print(f"   • String conversion overhead: ~2x original size")
    print(f"   • Table structure overhead: ~1.5x converted size")
    print(f"   • Total conversion overhead: ~3x original data size")
    
    adjusted_limit = min_safe_objects // 3
    print(f"🎯 Recommended DEFAULT_MAX_ROWS: {adjusted_limit:,}")
    
    return adjusted_limit


def analyze_performance_bottlenecks():
    """Analyze performance bottlenecks in current implementation."""
    print("\n⚡ PERFORMANCE BOTTLENECK ANALYSIS")
    print("=" * 50)
    
    bottlenecks = [
        {
            "component": "_extract_headers",
            "complexity": "O(n * k)",
            "description": "Iterates through all objects and keys",
            "current_limits": "MAX_OBJECTS=10,000, MAX_KEYS=1,000",
            "bottleneck_factor": "High for many objects with many keys"
        },
        {
            "component": "_object_to_row",
            "complexity": "O(n * k)",
            "description": "Converts each object to row format",
            "current_limits": "None",
            "bottleneck_factor": "Linear scaling, but no protection"
        },
        {
            "component": "_convert_array_list",
            "complexity": "O(n * m)",
            "description": "String conversion for all elements",
            "current_limits": "None", 
            "bottleneck_factor": "Memory allocation for string conversion"
        },
        {
            "component": "TableBuilder.build",
            "complexity": "O(n * m)",
            "description": "Creates docutils nodes for each cell",
            "current_limits": "None",
            "bottleneck_factor": "DOM node creation overhead"
        }
    ]
    
    for bottleneck in bottlenecks:
        print(f"\n🔍 {bottleneck['component']}:")
        print(f"   Complexity: {bottleneck['complexity']}")
        print(f"   Description: {bottleneck['description']}")
        print(f"   Current Limits: {bottleneck['current_limits']}")
        print(f"   Bottleneck: {bottleneck['bottleneck_factor']}")
    
    print(f"\n💡 KEY FINDINGS:")
    print(f"   • Only _extract_headers has built-in limits")
    print(f"   • Table conversion and building have no limits")
    print(f"   • Memory usage scales linearly with data size")
    print(f"   • String conversion creates additional memory overhead")


def recommend_implementation_strategy():
    """Recommend implementation strategy based on analysis."""
    print(f"\n🎯 IMPLEMENTATION STRATEGY RECOMMENDATIONS")
    print("=" * 50)
    
    strategies = [
        {
            "priority": "High",
            "component": "TableConverter.convert()",
            "action": "Add DEFAULT_MAX_ROWS = 10,000",
            "reasoning": "Prevent runaway memory usage",
            "implementation": "Check input size before processing"
        },
        {
            "priority": "High", 
            "component": "Logging/Warning System",
            "action": "Warn when limit is applied",
            "reasoning": "User awareness and guidance",
            "implementation": "logger.warning() with helpful message"
        },
        {
            "priority": "Medium",
            "component": "Configuration System", 
            "action": "Add jsontable_max_rows config option",
            "reasoning": "Allow per-project customization",
            "implementation": "Read from Sphinx config in directive"
        },
        {
            "priority": "Medium",
            "component": "Memory Monitoring",
            "action": "Add memory usage tracking",
            "reasoning": "Better understanding of resource usage", 
            "implementation": "Optional tracemalloc integration"
        },
        {
            "priority": "Low",
            "component": "Streaming Processing",
            "action": "Consider streaming for very large datasets",
            "reasoning": "Handle datasets larger than memory",
            "implementation": "Future enhancement for specialized use cases"
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎯 {strategy['priority']} Priority - {strategy['component']}:")
        print(f"   Action: {strategy['action']}")
        print(f"   Reasoning: {strategy['reasoning']}")
        print(f"   Implementation: {strategy['implementation']}")


if __name__ == "__main__":
    try:
        # Run memory analysis
        recommended_limit = analyze_memory_usage()
        
        # Analyze performance bottlenecks
        analyze_performance_bottlenecks()
        
        # Provide implementation recommendations
        recommend_implementation_strategy()
        
        print(f"\n✅ Analysis completed!")
        print(f"🎯 Final Recommendation: DEFAULT_MAX_ROWS = {recommended_limit:,}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
