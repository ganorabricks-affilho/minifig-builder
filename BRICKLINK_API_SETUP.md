# BrickLink API Setup Guide

## Getting Your API Credentials

To use the BrickLink API fetcher, you need to register for API access.

### Step 1: Register for BrickLink API

1. Go to: https://www.bricklink.com/v2/api/register_consumer.page
2. Log in with your BrickLink account (create one if you don't have it)
3. Fill out the application form:
   - **Application Name**: Choose any name (e.g., "Minifig Builder")
   - **Application Description**: Brief description of what you're building
   - **Website**: Can use `http://localhost` if personal use
   - **Application Type**: Select "Desktop Application" or "Personal"
4. Submit the application

### Step 2: Get Your Credentials

After approval (usually instant), you'll receive:
- **Consumer Key** (like a username)
- **Consumer Secret** (like a password)
- **Token Value** (OAuth token)
- **Token Secret** (OAuth token secret)

### Step 3: Configure the Script

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   BRICKLINK_CONSUMER_KEY=YOUR_ACTUAL_CONSUMER_KEY
   BRICKLINK_CONSUMER_SECRET=YOUR_ACTUAL_CONSUMER_SECRET
   BRICKLINK_TOKEN=YOUR_ACTUAL_TOKEN
   BRICKLINK_TOKEN_SECRET=YOUR_ACTUAL_TOKEN_SECRET
   ```

3. Save the file

### Step 4: Test It

```bash
python3 src/fetch_bricklink_minifig.py SH0031
```

You should see the minifigure details with a complete parts list!

## Important Notes

⚠️ **Never commit your `.env` file to Git!** It contains sensitive credentials.
   - The `.gitignore` file is already configured to exclude `.env`

📊 **API Rate Limits:**
   - BrickLink limits API calls
   - The script includes automatic rate limiting (0.1s between requests)
   - For bulk operations, add delays

🔒 **Security:**
   - Keep your credentials private
   - Don't share your `.env` file
   - Regenerate tokens if exposed

## Usage Examples

### Basic fetch:
```bash
python3 fetch_bricklink_minifig.py SH0031
```

### Export to JSON:
```bash
python3 fetch_bricklink_minifig.py SH0031 --output json
```

### Export to CSV:
```bash
python3 fetch_bricklink_minifig.py SH0031 --output csv
```

## Troubleshooting

**"BrickLink API credentials not found!"**
- Make sure `.env` file exists and has correct credentials
- Check that variable names match exactly

**"401 Unauthorized"**
- Verify your credentials are correct
- Check if your API access was approved

**"429 Too Many Requests"**
- You've hit the rate limit
- Wait a few minutes before trying again

**"Item not found"**
- Check the minifigure ID is correct (case-insensitive)
- Verify the item exists on BrickLink

## API Documentation

Full BrickLink API documentation:
https://www.bricklink.com/v3/api.page
