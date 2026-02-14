# Minifigure Builder - Complete Solution

## 🎯 What This Does

Given your LEGO parts inventory (XML file), find which official LEGO minifigures you can build!

**Your inventory**: 4,094 unique parts, 19,785 total pieces

## ✅ Solution: API-Based Finder

I've created an **API-based solution** that:
- Uses BrickLink's API to fetch real-time minifigure data
- Checks which minifigures you can build from your parts
- Caches results locally to minimize API calls
- Simple, maintainable, and reliable

## 🚀 Quick Start

### 1. Make sure you have BrickLink API credentials

Your `.env` file should contain:
```
BRICKLINK_CONSUMER_KEY=your_key
BRICKLINK_CONSUMER_SECRET=your_secret  
BRICKLINK_TOKEN=your_token
BRICKLINK_TOKEN_SECRET=your_token_secret
```

### 2. Run the finder

```bash
# Check popular minifigures (uses built-in list)
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml

# Show only complete matches
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml --complete-only

# Check your custom list
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml --minifig-list my_targets.txt

# Save results to JSON
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml --output results.json
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| **src/find_minifigs_api.py** | Main script - finds buildable minifigures |
| **bricklink-inventory/ganorabricks-store.xml** | Your parts inventory (4,094 unique parts) |
| **API_MINIFIG_FINDER.md** | Complete documentation |
| **.api_cache/** | Cached API responses (created automatically) |

## 🔍 How to Find Minifigure IDs

### Option 1: Browse BrickLink
1. Go to https://www.bricklink.com/catalogList.asp?catType=M
2. Choose a theme/category
3. Click on minifigures you want to check
4. Note the ID from URL: `?M=SW0036` → ID is **SW0036**

### Option 2: Create a Custom List File

1. Create a text file `my_targets.txt` with one minifigure ID per line:
```
SW0036
SW0140
SH001
HP001
```

2. Then run:
```bash
python3 src/find_minifigs_api.py bricklink-inventory/ganorabricks-store.xml --minifig-list my_targets.txt
```

## 📊 Example Output

```
✅ COMPLETE MATCHES (3 minifigures):
--------------------------------------------------------------------------------

🎯 SW0036 - Luke Skywalker (Orange Flight Suit)
   Year: 2009
   Category: Star Wars
   Parts: 4 (100% match)
   Status: ✅ CAN BUILD NOW!

⚠️  PARTIAL MATCHES (12 minifigures):
--------------------------------------------------------------------------------

📊 SW0214 - Clone Trooper
   Year: 2010
   Match: 3/4 parts (75.0%)
   Missing 1 parts:
      • Minifigure, Headgear Helmet (White) - need 1 more
```

## 💡 Tips

1. **Start small**: Test with 20-50 minifigure IDs first
2. **Use caching**: After initial run, use `--use-cache-only` for instant results
3. **Focus on themes**: Generate lists for themes you like
4. **Track progress**: Export to JSON and track over time
5. **Rate limits**: First run is slower due to API rate limits (normal)

## 🔧 Technical Details

### Why API-based vs Database Parsing?

| Approach | Pros | Cons |
|----------|------|------|
| **Binary Database** | Fast, offline | Complex parsing, maintenance |
| **API-based** ✅ | Simple, real-time data, cacheable | Requires API credentials |

### Languages

**Python is the best choice** because:
- ✅ Built-in `lzma` support for databases
- ✅ Excellent for API calls (requests library)
- ✅ Easy XML parsing
- ✅ Great for data analysis
- ✅ Your existing code is already in Python

### Database Format

The BrickLink API provides:
- Real-time minifigure data
- Complete part inventories
- Current pricing information
- Caching support for offline use

## 📚 Documentation

- **API_MINIFIG_FINDER.md** - Complete guide
- **BRICKLINK_API_SETUP.md** - API setup instructions
- **README.md** - Project readme

## 🎓 Next Steps

1. Generate minifigure lists for your favorite themes
2. Run the finder and discover what you can build
3. Track new buildable minifigures as you acquire parts
4. Build a web dashboard to visualize results
5. Share your wishlist of almost-buildable minifigures

## ⚡ Performance

- **Initial run**: ~0.15s per minifigure (API rate limits)
- **Cached run**: Instant (reads from `.api_cache/`)
- **Your inventory**: Loads in <1 second

Example: Checking 100 minifigures
- First time: ~15-20 seconds
- With cache: <1 second

Enjoy building! 🧱✨
