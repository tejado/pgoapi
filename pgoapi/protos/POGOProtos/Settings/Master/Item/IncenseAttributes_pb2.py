# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: POGOProtos/Settings/Master/Item/IncenseAttributes.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from POGOProtos.Enums import PokemonType_pb2 as POGOProtos_dot_Enums_dot_PokemonType__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='POGOProtos/Settings/Master/Item/IncenseAttributes.proto',
  package='POGOProtos.Settings.Master.Item',
  syntax='proto3',
  serialized_pb=_b('\n7POGOProtos/Settings/Master/Item/IncenseAttributes.proto\x12\x1fPOGOProtos.Settings.Master.Item\x1a\"POGOProtos/Enums/PokemonType.proto\"\xd2\x02\n\x11IncenseAttributes\x12 \n\x18incense_lifetime_seconds\x18\x01 \x01(\x05\x12\x33\n\x0cpokemon_type\x18\x02 \x03(\x0e\x32\x1d.POGOProtos.Enums.PokemonType\x12(\n pokemon_incense_type_probability\x18\x03 \x01(\x02\x12\x30\n(standing_time_between_encounters_seconds\x18\x04 \x01(\x05\x12-\n%moving_time_between_encounter_seconds\x18\x05 \x01(\x05\x12\x35\n-distance_required_for_shorter_interval_meters\x18\x06 \x01(\x05\x12$\n\x1cpokemon_attracted_length_sec\x18\x07 \x01(\x05\x62\x06proto3')
  ,
  dependencies=[POGOProtos_dot_Enums_dot_PokemonType__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_INCENSEATTRIBUTES = _descriptor.Descriptor(
  name='IncenseAttributes',
  full_name='POGOProtos.Settings.Master.Item.IncenseAttributes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='incense_lifetime_seconds', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.incense_lifetime_seconds', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pokemon_type', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.pokemon_type', index=1,
      number=2, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pokemon_incense_type_probability', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.pokemon_incense_type_probability', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='standing_time_between_encounters_seconds', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.standing_time_between_encounters_seconds', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='moving_time_between_encounter_seconds', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.moving_time_between_encounter_seconds', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='distance_required_for_shorter_interval_meters', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.distance_required_for_shorter_interval_meters', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pokemon_attracted_length_sec', full_name='POGOProtos.Settings.Master.Item.IncenseAttributes.pokemon_attracted_length_sec', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=129,
  serialized_end=467,
)

_INCENSEATTRIBUTES.fields_by_name['pokemon_type'].enum_type = POGOProtos_dot_Enums_dot_PokemonType__pb2._POKEMONTYPE
DESCRIPTOR.message_types_by_name['IncenseAttributes'] = _INCENSEATTRIBUTES

IncenseAttributes = _reflection.GeneratedProtocolMessageType('IncenseAttributes', (_message.Message,), dict(
  DESCRIPTOR = _INCENSEATTRIBUTES,
  __module__ = 'POGOProtos.Settings.Master.Item.IncenseAttributes_pb2'
  # @@protoc_insertion_point(class_scope:POGOProtos.Settings.Master.Item.IncenseAttributes)
  ))
_sym_db.RegisterMessage(IncenseAttributes)


# @@protoc_insertion_point(module_scope)
