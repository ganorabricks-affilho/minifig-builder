# minifig-builder
Build minifigs based on parts

## BrickStore Database Downloader

This repository includes a script to download the latest LEGO catalog database files from the [BrickStore Database](https://github.com/rgriebl/brickstore-database) repository.

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Usage

#### Download Latest Database Files

Run the download script:
```bash
python3 src/download_brickstore_data.py
```

The script will:
- Fetch the latest release from the BrickStore Database repository
- Download downloads.zip
- Extract M.csv from the parts folder
- Save files to the `brickstore-data/` folder
- Replace existing files with the latest versions

#### Fetch Complete Inventory from BrickLink API

To get the complete parts list for any minifigure directly from BrickLink:

1. **Get API Credentials:**
   - Go to https://www.bricklink.com/v2/api/register_consumer.page
   - Register your application
   - You'll receive: Consumer Key, Consumer Secret, Token, and Token Secret

2. **Setup credentials:**
   ```bash
   python3 src/fetch_bricklink_minifig.py --setup
   ```
   This creates `.env.example`. Copy it to `.env`:
   ```bash
   cp .env.example .env
   ```
   
3. **Edit `.env` and add your credentials:**
   ```bash
   BRICKLINK_CONSUMER_KEY=your_consumer_key
   BRICKLINK_CONSUMER_SECRET=your_consumer_secret
   BRICKLINK_TOKEN=your_token
   BRICKLINK_TOKEN_SECRET=your_token_secret
   ```

4. **Fetch minifigure inventory:**
   ```bash
   python3 src/fetch_bricklink_minifig.py SH0031
   ```

This will fetch and display:
- Complete parts list with names
- Colors for each part
- Quantities
- Part flags (alternate, counterpart, extra, spare)

Export options:
```bash
python3 src/fetch_bricklink_minifig.py SH0031 --output json
python3 src/fetch_bricklink_minifig.py SH0031 --output csv
```

### Downloaded Files

After running the script, you'll have:
- **downloads.zip**: Raw catalog data (~36 MB) - Contains colors, categories, items metadata
- **M.csv**: Parts catalog extracted from downloads.zip (~5 MB)

### Available Data

From the `downloads.zip` XML files, you can access:
- **Colors**: 215 LEGO colors with RGB values
- **Categories**: 1,169 item categories
- **Minifigures**: 18,542 minifigure definitions
- **Parts**: 93,232 LEGO parts

**Inventory data** (which parts compose each minifigure/set) is available via the BrickLink API.

### Documentation

For more information about using the API-based finder, see [MINIFIG_FINDER_README.md](MINIFIG_FINDER_README.md)
