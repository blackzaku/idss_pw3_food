app = angular.module('IdssApp', ['ngMaterial']);


app.factory("recommend", ["$http", function ($http) {
    "use strict";

    $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";


    let recommend = {
        suggestions: {
            starter: [],
            main: [],
            dessert: []
        },

        facts: [],
        names: [],
        _names_lower: [],
        indexed: {},
        _tokens: {},
        selected: [],
        recipes: [],
        ingredients: []
    };

    recommend.suggest = function () {
        let data = {
            likes: [], dislikes: [],
            ingredients: [], no_ingredients: [],
            labels: [], no_labels: []
        };

        for (let recipe of recommend.selected) {
            if (recipe.liked === true) data.likes.push(recipe.label);
            if (recipe.liked === false) data.dislikes.push(recipe.label);
        }
        for (let ingredient of recommend.ingredients) {
            if (ingredient.include === "+") data.ingredients.push(ingredient.name);
            if (ingredient.include === "-") data.no_ingredients.push(ingredient.name);
        }
        for (let label of recommend.facts) {
            if (label.include === "+") data.labels.push(label.name);
            if (label.include === "-") data.no_labels.push(label.name);
        }

        if (data.labels.length === 0) data.labels = [];
        if (data.ingredients.length === 0) data.ingredients = [];


        $http({
            method: 'POST',
            url: '/suggest',
            data: data
        }).then(
            (response) => {
                console.log("Suggest response got:", response);
                let result = response.data;
                // We get three lists
                recommend.suggestions.starter = result.starters.map((dn) => recommend.indexed[dn]);
                recommend.suggestions.main = result.mains.map((dn) => recommend.indexed[dn]);
                recommend.suggestions.dessert = result.desserts.map((dn) => recommend.indexed[dn]);
            },
            (error) => console.error(error));
    };

    recommend.random = function (course, count = 10) {
        let list = [];
        for (let i = 0; i < count; i++) {
            let recipe;
            let c = 0;
            //TOOD: Fix this mess
            do{
              recipe = recommend.recipes[Math.floor(Math.random() * recommend.recipes.length)];
              c++;
            }while(recipe.cluster != course && c<150)
            list.push(recipe);
        }
        recommend.suggestions[course] = list;
    };

    recommend.load = function () {

        $http({
            method: 'GET',
            url: '/facts.json'
        }).then(
            (response) => recommend.facts = response.data,
            (error) => console.error(error));

        $http({
            method: 'GET',
            url: '/ingredients.json'
        }).then(
            (response) => recommend.ingredients = response.data,
            (error) => console.error(error));

        $http({
            method: 'GET',
            url: '/recipes.json'
        }).then(
            (response) => recommend.init(response.data),
            (error) => console.error(error));
    };

    recommend.init = function (recipes) {

        recommend.recipes = recipes;

        // Give just a random recommendation
        recommend.random("starter");
        recommend.random("main");
        recommend.random("dessert");

        recommend.recipes.forEach((recipe, index) => {
            let name = recipe.label;
            recommend.names.push(name);
            recommend._names_lower.push([name.trim().toLowerCase(), index]);
            recommend.indexed[name] = recipe; // Reference
            let parts = name.trim().toLowerCase().split(/\s+/gi);
            for (let part of parts) {
                if (recommend._tokens[part] === undefined) {
                    recommend._tokens[part] = [index]
                } else {
                    recommend._tokens[part].push(index);
                }
            }
        });

        recommend.names = recommend.recipes.map((r) => r.label);

        recommend.search = function (query, limit = 10) {
            let parts = query.trim().toLowerCase().split(/\s+/gi);
            if (parts.length > 0 && parts[0] !== "") {
                let filtered = [];
                let base = recommend._tokens[parts[0]];
                if (base === undefined) {
                    // Perform a stupid search
                    for (let pair of recommend._names_lower) {
                        let name = pair[0], index = pair[1];
                        if (!parts.find((p) => name.indexOf(p) === -1)) {
                            filtered.push(recommend.recipes[index]);
                        }
                        if (filtered.length === limit) break;
                    }
                } else {
                    let union = base, missing = [];
                    for (let i = 1; i < parts.length; i++) {
                        let part = parts[i];
                        let base = recommend._tokens[part];
                        if (base === undefined) {
                            missing.push(part)
                        } else {
                            union = base.filter((b) => union.indexOf(b) >= 0)
                        }
                    }
                    for (let index of union) {
                        let recipe = recommend.recipes[index], name = recipe.label;
                        if (!parts.find((p) => name.toLowerCase().indexOf(p) === -1)) {
                            filtered.push(recipe);
                        }
                        if (filtered.length === limit) break;
                    }
                }
                return filtered;
            } else {
                return [];
            }

        };
    };

    recommend.load();

    return recommend;
}]);

app.controller('FrontController', ["$scope", "recommend", function FrontController($scope, recommend) {


    $scope.recommend = recommend;

    $scope.addRecipe = function (recipe) {
        "use strict";
        if (!recommend.selected.find((r) => r.label === recipe.label)) {
            recommend.selected.push(recipe);
        }
    };


    $scope.ingredientFilter = "";
    $scope.toggleIngredient = (ingredient) => {
        "use strict";
        if (!ingredient.include) {
            ingredient.include = "+";
        } else if (ingredient.include === "+") {
            ingredient.include = "-";
        } else {
            ingredient.include = null;
        }
    };

    $scope.getSuggestions = () => {
        "use strict";
        recommend.suggest();
    }


}]);
