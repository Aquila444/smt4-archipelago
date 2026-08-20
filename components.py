from worlds.LauncherComponents import Component, Type, components, launch, SuffixIdentifier
from .config import GAME_NAME

client_name = "Shin Megami Tensei 4 Client"


def run_client(*args: str) -> None:
    from .client.launch import launch_smt4_client

    launch(launch_smt4_client, name=client_name, args=args)


components.append(
    Component(
        client_name,
        func=run_client,
        game_name=GAME_NAME,
        component_type=Type.CLIENT,
        supports_uri=False,
        file_identifier=SuffixIdentifier(".apsmt4")
    )
)
