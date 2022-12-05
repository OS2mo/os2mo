# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
def import_class(name):
    components = name.split(".")
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


# https://stackoverflow.com/questions/3405715/elegant-way-to-remove-fields-from-nested-dictionaries
def delete_keys_from_dict(dict_del, lst_keys):
    """
    Delete the keys present in lst_keys from the dictionary.
    Loops recursively over nested dictionaries.
    """
    dict_foo = dict_del.copy()  # to avoid the 'DictionaryHasChanged' error
    for field in dict_foo.keys():
        if field in lst_keys:
            del dict_del[field]
        if type(dict_foo[field]) == dict:
            delete_keys_from_dict(dict_del[field], lst_keys)
    return dict_del
