# inventory_analysis.py
def find_product_combinations(products, target_price, price_margin=10):
    """
    Find all unique pairs of products where the combined price is within
    the target_price ± price_margin range.

    Args:
        products: List of dictionaries with 'id', 'name', and 'price' keys
        target_price: The ideal combined price
        price_margin: Acceptable deviation from the target price

    Returns:
        List of dictionaries with product pairs and their combined price and price difference
    """
    if not isinstance(products, list) or len(products) < 2:
        return []

    # Drop invalid products and keep only those with numeric prices
    sanitized = [p for p in products if isinstance(p, dict) and
                 'id' in p and 'name' in p and isinstance(p.get('price'), (int, float))]
    if len(sanitized) < 2:
        return []

    # Sort by price to enable efficient range search
    sorted_products = sorted(sanitized, key=lambda p: p['price'])
    sorted_prices = [p['price'] for p in sorted_products]

    import bisect
    results = []
    found_pairs = set()  # store tuple of ordered IDs to prevent duplicates

    n = len(sorted_products)
    for i in range(n - 1):
        if i % 100 == 0:
            print(f"Processing product {i+1} of {n}")

        base = sorted_products[i]
        low_price = target_price - price_margin - base['price']
        high_price = target_price + price_margin - base['price']

        # Search range in sorted_prices for match candidates
        lo = bisect.bisect_left(sorted_prices, low_price, i + 1, n)
        hi = bisect.bisect_right(sorted_prices, high_price, i + 1, n)

        for j in range(lo, hi):
            candidate = sorted_products[j]
            if candidate['id'] == base['id']:
                continue

            combined_price = base['price'] + candidate['price']
            price_diff = abs(target_price - combined_price)

            if price_diff <= price_margin:
                pair_key = tuple(sorted((base['id'], candidate['id'])))
                if pair_key in found_pairs:
                    continue

                found_pairs.add(pair_key)
                results.append({
                    'product1': base,
                    'product2': candidate,
                    'combined_price': combined_price,
                    'price_difference': price_diff
                })

    # Sort by closeness to target, smaller difference first
    results.sort(key=lambda x: x['price_difference'])
    return results

# Example usage
if __name__ == "__main__":
    import time
    import random

    # Generate a large list of products
    print("Generating Product List")
    product_list = []
    for i in range(5000):
        product_list.append({
            'id': i,
            'name': f'Product {i}',
            'price': random.randint(5, 500)
        })

    # Measure execution time
    print(f"Finding product combinations for {len(product_list)} products")
    start_time = time.time()
    combinations = find_product_combinations(product_list, 500, 50)
    end_time = time.time()

    print(f"Found {len(combinations)} product combinations")
    print(f"Execution time: {end_time - start_time:.2f} seconds")