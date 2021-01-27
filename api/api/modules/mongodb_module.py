from .relations_module import get_relation_by_model

def build_lookup_filter(references, model):
    """
    Returns the lookups objects for the model
    Parameters
    ----------
    references: dict
        Dictionary with the names of models of the relationship
    model: str
        Model name
    """
    entities = references.split(',')
    keys_relations = get_relation_by_model(model)
    pipeline = []

    for entity in entities:
        selected = keys_relations.get(entity)
        pipeline.append(
            {
                '$lookup': {
                    'from': entity,
                    'localField': selected['localField'],
                    'foreignField': selected['foreignField'],
                    'as': selected['as']
                }
            })

    return pipeline

def build_paginate_filter(skip, limit, pipeline):
    """
    Returns the paginate filter for aggregation pipeline
    Parameters
    ----------
    skip: int
        The number of documents to ommit
    limit: int
        The limit documents to return
    pipeline: array
        The dictionaries of pipeline
    """
    pipeline.append({ '$skip': skip })
    pipeline.append({ '$limit': limit })
    return pipeline

def build_sort_filter(sort, pipeline):
    """
    Returns the sort filter for aggregation pipeline
    Parameters
    ----------
    property: str
        Property that's indicate the type of ordering
    """
    pipeline.append({ '$sort': sort })
    return pipeline