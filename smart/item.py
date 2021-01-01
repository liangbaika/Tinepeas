# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      item
# Author:    liangbaikai
# Date:      2020/12/31
# Desc:      there is a python file description
# ------------------------------------------------------------------
from __future__ import annotations

from typing import Any

from smart.field import BaseField, RegexField, FuncField


class ItemMeta(type):
    """
    Metaclass for an item
    """

    def __new__(cls, name, bases, attrs):
        __fields = dict(
            {
                (field_name, attrs.pop(field_name))
                for field_name, object in list(attrs.items())
                if isinstance(object, BaseField)
            }
        )
        attrs["__fields"] = __fields
        new_class = type.__new__(cls, name, bases, attrs)
        return new_class


class Item(metaclass=ItemMeta):
    """
    Item class for each item
    """

    def __init__(self, source):
        self.__source = source
        results = self.__get_item() or {}
        self.__dict__.update(results)

    def to_dict(self):
        dict___items = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return dict___items

    def extract(self, key, other_source):
        if not key or not other_source:
            return None
        cls = self.__class__
        fields = getattr(cls, "__fields")
        if key not in fields.keys():
            return None
        for k, v in fields.items():
            if isinstance(v, BaseField):
                value = v.extract(other_source)
                self.__dict__.update(key=value)
                return value

    def __get_item(
            self,
    ) -> Any:
        cls = self.__class__
        fields = getattr(cls, "__fields")
        dict = {}
        for k, v in fields.items():
            if isinstance(v, BaseField):
                value = v.extract(self.__source)
            else:
                value = v
            dict.setdefault(k, value)
        for k, v in cls.__dict__.items():
            if k.startswith("_"):
                continue
            dict.setdefault(k, v)
        return dict

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if key in self.__dict__.keys():
            self.__dict__[key] = value
        else:
            raise KeyError("%s does not support field: %s" %
                           (self.__class__.__name__, key))
