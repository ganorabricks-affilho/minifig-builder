# Minifigure Price Caching System

## Status

⚠️ **Note:** Price caching functionality is currently not available. The primary minifigure finder uses the BrickLink API for availability and parts data.

## Overview (Reference)

The price caching system was designed to allow you to:
- **Fetch minifigure prices independently** from minifigure data (scrapes from BrickLink)
- **Update prices on a separate schedule** without re-fetching full minifig info
- **Track 6-month average prices** from BrickLink sales data
- **Compare with current market prices** (current inventory listings)
- **Cache prices locally** to minimize web requests

## How It Would Work (Archived Design)

The system was designed with two separate caches:

1. **Minifigure Cache** (`.api_cache/minifigures.json`)
   - Contains full minifigure data (name, parts, etc.)
   - Built once when you discover a minifigure
   - Updates only if you re-run `find_minifigs_api.py` without `--use-cache-only`

2. **Price Cache** (`.api_cache/minifig_prices.json`)
   - Contains price data scraped from BrickLink website
   - Can be updated independently on any schedule
   - Includes 6-month sales data + current market prices
   - Timestamps each price update

### Price Scraping Method

Unlike the API, prices are scraped from:
- **Source**: BrickLink's public price guide pages
- **URL**: `https://www.bricklink.com/priceGuideSummary.asp`
- **Method**: HTML table parsing
- **Rate**: ~0.1s per minifigure (respects rate limits)
- **Data**: Same data BrickStore uses (from HTML table)

### Independent Update Process

```
find_minifigs_api.py          update_minifig_prices.py
        ↓                              ↓
   Fetches minifigs              Fetches prices
   Caches full data              Caches price data
   (slower)                       (faster, independent)
        ↓                              ↓
   .api_cache/                   .api_cache/
   minifigures.json              minifig_prices.json
```

## Usage

⚠️ **Currently not available** - Price updating scripts have been removed.

For now, use the main finder for minifigure availability:
```bash
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml
```

### Previous Implementation (Reference)

The old workflow had these steps:

## API Rate Limits

- Both scripts respect BrickLink API rate limits (0.15s per call)
- Prices are cached, so subsequent runs use cached data
- Update script uses `--use-cache-only` by default to avoid re-fetching minifig data

## Price Data Included

Each cached price includes:
```json
{
  "minifig_id": {
    "data": {
      "ordered_new": {
        "lots": 27,
        "quantity": 40,
        "min_price": 5.99,
        "avg_price": 14.03,
        "qty_avg_price": 13.68,
        "max_price": 30.00
      },
      "ordered_used": { ... },    // Past 6 months used
      "inventory_new": { ... },   // Current market new
      "inventory_used": { ... }   // Current market used
    },
    "updated": "2026-02-12T20:54:27"
  }
}
```

## Workflow Examples

### Scenario: New Minifigures

1. Run finder to discover minifigures:
   ```bash
   python3 find_minifigs_api.py ganorabricks-store.xml
   ```

2. Later, update prices for all:
   ```bash
   python3 update_minifig_prices.py
   ```

3. Next month, just update prices (minifig data doesn't change):
   ```bash
   python3 update_minifig_prices.py
   ```

### Scenario: Star Wars Focus

1. Get Star Wars minifigures:
   ```bash
   python3 find_minifigs_api.py ganorabricks-store.xml --minifig-list star_wars.txt
   ```

2. Updated prices weekly:
   ```bash
   python3 update_minifig_prices.py --minifig-list star_wars.txt
   ```

### Scenario: Rebuild All

Start fresh:
```bash
# Keep minifig data, rebuild prices
python3 update_minifig_prices.py --clear

# Or use fresh cache for everything
rm -rf .api_cache
python3 find_minifigs_api.py ganorabricks-store.xml
python3 update_minifig_prices.py
```

## File Formats

### Minifigure List (Optional)

For `--minifig-list` option, create a text file with one ID per line:

```
# My Star Wars collection
SW0036
SW0140
SW0273

# HP minifigs
HP001
HP002
HP006
```

Lines starting with `#` are ignored.

## Tips

1. **First run takes longer** - API calls for each minifigure
2. **Updates are fast** - Uses cached minifig data, only fetches prices
3. **Run prices weekly** - To track price trends over time
4. **Keep minifig list** - Reuse the same list for consistent updates
5. **Export for analysis** - Export results to JSON to analyze trends

## Troubleshooting

### "No minifigures cached"
```bash
python3 find_minifigs_api.py ganorabricks-store.xml
```
Run the finder first to build the minifigure cache.

### "API credentials not found"
See [API_MINIFIG_FINDER.md](API_MINIFIG_FINDER.md) for setup instructions.

### Prices not updating
Make sure minifigure is in cache first:
```bash
python3 update_minifig_prices.py --list
```

If minifigure shows `⚪`, it needs a price fetch.

## Next Steps

1. Create a minifigure list (`minifigs.txt`) with your favorite IDs
2. Build initial cache: `python3 find_minifigs_api.py ganorabricks-store.xml --minifig-list minifigs.txt`
3. Update prices: `python3 update_minifig_prices.py`
4. Schedule weekly updates with your OS:
   - **macOS/Linux**: Use `cron` to run `update_minifig_prices.py` weekly
   - **Windows**: Use Task Scheduler for weekly updates
