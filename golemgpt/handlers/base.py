from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from typing import Any, Generic, Type, TypeVar


class BaseParams(BaseModel):
    # Allow extra parameters just in case as we might want
    # to handle LLMs impercisions.
    model_config = ConfigDict(extra="allow")


P = TypeVar("P", bound=BaseParams)


class BaseOutput(BaseModel):
    """
    Represents the output of an action.

    Attributes:

        - result (str): The successfully serialized result from the LLM.
        - error_feedback (str, optional): Feedback for the LLM to consider
          for potential retry. Defaults to an empty string.
    """

    result: str
    error_feedback: str = ""


class BaseHandler(Generic[P]):
    params_cls: Type[P]

    description: str = ""

    @classmethod
    def get_description(cls) -> str:
        return cls.description

    @classmethod
    def get_params_jsonschema(cls) -> dict[str, str | dict[str, str]]:
        def _jsonschema_type(field: FieldInfo) -> str:
            annotation: Any = field.annotation
            if hasattr(annotation, "__args__"):
                name = annotation.__args__[0].__name__.lower()
            else:
                name = annotation.__name__.lower()

            name: str
            types_map = {
                "str": "string",
                "float": "number",
                "int": "number",
                "decimal": "number",
                "bool": "boolean",
                "dict": "object",
            }

            return types_map.get(name, "object")

        parameters = {
            "type": "object",
            "properties": {
                name: {"type": _jsonschema_type(field)}
                for name, field in cls.params_cls.model_fields.items()
                if field.annotation
            },
        }

        return parameters

    def validate_params(self, params: dict[str, Any]) -> P:
        return self.params_cls(**params)

    def validate_output(self, output: BaseOutput) -> BaseOutput:
        return output

    def do_action(self, params: P | None) -> BaseOutput:
        raise NotImplementedError()

    def __call__(self, params: dict[str, Any] | None) -> BaseOutput:
        params_validated: P | None = None
        if params:
            params_validated = self.validate_params(params)

        output = self.do_action(params_validated)

        output = self.validate_output(output)

        return output
