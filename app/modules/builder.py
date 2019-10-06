"""
This module is a builder for schemas that are specified in json file
It maps json objects to QTreeWidgetItem along with its type information.
Even with complex schema it should be able to create QTreeWidgetItems since
it works recursively on tree elements.

transform_complex_element_to_tree_item should be enough to parse any json
schema to create an underlying tree representation of a tree widget
"""
# Author: Kaan Eraslan
# License: see, LICENSE

from PySide2.QtWidgets import QTreeWidgetItem
from collections import namedtuple


class ItemObj(QTreeWidgetItem):
    "tree item object"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_type = None

    def set_value_type(self, val):
        "Set text type to item"
        self.value_type = type(val)

    def get_value_type(self):
        "return text type"
        return self.value_type


def check_simple_value(val) -> bool:
    "Check if value is float, int, str, bool, none"
    if (isinstance(val, str) or
        isinstance(val, int) or
        isinstance(val, float) or
        isinstance(val, bool) or
            isinstance(val, None)):
        return True
    else:
        return False


def transform_val_to_tree_item(val) -> QTreeWidgetItem:
    """
    Transform key value to tree item

    Parameters
    -----------
    val: value or text value of the widget item

    Returns
    --------
    item: tree widget item that represents the key value
    """
    assert check_simple_value(val)
    item = ItemObj()
    item.setText(str(val))
    item.set_value_type(val)
    return item


def transform_simple_val_to_tree_item(name: str, val) -> QTreeWidgetItem:
    """
    Transform simple val with its name to tree widget item
    """
    assert isinstance(name, str)
    assert check_simple_value(val)
    item = transform_val_to_tree_item(name)
    vitem = transform_val_to_tree_item(val)
    item.addChild(vitem)
    return item


def check_simple_list(values: list) -> bool:
    "Check if list contains only str, int, float, bool, none"
    if (isinstance(val, list) or isinstance(val, tuple)):
        for val in values:
            if not check_simple_value(val):
                return False
        return True
    else:
        return False


def transform_simple_list_to_tree_item(val: list,
                                       name: str) -> QTreeWidgetItem:
    """
    Transform list value to tree item

    Parameters
    -----------
    val: a collection value that contains other elements

    Returns
    --------
    item
    """
    assert check_simple_list(val)
    assert isinstance(name, str)
    item = ItemObj()
    item.setText(name)
    item.set_value_type(val)
    for v in val:
        vitem = transform_val_to_tree_item(v)
        item.addChild(vitem)
    return item


def check_simple_dict(dictval: dict):
    "Check whether dictionary is simple."
    if isinstance(dictval, dict):
        for key, val in dictval.items():
            if not check_simple_list(val) or not check_simple_value(val):
                return False
        return True
    else:
        return False


def transform_simple_dict_to_tree_item(val: dict,
                                       name: str) -> QTreeWidgetItem:
    """
    Transform simple dictionary to tree widget

    Parameters
    -----------
    val: simple dictionary having key values, who are simple dictionaries
    name: text of the item
    """
    assert isinstance(name, str)
    assert check_simple_dict(val)
    item = ItemObj()
    item.set_value_type(val)
    item.setText(name)
    for key, vs in val.items():
        if check_simple_value(vs):
            vitem = transform_simple_val_to_tree_item(key, vs)
        elif check_simple_list(vs):
            vitem = transform_simple_list_to_tree_item(key, vs)
        item.addChild(vitem)
    return item


def check_simple_element(value) -> bool:
    "Check whether value is a simple dict, list, val"
    return bool(check_simple_value(value) or check_simple_list(value) or
                check_simple_dict(value))


def transform_simple_element_to_tree_item(name: str, value) -> QTreeWidgetItem:
    """
    Transform given value to tree item
    """
    assert isinstance(name, str)
    assert check_simple_element(value)
    if check_simple_value(value):
        vitem = transform_simple_val_to_tree_item(name, value)
    elif check_simple_list(value):
        vitem = transform_simple_list_to_tree_item(name, value)
    elif check_simple_dict(value):
        vitem = transform_simple_dict_to_tree_item(name, value)
    else:
        raise ValueError("Unknown simple element: " + str(value))
    #
    return vitem


def transform_complex_element_to_tree_item(name: str,
                                           value) -> QTreeWidgetItem:
    "Transform complex element to tree item"
    if check_simple_element(value):
        return transform_simple_element_to_tree_item(name, value)
    #
    item = ItemObj()
    item.setText(name)
    item.set_value_type(value)
    if isinstance(value, dict):
        for key, val in value.items():
            item.addChild(transform_complex_element_to_tree_item(key, val))
    elif isinstance(value, list) or isinstance(value, tuple):
        item.addChild(transform_complex_element_to_tree_item(name, val))
    return item


def check_schema(schema: dict):
    "Check schema for having several attributes"
    if "type" not in schema:
        mess = "Schema does not contain a type field."
        mess += " Type field is required for defining model type."
        mess += " Please change your schema file accordingly"
        raise ValueError(mess)
    model_name = schema["type"]
    if model_name != "Entry" and model_name != "Dictionary":
        mess = "Specified schema type: " + model_name
        mess += " is not supported only Entry and Dictionary"
        mess += " are supported as schema types. If your schema"
        mess += " is conceptually equivalent to that of Entry or Dictionary"
        mess += " please specify in type field the equivalent entity: Entry"
        mess += " , Dictionary, and save your old value to a different field."
        raise ValueError(mess)
    if "name" not in schema:
        mess = "Please specify a name field with a unique value for your"
        mess += " schema to distinguish it"
        raise ValueError(mess)


def model_builder(schema: dict):
    "Build model from given schema dict"
    check_schema(schema)
    model_name = schema["type"]
    model_name += model_name + "Model"
    keys = [k for k in schema.keys()]
    bad_keys = []
    for k in keys:
        if not all([c in
                    ["wxcvbnqsdfghjklmazertyuiopWXCVBNQSDFGHJKLMAZERTYUIOP0123456789"]
                    for c in k
                    ]):
            bad_keys.append(k)
    #
    if bad_keys:
        mess = "Some of the key names are not supported please correct them,"
        mess += " so that they don't have any special characters as well as"
        mess += " space. They should not start with a number as well."
        raise ValueError(mess)
    return namedtuple(model_name, keys)
