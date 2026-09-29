import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Add ErrorBoundary class at the top of the file, right after imports
boundary_code = """
import React from 'react';
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return <div style={{ padding: '2rem', color: 'red' }}><h1>Something went wrong.</h1><pre>{this.state.error.toString()}</pre></div>;
    }
    return this.props.children;
  }
}
"""
content = content.replace("export default function HotelExpenses() {", boundary_code + "\nexport default function HotelExpenses() {")

# Wrap the return with ErrorBoundary
content = content.replace("  return (\n    <div>", "  return (\n    <ErrorBoundary>\n    <div>")
content = content.replace("      )}\n    </div>\n  )\n}", "      )}\n    </div>\n    </ErrorBoundary>\n  )\n}")

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)

