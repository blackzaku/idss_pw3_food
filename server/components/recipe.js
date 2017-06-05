app.component('recipe', {
    bindings: {
        recipe: '=',
        suggestion: '<',
        header: '@?',
        headerColor: '@?'
    },
    templateUrl: '/components/recipe.html',
    controller: function RecipeSearchController($scope, recommend) {
        "use strict";

        $scope.recommend = recommend;

        $scope.openMenu = ($mdMenu, ev) => {
            "use strict";
            $mdMenu.open(ev);
        };

        $scope.addRecipe = function (recipe) {
            "use strict";
            if (!recommend.selected.find((r) => r.label === recipe.label)) {
                recommend.selected.push(recipe);
            }
        };


        $scope.setLiked = (recipe, liked) => {
            $scope.addRecipe(recipe);
            recipe.liked = liked;
        };


        $scope.removeRecipe = (recipe) => {
            "use strict";
            let index = recommend.selected.findIndex((r) => r.label === recipe.label);
            recommend.selected.splice(index, 1);
        };

        $scope.setAs = (recipe, course) => {
            if (!recommend.suggestions[course].find((r) => r.label === recipe.label)) {
                recommend.suggestions[course].unshift(recipe);
            }
        };

        $scope.skipSuggestion = (course) => {
            let list = recommend.suggestions[course];
            if (list.length === 1) {
                alert("No more alternatives, please refresh the tree course meal.")
            } else {
               list.shift();
            }
        }

    }
});