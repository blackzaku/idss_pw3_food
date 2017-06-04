app = angular.module('IdssApp', ['ngMaterial']);


app.factory("recommend", ["$http", function ($http) {
    "use strict";



    let recommend = {
        names: [],
        _names_lower: [],
        indexed: {},
        _tokens: {},
        selected: [],
        recipes: [],
        ingredients: []
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

    recommend.init = function(recipes) {

        recommend.recipes = recipes;

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

    $scope.removeRecipe = (recipe) => {
        "use strict";
        let index = recommend.selected.findIndex((r) => r.label === recipe.label);
        recommend.selected.splice(index, 1);
    };


    $scope.ingredientFilter="";
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

    $scope.openMenu = ($mdMenu, ev) => {
        "use strict";
        $mdMenu.open(ev);
    };

    $scope.setLiked = (recipe, liked) => {
        recipe.liked = liked;
    };

}]);
