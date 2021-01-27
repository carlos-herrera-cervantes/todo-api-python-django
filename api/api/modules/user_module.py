async def add_todo_to_user(self, user_id, todo_id, request):
    """
    Add todo ID into the todos of user
    Parameters
    ----------
    user_id: str
        User ID
    todo_id: str
        ToDo ID
    request: dict
        Object request
    """
    user = await self.user_repository.get_by_id(user_id, request.GET)
    todo_ids = user['todos']
    todo_ids.append(todo_id)
    todos = { 'todos': todo_ids }
    await self.user_manager.update(user_id, todos)

async def delete_todo_of_user(self, user_id, todo_id, request):
    """
    Remove the ID of ToDo from the user's ToDos
    Parameters
    ----------
    user_id: str
        User ID
    todo_id: str
        ToDo ID
    request: dict
        Object request
    """
    user = await self.user_repository.get_by_id(user_id, request.GET)
    todo_ids = user['todos']
    todo_ids.remove(todo_id)
    todos = { 'todos': todo_ids }
    await self.user_manager.update(user_id, todos)