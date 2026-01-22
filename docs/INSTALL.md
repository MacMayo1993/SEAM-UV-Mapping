# Installation Guide

## Requirements

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 500MB for addon + test data

### Software Requirements
- **Blender**: 3.6 or newer (4.0+ recommended)
- **Python**: 3.10+ (included with Blender, standalone only for development)

### Python Dependencies (Development Only)
```bash
numpy>=1.24.0
scipy>=1.10.0
pytest>=7.4.0
pytest-benchmark>=4.0.0
matplotlib>=3.7.0
```

## Installation Methods

### Method 1: Blender Addon (Recommended for Artists)

1. **Download Release:**
   - Go to [Releases](https://github.com/MacMayo1993/SEAM-UV-Mapping/releases)
   - Download `non_orientable_uv_addon_v1.0.0.zip`
   - **Do NOT unzip** - Blender expects a .zip file

2. **Install in Blender:**
   ```
   1. Open Blender
   2. Edit → Preferences (or Blender → Preferences on macOS)
   3. Add-ons tab
   4. Click "Install..." button
   5. Navigate to downloaded .zip file
   6. Click "Install Add-on"
   7. Search for "Non-Orientable" in add-ons list
   8. Check the box to enable it
   ```

3. **Verify Installation:**
   ```
   1. Open UV Editor workspace
   2. Press N to open sidebar
   3. Look for "Non-Orientable" tab
   4. If present, installation successful!
   ```

### Method 2: Development Install (For Contributors)

1. **Clone Repository:**
   ```bash
   git clone https://github.com/MacMayo1993/SEAM-UV-Mapping.git
   cd SEAM-UV-Mapping
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Symlink to Blender:**

   **Linux/macOS:**
   ```bash
   ln -s $(pwd)/addon ~/.config/blender/3.6/scripts/addons/non_orientable_uv
   ```

   **Windows (PowerShell as Admin):**
   ```powershell
   New-Item -ItemType SymbolicLink `
     -Path "$env:APPDATA\Blender Foundation\Blender\3.6\scripts\addons\non_orientable_uv" `
     -Target "$(pwd)\addon"
   ```

4. **Enable in Blender:**
   - Preferences → Add-ons → Refresh
   - Search "Non-Orientable" → Enable

### Method 3: Standalone Python (No Blender)

For using the core algorithm without Blender:

```bash
# Clone repo
git clone https://github.com/MacMayo1993/SEAM-UV-Mapping.git
cd SEAM-UV-Mapping

# Install core package
pip install -e .

# Test installation
python -c "from addon.core.topology import TopologicalUVAtlas; print('Success!')"
```

## Configuration

### Addon Preferences

After installation, configure in Blender Preferences:

```
Edit → Preferences → Add-ons → Non-Orientable UV Unwrapping
```

**Settings:**
- **Default k* threshold**: 0.721 (recommended, adjust ±0.05 for experimentation)
- **Auto-create shader**: Enabled (automatically generates parity-aware materials)
- **Verbose logging**: Disabled (enable for debugging)
- **Max vertices**: 1000000 (safety limit to prevent crashes)

## Troubleshooting

### Common Issues

**Problem:** Addon doesn't appear after installation
**Solution:**
- Ensure Blender version is 3.6+
- Try "Refresh" button in Add-ons preferences
- Check Console (Window → Toggle System Console on Windows) for errors

**Problem:** "No module named 'numpy'" error
**Solution:**
- Blender's Python should include NumPy by default
- If missing: Open Blender's Python console, run:
  ```python
  import subprocess
  import sys
  subprocess.call([sys.executable, "-m", "pip", "install", "numpy", "scipy"])
  ```

**Problem:** Unwrapping crashes on large meshes
**Solution:**
- Reduce `k_star` threshold (fewer stitch edges = faster)
- Increase max vertices limit in preferences
- Try on decimated version first

**Problem:** Shader doesn't work in EEVEE
**Solution:**
- Ensure "Vertex Colors" is enabled in Material Properties
- Check that parity attribute exists (Mesh Properties → Attributes)
- Try re-creating shader with "Create Parity-Aware Shader" operator

### Getting Help

- **Documentation**: Check [docs/](.) folder
- **Issues**: [GitHub Issues](https://github.com/MacMayo1993/SEAM-UV-Mapping/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MacMayo1993/SEAM-UV-Mapping/discussions)

## Uninstallation

**Blender Addon:**
```
Edit → Preferences → Add-ons
Search "Non-Orientable"
Click Remove button
```

**Development Install:**
```bash
# Remove symlink
rm ~/.config/blender/3.6/scripts/addons/non_orientable_uv  # Linux/macOS
Remove-Item "$env:APPDATA\Blender Foundation\Blender\3.6\scripts\addons\non_orientable_uv"  # Windows

# Uninstall Python package
pip uninstall non-orientable-uv
```

## Next Steps

- Read [USAGE.md](USAGE.md) for tutorials
- Try example scripts in [examples/](../examples/)
- Run tests to verify functionality
- Check [API.md](API.md) for programmatic usage
