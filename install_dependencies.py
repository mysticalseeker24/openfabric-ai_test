import subprocess
import sys
import os

# Create a directory for modified packages if it doesn't exist
os.makedirs('openfabric_custom', exist_ok=True)

print("==== Openfabric Assessment Dependencies Installation ====")
print("Installing core dependencies with precompiled wheels where possible...")

# First install packages that are less problematic and don't depend on C extensions
try:
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install',
        'python-dateutil', 'requests', 'marshmallow', 'pillow', 'pydantic'
    ])
    print("✅ Core utilities successfully installed")
except Exception as e:
    print(f"❌ Error installing core utilities: {e}")

# Try to install optional dependencies
print("\nAttempting to install optional dependencies...")
optional_deps = [
    ('ollama', 'LLM integration'),
    ('streamlit', 'GUI frontend'),
    ('chromadb', 'Advanced memory system')
]

for package, description in optional_deps:
    try:
        print(f"Installing {package} for {description}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ {package} successfully installed")
    except Exception as e:
        print(f"❌ Could not install {package}: {e}")
        print(f"   {description} functionality may be limited")

# Install openfabric-pysdk using --no-dependencies to avoid the gevent compilation issue
print("\nInstalling openfabric-pysdk...")
try:
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', 'openfabric-pysdk==0.2.9', '--no-dependencies'
    ])
    print("✅ openfabric-pysdk successfully installed (without dependencies)")
except Exception as e:
    print(f"❌ Error installing openfabric-pysdk: {e}")

# Install required dependencies of openfabric-pysdk that are safe (excluding gevent)
print("\nInstalling required openfabric-pysdk dependencies...")
safe_deps = [
    'Flask>=2.0.1,<3.0.0',
    'Flask-Cors>=3.0.10,<4.0.0',
    'Flask-RESTful>=0.3.9,<0.4.0',
    'Flask-SocketIO>=5.3.6,<6.0.0',
    'Werkzeug>=2.0.3',
    'marshmallow-enum>=1.5.1,<2.0.0',
    'marshmallow-jsonapi>=0.24.0,<0.25.0',
    'marshmallow>=3.0.0,<4.0.0',
    'pydantic>=1.8.2,<2.0.0',
    'python-socketio>=5.3.0,<6.0.0',
    'schema>=0.7.4,<0.8.0',
    'termcolor>=1.1.0,<2.0.0',
    'tqdm>=4.62.3,<5.0.0'
]

for dep in safe_deps:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        print(f"✅ Installed {dep}")
    except Exception as e:
        print(f"❌ Failed to install {dep}: {e}")

print("\n==== Installation Summary ====")
print("The core components have been installed.")
print("Some C extension-based packages may need to be installed manually if they're required.")
print("\nYou can now run the application with:")
print("python main.py")
print("\nTo check which features are available:")
print("python main.py --check")
