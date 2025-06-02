def clean_countries_full(data):
    result = []
    rejected = []
    seen_cca3 = set()

    for country in data:
        try:
            cca3 = country.get("cca3")
            if not cca3 or cca3 in seen_cca3:
                rejected.append({"reason": "missing or duplicate cca3", "raw": country})
                continue

            name = country.get("name", {}).get("common")
            if not name:
                rejected.append({"reason": "missing name", "raw": country})
                continue

            region = country.get("region")
            subregion = country.get("subregion")
            population = country.get("population", 0)
            area = country.get("area", 0.0)
            capital = country.get("capital", [])

            if isinstance(capital, str):
                capital = [capital]
            elif capital is None:
                capital = []

            result.append({
                "cca3": cca3,
                "name": name,
                "region": region,
                "subregion": subregion,
                "population": population,
                "area": area,
                "capital": capital
            })

            seen_cca3.add(cca3)
        except Exception as e:
            rejected.append({"reason": str(e), "raw": country})

    return result, rejected
