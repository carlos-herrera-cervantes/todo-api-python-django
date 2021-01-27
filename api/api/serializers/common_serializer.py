from datetime import datetime
    
def default(dict):
    """
    Serializer the fields that not contain a correct format
    Parameters
    ----------
    dict: dict
        Dictionary with fields
    """
    if '_id' in dict.keys():
        dict['id'] = dict['_id']['$oid']

    if 'created_at' in dict.keys():
        dict['created_at'] = datetime.fromtimestamp(dict['created_at']['$date'] / 1000).isoformat()
        dict['updated_at'] = datetime.fromtimestamp(dict['updated_at']['$date'] / 1000).isoformat()

    dict.pop('_id', None)
    dict.pop('password', None)

    return dict