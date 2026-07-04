"""Plugin registry for DocuCore."""

from docucore.plugins.base import BasePlugin
from docucore.plugins.docker import DockerPlugin
from docucore.plugins.dotnet import DotnetPlugin
from docucore.plugins.generic import GenericPlugin
from docucore.plugins.node import NodePlugin
from docucore.plugins.python import PythonPlugin

PLUGIN_REGISTRY: dict[str, BasePlugin] = {
    "generic": GenericPlugin(),
    "python": PythonPlugin(),
    "node": NodePlugin(),
    "dotnet": DotnetPlugin(),
    "docker": DockerPlugin(),
}


def get_plugin(name: str) -> BasePlugin | None:
    return PLUGIN_REGISTRY.get(name)


def get_plugins(names: list[str]) -> list[BasePlugin]:
    return [plugin for name in names if (plugin := get_plugin(name)) is not None]


__all__ = ["BasePlugin", "PLUGIN_REGISTRY", "get_plugin", "get_plugins"]
