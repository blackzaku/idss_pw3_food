import json

filename = "recipes.json"
with open(filename) as json_data:
    recipes = json.load(json_data)

names = [label for label, recipe in recipes.items()]


class IdssFood:
    # Carlos: Define the clusters, just a list
    CLUSTERS = {
        "starters": [],
        "mains": [],
        "desserts": []
    }
    NAMES = names
    RECIPES = recipes

    def __init__(self):
        self.liked = []
        self.disliked = []

        self.labels = None  # AND
        self.no_labels = []  # AND

        self.ingredients = None  # OR
        self.no_ingredients = []  # AND

    def set_liked(self, liked=(), disliked=()):
        self.liked = self.label2index(liked)
        self.disliked = self.label2index(liked)

    def set_labels(self, labels=None, no_labels=()):
        self.labels = labels
        self.no_labels = no_labels

    def set_ingredients(self, ingredients=None, no_ingredients=()):
        self.ingredients = ingredients
        self.no_ingredients = no_ingredients

    def get_closest_to_liked(self, cluster=None):
        # Marti: Use k-nearest neighbours having into account the valid clusters
        return [0, 1, 2, 3, 4, 5, 6, 7, 9]

    def filter(self, closest):
        # Nariman: Use labels, no_labels and ingredients and no_ingredients to filter out
        return closest

    def rank(self, closest):
        # Nariman: Use disliked dishes to rank
        return closest

    def index2label(self, list):
        return [IdssFood.NAMES[index] for index in list]

    def label2index(self, list):
        return [IdssFood.NAMES.index(label) for label in list]

    def get_recommendation(self, clusters=("starters", "mains", "desserts")):
        recommendations = {"starters": None, "mains": None, "desserts": None}
        for cluster in clusters:
            recipes = self.get_closest_to_liked(cluster)
            recipes = self.filter(recipes)
            recipes = self.rank(recipes)
            recommendations[cluster] = self.index2label(recipes)
        return recommendations
