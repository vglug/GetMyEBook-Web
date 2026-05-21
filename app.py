import importlib

# Import the package initializer directly to avoid importing the
# top-level `cps.py` script which would parse CLI args unexpectedly.
cps_pkg = importlib.import_module('cps.__init__')

def create_app():
    return cps_pkg.create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
