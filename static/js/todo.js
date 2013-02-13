angular.module('Todo', ['ngResource']);

function TodoCtrl($scope, $resource) {
    $scope.priorities = ['high', 'normal', 'low'];

    var Todo = $resource(
        '/todo/:todoId', {'todoId': '@id'},
        {update: {method: 'PUT'}}
    );

    $scope.todos = Todo.query();

    $scope.max_id = 0;

    $scope.addTodo = function() {
        if($scope.todoText){
            var todo = {
                text: $scope.todoText,
                done: false,
                priority: 'normal'
            };
            if($scope.online){
                todo = new Todo(todo);
                todo.$save();
            }
            else{
                var todo_id = $scope.max_id + 1;
                $scope.max_id = todo_id;
                angular.extend(todo, {'id': todo_id});
            }

            $scope.todos.push(todo);
            $scope.todoText = '';
        }
    };

    $scope.findTodo = function(todo_id){
        var index = -1;
        var i;
        for(i=0;i<$scope.todos.length;++i){
            if ($scope.todos[i].id == todo_id){
                index = i;
            }
        }
        return index;
    };

    $scope.removeTodo = function(todo_id) {
        var index = $scope.findTodo(todo_id);
        if(index >= 0){
            if($scope.online){
                $scope.todos[index].$remove();
            }
            $scope.todos.splice(index, 1);
        }
    };

    $scope.setCurrentTodo = function(todo_id){
        $scope.todoEditIndex = $scope.findTodo(todo_id);
        $scope.oldTodo = angular.copy($scope.todos[$scope.todoEditIndex]);
    };

    $scope.updateTodo = function(todo_id){
        if($scope.online){
            if(todo_id){
                var index = $scope.findTodo(todo_id);
            }
            else{
                var index = $scope.todoEditIndex;
            }
            $scope.todos[index].$update();
        }
    };

    $scope.resetTodo = function(){
        angular.copy($scope.oldTodo, $scope.todos[$scope.todoEditIndex]);
    }

    $scope.priorityKey = function(todo){
        return $scope.priorities.indexOf(todo.priority);
    };
}

