# -*- coding: utf-8 -*-
#
# Copyright 2016 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import re
import os.path
import fnmatch

# Import Salt libs
from salt.ext import six
from salt.exceptions import CommandExecutionError


class InputSanitizer(object):
    @staticmethod
    def trim(value):
        '''
        Raise an exception if value is empty. Otherwise strip it down.
        :param value:
        :return:
        '''
        value = (value or '').strip()
        if not value:
            raise CommandExecutionError("Empty value during sanitation")

        return six.text_type(value)

    @staticmethod
    def filename(value):
        '''
        Remove everything that would affect paths in the filename

        :param value:
        :return:
        '''
        return re.sub('[^a-zA-Z0-9.-_ ]', '', os.path.basename(InputSanitizer.trim(value)))

    @staticmethod
    def hostname(value):
        '''
        Clean value for RFC1123.

        :param value:
        :return:
        '''
        return re.sub(r'[^a-zA-Z0-9.-]', '', InputSanitizer.trim(value)).strip('.')

    id = hostname


clean = InputSanitizer()


def mask_args_value(data, mask):
    '''
    Mask a line in the data, which matches "mask".

    In case you want to put to the logs rosters or other data,
    but you certainly do not want to put there an actual IP address,
    passwords, user names etc.

    Note, this is working only when data is a single string,
    ready for print or dump to the log. Also, when the data is formatted
    as "key: value" in YAML syntax.

    :param data: String data, already rendered.
    :param mask: Mask that matches a single line

    :return:
    '''
    if not mask:
        return data

    out = []
    for line in data.split(os.linesep):
        if fnmatch.fnmatch(line.strip(), mask) and ':' in line:
            key, value = line.split(':', 1)
            out.append('{}: {}'.format(key.strip(), '** hidden **'))
        else:
            out.append(line)

    return '\n'.join(out)
