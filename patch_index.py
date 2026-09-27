import re

with open('index.html', 'r') as f:
    content = f.read()

# Replace viewport and status bar tags
old_viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />'
new_viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover" />'
content = content.replace(old_viewport, new_viewport)

old_status_bar = '<meta name="apple-mobile-web-app-status-bar-style" content="default" />'
new_status_bar = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />'
content = content.replace(old_status_bar, new_status_bar)

with open('index.html', 'w') as f:
    f.write(content)
