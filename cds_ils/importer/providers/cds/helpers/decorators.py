# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML rules utils."""
import functools

from dojson.errors import IgnoreKey


def replace_in_result(phrase, replace_with, key=None):
    """Replaces string values in list with given string."""

    def the_decorator(fn_decorated):
        def proxy(*args, **kwargs):
            res = fn_decorated(*args, **kwargs)
            if res:
                if not key:
                    return [k.replace(phrase, replace_with).strip() for k in res]
                else:
                    return [
                        dict(
                            (
                                k,
                                (
                                    v.replace(phrase, replace_with).strip()
                                    if k == key
                                    else v
                                ),
                            )
                            for k, v in elem.items()
                        )
                        for elem in res
                    ]
            return res

        return proxy

    return the_decorator


def filter_list_values(f):
    """Remove None and blank string values from list of dictionaries."""

    @functools.wraps(f)
    def wrapper(self, key, value, **kwargs):
        out = f(self, key, value)
        if out:
            clean_list = [
                dict((k, v) for k, v in elem.items() if v) for elem in out if elem
            ]
            clean_list = [elem for elem in clean_list if elem]
            if not clean_list:
                raise IgnoreKey(key)
            return clean_list
        else:
            raise IgnoreKey(key)

    return wrapper


def out_strip(fn_decorated):
    """Decorator cleaning output values of trailing and following spaces."""

    def proxy(self, key, value, **kwargs):
        res = fn_decorated(self, key, value, **kwargs)
        if not res:
            raise IgnoreKey(key)
        if isinstance(res, str):
            # the value is not checked for empty strings here because clean_val
            # does the job, it will be None caught before
            return res.strip()
        elif isinstance(res, list):
            cleaned = [elem.strip() for elem in res if elem]
            if not cleaned:
                raise IgnoreKey(key)
            return cleaned
        else:
            return res

    return proxy


def filter_empty_dict_values(f):
    """Remove None values from dictionary."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        out = f(*args, **kwargs)
        return dict((k, v) for k, v in out.items() if v)

    return wrapper
