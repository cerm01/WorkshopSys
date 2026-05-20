# -*- mode: python ; coding: utf-8 -*-
"""
WorkshopSys.spec  -  Configuración de empaquetado PyInstaller
Genera: WorkshopSys.exe  (ejecutable único, sin consola)
"""
import os

# ── Datos a empaquetar ────────────────────────────────────────────────────────
datas = [
    # Íconos de la interfaz
    ('assets/icons', 'assets/icons'),
]

# El modelo ML solo se incluye si ya fue entrenado
if os.path.exists('modelo_ml_onehot.pkl'):
    datas.append(('modelo_ml_onehot.pkl', '.'))
else:
    print("AVISO: modelo_ml_onehot.pkl no encontrado. "
          "El modulo de IA no funcionara en el ejecutable. "
          "Ejecuta 'python entrenar_onehot.py' antes de hacer el build.")

# ── Imports ocultos (PyInstaller no los detecta automaticamente) ──────────────
hidden_imports = [
    # scikit-learn internals
    'sklearn',
    'sklearn.linear_model',
    'sklearn.linear_model._base',
    'sklearn.preprocessing',
    'sklearn.preprocessing._encoders',
    'sklearn.preprocessing._data',
    'sklearn.utils',
    'sklearn.utils._cython_blas',
    'sklearn.utils._weight_vector',
    'sklearn.utils.murmurhash',
    'sklearn.neighbors',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree',
    'sklearn.tree._utils',
    # pandas internals
    'pandas',
    'pandas._libs',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.timestamps',
    # reportlab
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.platypus',
    'reportlab.lib',
    'reportlab.graphics',
    # websocket
    'websocket',
    'websocket._http',
    'websocket._socket',
    'websocket._ssl_compat',
    # PIL / Pillow
    'PIL',
    'PIL.Image',
    'PIL.ImageFile',
    # openpyxl
    'openpyxl',
    # otros
    'unicodedata',
    'pickle',
    'pkg_resources',
    'pkg_resources._vendor',
]

# ── Módulos a excluir (solo del servidor, no necesarios en el cliente) ─────────
excludes = [
    'fastapi',
    'uvicorn',
    'starlette',
    'sqlalchemy',
    'psycopg2',
    'alembic',
    'pytest',
    'unittest',
    'xmlrpc',
    'tkinter',
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
    'server',   # nuestro módulo server/ no se usa en el cliente
]

# ── Análisis ──────────────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

# ── Ejecutable único (.exe sin consola) ───────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WorkshopSys',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # Compresión UPX (reduce tamaño ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # Sin ventana de consola negra
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icons/dmv.jpg',  # Descomentar si tienes un .ico
)
