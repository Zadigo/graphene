from typing import Any, Sequence


class InvalidMetaOptionsError(TypeError):
    message = "Invalid options provided in Meta class: {invalid_keys}. Valid options are: {valid_keys}"

    def __init__(self, invalid_keys: Sequence[str], valid_keys: Sequence[str]):
        super().__init__(self.message.format(invalid_keys=invalid_keys, valid_keys=valid_keys))


class GrapheneObjectTypeError(TypeError):
    message = "Expected a Graphene ObjectType or a subclass of ObjectType, got {value_type} without a name"

    def __init__(self, value: Any):
        super().__init__(self.message.format(value_type=type(value).__name__))
