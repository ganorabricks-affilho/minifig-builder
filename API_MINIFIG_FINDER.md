# API-Based Minifigure Finder

## Overview

The **API-based minifigure finder** uses the BrickLink API to check which official LEGO minifigures you can build from your parts inventory.

## Why API-based?

✅ **Real-time data** - Always up-to-date minifigure information  
✅ **Simpler** - No complex binary database parsing  
✅ **Caching** - API responses saved locally to minimize calls  
✅ **Targeted** - Check specific themes or minifigure lists  
✅ **Maintainable** - Easier to understand and modify

## Quick Start

### 1. Set up BrickLink API credentials

Get your API credentials from: https://www.bricklink.com/v2/api/register_consumer.page

Create a `.env` file with:
```
BRICKLINK_CONSUMER_KEY=your_key_here
BRICKLINK_CONSUMER_SECRET=your_secret_here
BRICKLINK_TOKEN=your_token_here
BRICKLINK_TOKEN_SECRET=your_token_secret_here
```

### 2. Run the finder

Run from the root workspace directory:

```bash
# Check minifigures using cached data
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml
```

## Populating the Cache

The script uses cached minifigure data. To populate the cache with valuable minifigures:

```bash
python3 src/cache_valuable_minifigs.py --theme SW
python3 src/cache_valuable_minifigs.py --theme SH
```

Then run the finder to check against your inventory.

## Finding Minifigure IDs

### BrickLink Search
1. Go to https://www.bricklink.com/catalogList.asp?catType=M
2. Browse categories (Star Wars, Super Heroes, Harry Potter, etc.)
3. Click on a minifigure
4. The ID is in the URL: `/catalogItem.asp?M=SW0036` → ID is `SW0036`

### Common Themes

- **Star Wars**: SW#### (e.g. SW0036, SW0214)
- **Super Heroes**: SH#### (e.g., SH034, SH185)
- **Harry Potter**: HP#### (e.g., HP001, HP006)
- **City**: CTY#### (e.g., CTY095)
- **Creator**: COL#### (e.g., COL001)
- **Ninjago**: NJO#### (e.g., NJO001)

## How It Works

1. **Loads your inventory** from XML file (4,094 unique parts)
2. **Connects to BrickLink API** using OAuth1 authentication
3. **For each minifigure**:
   - Fetches item data (name, year, category)
   - Fetches part inventory
   - Compares against your parts
   - Caches result locally
4. **Reads cached minifigure data** from `.api_cache/minifigures.json`
3. **For each minifigure in cache**:
   - Compares parts against your inventory
   - Calculates match percentage
   - Ide Location

The cache is stored in the workspace root directory:

```
minifig-builder/
├── .api_cache/              (cache folder in root)
│   ├── minifigures.json     (cached minifigure data)
│  Performance

Since the finder uses cached data:
- **Instant results** - No API calls needed
- **Low overhead** - Efficient JSON parsing and comparison
- **Populate cache separately** - Use `cache_valuable_minifigs.py` to fetch data from API
    └── ganorabricks-store.xml
``
## APPopulate cache first**: Run `cache_valuable_minifigs.py` for themes you care about
2. **Focus on themes**: Star Wars (SW), Super Heroes (SH), Harry Potter (HP) have most minifigs
3. **Check results**: Run finder periodically as you acquire new parts
4. **Filter prices**: Use `--min-price` flag when caching to only get valuable minifigs
5. **Multiple themes**: Run cache script for each theme separately or all at once
- Use `--use-cache-only` to avoid any API calls

## Tips

1. **Start small**: Test with 10-20 minifigure IDs first
2. **Build your list**: Add more IDs as you discover interesting minifigures
3. **Check themes**: Focus on themes you like (Star Wars, Marvel, etc.)
4. **Use cache**: After initial run, re-run with `--use-cache-only` for instant results
5. **Export results**: Use `--output results.json` to save and analyze later
- Create `.env` file in the **workspace root** with your credentials
- Or set environment variables
- Get credentials from BrickLink API console
- `.env` must be at: `minifig-builder/.env` (not in src folder)
### "API request failed: 404"
- The minifigure ID doesn't exist
- Check ID format on BrickLink
- Some IDs may be retired or never existed

### "BrickLink API credentials not found"
- Create `.env` file with your credentials
- Or set environment variables
- Get credentials from BrickLink API console
Cache not found
- Run `python3 src/cache_valuable_minifigs.py --theme SW` first
- This populates `.api_cache/minifigures.json` with minifigure data
- Then run the finder script
- API rate limits are 0.15s per call (normal)

## Example Output

```
✅ COMPLETE MATCHES (2 minifigures):
--------------------------------------------------------------------------------

🎯 SW0036 - Luke Skywalker (Orange Flight Suit)
   Year: 2009
   Category: Star Wars
   Parts: 4 (100% match)
   Status: ✅ CAN BUILD NOW!

🎯 HP001 - Harry Potter
   Year: 2001
   Category: Harry Potter
   Parts: 4 (100% match)
   Status: ✅ CAN BUILD NOW!

⚠️  PARTIAL MATCHES (15 minifigures):
--------------------------------------------------------------------------------

📊 SW0214 - Clone Trooper
   Year: 2010
   Category: Star Wars
   Match: 3/4 parts (75.0%)
   Missing 1 parts:
      • Minifigure, Headgear Helmet Clone Trooper (White) - need 1 more
```

## Next Steps

- Create targeted minifigure lists for themes you like
- Run periodically as you acquire new parts
- Export to JSON and build a web dashboard
- Integrate with your parts management system
