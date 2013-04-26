:: # Copyright 2013, Big Switch Networks, Inc.
:: #
:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
:: # the following special exception:
:: #
:: # LOXI Exception
:: #
:: # As a special exception to the terms of the EPL, you may distribute libraries
:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
:: # from the LoxiGen Libraries and the notice provided below is (i) included in
:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
:: # documentation for the LoxiGen Libraries, if distributed in binary form.
:: #
:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
:: #
:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
:: # a copy of the EPL at:
:: #
:: # http://www.eclipse.org/legal/epl-v10.html
:: #
:: # Unless required by applicable law or agreed to in writing, software
:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
:: # EPL for the specific language governing permissions and limitations
:: # under the EPL.
::
:: import itertools
:: import of_g
:: include('_copyright.py')

:: include('_autogen.py')

import struct
import const
import util
import loxi.generic_util
import loxi

def unpack_list(buf):
    if len(buf) % 8 != 0: raise loxi.ProtocolError("action list length not a multiple of 8")
    def deserializer(buf):
        type, length = struct.unpack_from("!HH", buf)
        if length % 8 != 0: raise loxi.ProtocolError("action length not a multiple of 8")
        parser = parsers.get(type)
        if not parser: raise loxi.ProtocolError("unknown action type %d" % type)
        return parser(buf)
    return loxi.generic_util.unpack_list(deserializer, "!2xH", buf)

class Action(object):
    type = None # override in subclass
    pass

:: for ofclass in ofclasses:
:: include('_ofclass.py', ofclass=ofclass, superclass="Action")

:: #endfor

:: if version == of_g.VERSION_1_0:
def parse_vendor(buf):
:: else:
def parse_experimenter(buf):
:: #endif
    if len(buf) < 16:
        raise loxi.ProtocolError("experimenter action too short")

    experimenter, = struct.unpack_from("!L", buf, 4)
    if experimenter == 0x005c16c7: # Big Switch Networks
        subtype, = struct.unpack_from("!L", buf, 8)
    elif experimenter == 0x00002320: # Nicira
        subtype, = struct.unpack_from("!H", buf, 8)
    else:
        raise loxi.ProtocolError("unexpected experimenter id %#x" % experimenter)

    if subtype in experimenter_parsers[experimenter]:
        return experimenter_parsers[experimenter][subtype](buf)
    else:
        raise loxi.ProtocolError("unexpected BSN experimenter subtype %#x" % subtype)

parsers = {
:: sort_key = lambda x: x.type_members[0].value
:: msgtype_groups = itertools.groupby(sorted(ofclasses, key=sort_key), sort_key)
:: for (k, v) in msgtype_groups:
:: v = list(v)
:: if len(v) == 1:
    ${k} : ${v[0].pyname}.unpack,
:: else:
    ${k} : parse_${k[12:].lower()},
:: #endif
:: #endfor
}

:: experimenter_ofclasses = [x for x in ofclasses if x.type_members[0].value == 'const.OFPAT_VENDOR']
:: sort_key = lambda x: x.type_members[1].value
:: experimenter_ofclasses.sort(key=sort_key)
:: grouped = itertools.groupby(experimenter_ofclasses, sort_key)
experimenter_parsers = {
:: for (experimenter, v) in grouped:
    ${experimenter} : {
:: for ofclass in v:
        ${ofclass.type_members[2].value}: ${ofclass.pyname}.unpack,
:: #endfor
    },
:: #endfor
}
