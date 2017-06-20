import json
import numpy as np
from scipy.spatial.distance import euclidean as distance_
from scipy.stats import pearsonr
from sklearn.neighbors import NearestNeighbors
from collections import OrderedDict

dimensions_ingredients = 702
dimensions_nutrition_facts = 22
number_of_clusters=100
number_of_dishes =5326

filenames = ["../firsts.json","../seconds.json","../desserts.json"]
X = np.zeros([number_of_dishes, dimensions_ingredients+dimensions_nutrition_facts])
index = 0
labels = {}
names = []
clusters = {
    "starters": [],
    "mains": [],
    "desserts": []
}
for clustName,filename in zip(["starters","mains","desserts"],filenames):
    with open(filename) as json_data:
        recipes = json.load(json_data)
        names +=list(recipes.keys())
        for label, recipe in recipes.items():
            for ingredient in recipe["ingredients"]:
                X[index, ingredient[0]] = ingredient[1]
            for fact in recipe["nutrition"]:
                X[ index, dimensions_ingredients + fact[0] ] = fact[1]
            clusters[clustName].append(index)
            labels[index] = recipe["healthLabels"]
            index+=1
    print("File "+filename+" was successfully read")
#names = [label for label, recipe in recipes.items()]

def getPearson(a,b,**kwargs):
    #Remove one to make the maximum on 0 for the knn to work
    return pearsonr(a,b)[0]-1
class IdssFood:
    # Carlos: Define the clusters, just a list
    CLUSTERS = clusters
    NAMES = names
    RECIPES = recipes
    LABELS = labels
    X_ = X
    SALIENCY = 0.5


    def __init__(self):
        self.liked = []
        self.disliked = []

        self.labels = None  # AND
        self.no_labels = []  # AND

        self.ingredients = None  # OR
        self.no_ingredients = []  # AND

        self.nbrs = NearestNeighbors(n_neighbors=40, algorithm='ball_tree',metric=getPearson).fit(self.X_[:,:dimensions_ingredients])

    def set_liked(self, liked=[], disliked=[]):
        self.liked = self.label2index(liked)
        self.disliked = self.label2index(disliked)

    def set_labels(self, labels=None, no_labels=()):
        self.labels = labels
        self.no_labels = no_labels

    def set_ingredients(self, ingredients=None, no_ingredients=()):
        self.ingredients = ingredients
        self.no_ingredients = no_ingredients

    def get_closest_to_liked(self, cluster=None):
        # Marti: Use k-nearest neighbours having into account the valid clusters
        candidates = []
        distances = []
        for item in self.liked:
            dist,ind = self.nbrs.kneighbors(self.X_[item,:dimensions_ingredients].reshape(1, -1))
            #The first item is itself
            dist = dist[0][1:]
            std = self.SALIENCY*np.std(dist)
            dist=(dist+std)**2
            candidates.extend(ind[0][1:])
            distances.extend(dist)
        todel = []
        for ind,candidate in enumerate(candidates):
            if not candidate in IdssFood.CLUSTERS[cluster]:
                todel+=[ind]
        for ind in sorted(todel,reverse=True):
            del distances[ind]
            del candidates[ind]
        distind= np.argsort(distances)
        distind=list(OrderedDict.fromkeys(distind))
        candidates = np.array(candidates)[distind[:10]]
        return list(candidates)

    def filter(self, closest):
        # Nariman: Use labels, no_labels and ingredients and no_ingredients to filter out
        remove_list = []
        for index in closest:
            #labels filtering
            for label in  self.LABELS[index]:
                if label in self.no_labels:
                    remove_list += [index]
            for label in  self.labels:
                if label not in self.LABELS[index]:
                    remove_list += [index]
            #ingredients filtering            ###this is based on having X but it can easily changed to get from json file directly if needed.
            for ingredient in  self.no_ingredients:
                if self.X_[index,ingredient]:
                    remove_list += [index]
            for ingredient in  self.ingredients:
                if self.X_[index,ingredient]==0:
                    remove_list += [index]
        for item in set(remove_list):
            closest.remove(item)
        for item in self.disliked+self.liked:
            if item in closest:
                closest.remove(item)
        return closest

    def rank(self, closest,utility = 0): # utility=0:OWA, utility=1:meanstd
        # Nariman: Use disliked dishes to rank
        #first approach: utility function => mean-std
        L = len(closest)
        X_ingredients = self.X_[:,0:dimensions_ingredients]

        if utility==1:
            dist_list = []
            for i in range(L):
                temp = []
                for dish in self.disliked:
                    temp.append( distance_(X_ingredients[int(dish),:],X_ingredients[int(closest[i]),:]) )
                dist_list.append(temp)
            rank_list = []
            for index in range(len(dist_list)):
                rank = 1*np.mean(dist_list[index])-1*np.std(dist_list[index])
                rank_list.append([rank, index])
            rank_list.sort(reverse=True)
            closest_temp = []
            for i in range(0,len(closest)):
                closest_temp.append(closest[int(rank_list[i][1])])
            closest = closest_temp
            return closest
        #second approach: utility function => OWA :  more weight for closer distances to dislike
        dist_list = []
        for i in range(L):
            temp = []
            for dish in self.disliked:
                temp.append( distance_(X_ingredients[int(dish),:],X_ingredients[int(closest[i]),:]) )
            dist_list.append([temp,i])
        L = len(closest)
        OWAweights = []
        if L != 1:
            for w in range(len(self.disliked)):
                OWAweights.append(2*(w+1)/((len(self.disliked))*((len(self.disliked))+1)))
        else: OWAweights = [1]
        rank_list_ = []
        dist_list.sort(reverse=True)
        for index in range(L):
            rank_ = sum(np.multiply(dist_list[index][0], OWAweights))
            rank_list_.append([rank_,dist_list[index][1]])
        rank_list_.sort(reverse=True)
        closest_temp_ = []
        for i in range(L):
            closest_temp_.append(closest[int(rank_list_[i][1])])
        closest = closest_temp_
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
