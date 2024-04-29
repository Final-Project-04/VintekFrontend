# Simulate a session with a dictionary
session = {}

# Simulate storing a token in the session
session['token'] = 'ce8f42ece0ce6c5011ecb0a733e2d634f29369f4'
print(f"Token in session: {session.get('token')}")

# Simulate clearing the session
session.clear()
print(f"Token in session after clearing: {session.get('token')}")