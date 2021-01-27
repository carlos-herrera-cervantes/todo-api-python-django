def parse_pages(query_params):
    """
    Return the value of pagination
    Parameters
    ----------
    query_params: dict
        Query parameters of request
    """
    page = 0 if query_params.get('page') == '1' else int(query_params.get('page')) - 1
    page_size = int(query_params.get('page_size'))
    return { 'page': page, 'page_size': page_size }

def get_paginate_object(query_params, total_docs):
    """
    Return paginate object
    Parameters
    ----------
    query_params: dict
        Query parameters of request
    total_docs: int
        Total documents
    """
    page = int(query_params.get('page'))
    page_size = int(query_params.get('page_size'))
    take = page * page_size
    subtracted_items = total_docs - take
    remaining_documents = 0 if subtracted_items < 0 else subtracted_items

    return {
        'page': page,
        'page_size': page_size,
        'remaining_documents': remaining_documents,
        'total_documents': total_docs
    }

def get_type_ordering_object(sort):
    """
    Return sort object
    Parameters
    ----------
    sort: str
        Property used to sort documents
    """
    is_ascending = '-' in sort
    property = sort.split('-').pop() if is_ascending else sort
    return { property: -1 if is_ascending else 1 }