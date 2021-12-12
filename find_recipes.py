import requests


def find_recipes(ingredients):
    il = ""
    for i in ingredients:
        il += i + ","
    il = il[:-1]

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "needsimage": 1,
        "app": 1,
        "kitchen": il,
        "focus": "",
        "kw": il,
        "catname": "",
        "start": 0,
        "fave": "false",
        "expand_kw": 1,
        "sort": "relevance",
        "lang": "en",
    }
    url = "https://d1.supercook.com/dyn/results"

    response = requests.post(url, data=data, headers=headers)
    content = response.json()["results"]
    recipes = []

    for recipe in content:
        website = recipe["domain"]
        img_link = recipe["img"]
        title = recipe["title"]
        ingredients_used = recipe["uses"]
        recipes.append({"website": website, "img_link": img_link, "title": title, "ingredients_used": ingredients_used})

    return recipes
