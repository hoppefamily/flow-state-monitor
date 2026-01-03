import json
import urllib.error
import urllib.request


def test_ortex_api():
    """Test the Ortex API with the TEST key."""

    api_key = 'TEST'
    symbol = 'AAPL'

    # Try different endpoints
    endpoints = [
        f'https://public-api.ortex.com/v1/equities/{symbol}/short-interest',
        f'https://public-api.ortex.com/v1/stocks/{symbol}/short-interest',
        f'https://api.ortex.com/v2/equities/{symbol}/short-interest',
        f'https://public-api.ortex.com/v2/equities/{symbol}/short-interest',
    ]

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }

    print("Testing Ortex API with TEST key")
    print(f"Symbol: {symbol}")
    print()

    for url in endpoints:
        print(f"Trying: {url}")

        try:
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, timeout=10) as response:
                status = response.status
                data = response.read().decode('utf-8')

                print(f"  ✓ Success! Status: {status}")
                print(f"  Response length: {len(data)} chars")

                # Check if it's HTML or JSON
                if data.strip().startswith('<!DOCTYPE') or data.strip().startswith('<html'):
                    print("  ✗ Got HTML response (wrong endpoint)")
                else:
                    # Try to parse as JSON
                    try:
                        json_data = json.loads(data)
                        print("  ✓ Valid JSON response!")
                        print(f"  Keys: {list(json_data.keys())}")
                        print(f"  Sample data: {str(json_data)[:200]}")
                        print()
                        print("=" * 60)
                        print("SUCCESS! This endpoint works:")
                        print(url)
                        print("=" * 60)
                        return True
                    except:
                        print("  ✗ Couldn't parse as JSON")
                print()

        except urllib.error.HTTPError as e:
            print(f"  ✗ HTTP Error {e.code}: {e.reason}")
            try:
                error_body = e.read().decode('utf-8')[:200]
                print(f"  Error response: {error_body}")
            except:
                pass
            print()

        except urllib.error.URLError as e:
            print(f"  ✗ URL Error: {e.reason}")
            print()

        except Exception as e:
            print(f"  ✗ Unexpected error: {type(e).__name__}: {str(e)}")
            print()

    print("=" * 60)
    print("No working endpoint found with TEST key")
    print("You may need a real API key from https://public.ortex.com/")
    print("=" * 60)
    return False

if __name__ == '__main__':
    test_ortex_api()
