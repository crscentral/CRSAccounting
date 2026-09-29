with open('src/components/AccountFormModal.jsx', 'r') as f:
    content = f.read()

# I want to add an effect that listens to `form.name` and auto-fills `form.code` if found.
# But it requires debouncing or just a blur event.
# Let's just do it on blur.
