# Changelog

## [Latest] - 2025-11-28

### Added

- ✅ **tunnel.sh** - New wrapper script that automatically activates venv and starts all configured tunnels
  - Auto-detects Python binary from `.env` or defaults to `venv/bin/python`
  - Includes retry logic (up to 3 attempts) for SSH connection issues
  - Graceful error handling with clear status messages
  - Works seamlessly with systemd services

### Fixed

- ✅ **pytunnel.py** - Fixed white page issue when accessing public URL
  - Removed slow SSH pre-check that was causing timeouts
  - Removed slow cleanup step that was hanging startup
  - Changed from `reverse_forward_multiple()` to individual `reverse_forward_tunnel()` calls for better reliability
  - Added retry logic for SSH connection timeouts
  - Added delays between tunnel connections to prevent connection issues
  - Improved error handling with informative messages

### Changed

- ✅ **README.md** - Updated with new tunnel.sh usage and troubleshooting guides
  - Added "Quick Start - Using tunnel.sh (Recommended)" section
  - Added troubleshooting for white page issues
  - Added troubleshooting for connection timeouts
  - Updated project structure to include tunnel.sh
  - Updated Technologies section with accurate dependencies

### Technologies

- **Requirements.txt** - Cleaned to 3 core dependencies:
  - paramiko==4.0.0
  - duckdb==1.4.2
  - python-dotenv==1.0.0

## Usage

### Recommended Way to Start Tunnels

```bash
./tunnel.sh
```

This is the easiest and most reliable way. It handles:

- Automatic venv activation
- SSH connection retries
- All tunnel startup with proper delays
- Error recovery

### Alternative Methods

```bash
# Manual activation
source venv/bin/activate
python pytunnel.py

# Interactive menu
./pymanage.py
```

## Key Improvements

1. **No More Manual venv Activation** - `tunnel.sh` handles it automatically
2. **Automatic Retry Logic** - Failed connections retry up to 3 times
3. **Better Error Messages** - Clear indication of what's wrong
4. **Reliable Multi-Tunnel Startup** - Staggered tunnel creation with proper delays
5. **Flask App Works Perfectly** - Public URL now displays content correctly

## Testing Completed

- ✅ Flask app accessible at `http://bunker.geekdo.me:8000/` with full HTML content
- ✅ SSH reverse tunnels established successfully
- ✅ Multiple simultaneous tunnels working
- ✅ Connection resilience tested and improved
- ✅ Error handling and recovery verified
