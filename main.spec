# -*- mode: python ; coding: utf-8 -*-
import os
import sys
base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
site_packages_path = os.path.join(sys.base_prefix, "lib", "python" + sys.version[:3], "site-packages")

block_cipher = None

a = Analysis(['main.py'],
             pathex=[base_path, site_packages_path],
             binaries=[],
             datas=[('client_secret.json','.'), ('MWGC_logo.png','.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='MWGC Autofill Ringer Board',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
