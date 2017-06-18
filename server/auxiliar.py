#!/usr/bin/env python

import json
import os

def prepare_clusters(base_dir="../"):
    clusters = {
        "starter": [],
        "main": [],
        "dessert": []
    }
    filenames = ["../firsts.json","../seconds.json","../desserts.json"]
    for clustName,filename in zip(["starter","main","dessert"],filenames):
        with open(filename) as json_data:
            recipes = json.load(json_data)
            clusters[clustName].extend(list(recipes.keys()))
    return clusters
def getCluster(clusters, label):
    for cluster in ["starter","main","dessert"]:
        if label in clusters[cluster]:
            return cluster
    return "None"
def build_recipes_json(base_dir="../food"):
    all_recipes = []
    facts = set()
    clusters = prepare_clusters()
    # Read files
    for filename in os.listdir(base_dir):
        # print("Reading file "+filename)
        with open(base_dir + "/" + filename, encoding="utf-8") as json_data:
            print(filename)
            recipes_results = json.load(json_data)
            for hit in recipes_results["hits"]:
                recipe = hit["recipe"]
                simple = {
                    "label": recipe["label"],
                    "image": recipe["image"],
                    "source": recipe["source"],
                    "url": recipe["url"],
                    "dietLabels": recipe["dietLabels"],
                    "healthLabels": recipe["healthLabels"],
                    "ingredientLines": recipe["ingredientLines"],
                    "cluster": getCluster(clusters,recipe["label"])
                }
                facts = facts.union(recipe["dietLabels"]+recipe["healthLabels"])
                all_recipes.append(simple)
    with open("./recipes.json", "w") as json_file:
        json.dump(all_recipes, json_file)
    with open("./facts.json", "w") as facts_file:
        json.dump([{"name": fact} for fact in facts], facts_file)
    return all_recipes


build_recipes_json()

def build_ingredients_json(ingredidents_file="../ingredients.txt"):
    all_ingredients = []
    with open(ingredidents_file, encoding="utf-8") as ingredients:
        for line in ingredients:
            line = line.strip()
            ingredient = line.split()
            all_ingredients.append({
                "name": " ".join(ingredient[1:]),
                "frequency": int(ingredient[0]),
                "index": len(all_ingredients)
            })
    with open("./ingredients.json", "w") as json_file:
        json.dump(all_ingredients, json_file)
    return all_ingredients


build_ingredients_json()
