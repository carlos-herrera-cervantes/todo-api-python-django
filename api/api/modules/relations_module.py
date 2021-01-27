def get_relation_by_model(model):
    """
    Returns the function to get relations by model
    Parameters
    ----------
    model: str
        Model name
    """
    switcher = {
        'user': get_relations_for_user(),
        'todo': get_relations_for_todo()
    }

    return switcher.get(model)

def get_relations_for_user():
    """
    Returns the dictionary with the models relationship of user
    """
    return {
        'todo': {
            'localField': '_id',
            'foreignField': 'user_id',
            'as': 'todos'
        }
    }

def get_relations_for_todo():
    """
    Returns the dictionary with the models relationship of todo
    """
    return {
        'user': {
            'localField': 'user_id',
            'foreignField': '_id',
            'as': 'user'
        }
    }