app.component('recipeSearch', {
    bindings: {
        recipeSelected: '&'
    },
  templateUrl: '/components/recipeSearch.html',
  controller: function RecipeSearchController($scope, recommend) {

    $scope.selectedItem = null;
    $scope.searchText = "";
    $scope.names = null;


    $scope.auxSelectedItemChange = (selected) => {
        "use strict";
        if (!!selected) {
            this.recipeSelected({recipe:selected});
        }
        $scope.selectedItem = null;
    };


    $scope.querySearch = (query) => {
        let result =  recommend.search(query);
        return result;
    };

  }
});