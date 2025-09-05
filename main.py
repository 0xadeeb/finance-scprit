#!/usr/bin/env python3
"""
Finance Script - Main entry point with signal handling
This script processes bank statements and generates financial summaries using local or cloud storage.
"""

import sys
import signal
from finance_analyzer import FinanceAnalyzer

def main():
    """Main entry point with proper signal handling"""
    analyzer = None
    
    try:
        analyzer = FinanceAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Received Ctrl+C (KeyboardInterrupt)")
        if analyzer:
            print("🧹 Cleaning up temporary files...")
            analyzer._comprehensive_cleanup()
        print("✅ Cleanup complete. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        if analyzer:
            print("🧹 Cleaning up temporary files...")
            analyzer._comprehensive_cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
