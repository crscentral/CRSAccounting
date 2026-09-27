import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# I will wrap the return statement in a try/catch.
# Actually, I can just write a quick wrapper component inside the file.
new_wrapper = """
class AnalyticsErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() { 
    if (this.state.hasError) return <div className="p-10 text-red-500 font-bold">ERROR: {String(this.state.error)}<br/>{this.state.error && this.state.error.stack}</div>; 
    return this.props.children; 
  }
}
"""

# Replace export default function Analytics() with export default function AnalyticsWrapped() { return <AnalyticsErrorBoundary><Analytics /></AnalyticsErrorBoundary> }
content = content.replace("export default function Analytics() {", "import React from 'react';\n" + new_wrapper + "\nfunction AnalyticsInner() {")
content = content.replace("export default function Analytics()", "function AnalyticsInner()")

content += "\nexport default function Analytics() { return <AnalyticsErrorBoundary><AnalyticsInner /></AnalyticsErrorBoundary>; }\n"

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)

