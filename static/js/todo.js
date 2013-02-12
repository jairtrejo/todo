angular.module('Todo', ['ngResource']);

function TodoCtrl($scope, $resource) {
    $scope.priorities = ['high', 'normal', 'low'];
    $scope.todos = [];

    var Todo = $resource(
        '/todo/:todoId', {'todoId': '@id'},
        {update: {method: 'PUT'}}
    );

    var getMaxTodoId = function(todos){
        var max_id = -1;
        var todo_id = -1;
        for(var i=0;i<todos.length;++i){
            todo_id = todos[i].id;
            if (todo_id > max_id){
                max_id = todo_id;
            }
        }
        return max_id;
    }

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
                var todo_id = getMaxTodoId($scope.todos) + 1;
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
                var todo = new Todo($scope.todos[index]);
                todo.$remove();
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
            var todo = $scope.todos[index];
            todo = new Todo(todo);
            todo.$update();
            $scope.todos[$scope.todoEditIndex] = todo;
        }
    };

    $scope.resetTodo = function(){
        angular.copy($scope.oldTodo, $scope.todos[$scope.todoEditIndex]);
    }

    $scope.priorityKey = function(todo){
        return $scope.priorities.indexOf(todo.priority);
    };
}

